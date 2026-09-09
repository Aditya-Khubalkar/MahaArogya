import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../database/prisma.service';
import {
  haversineDistance,
  estimateDrivingMinutes,
} from '../common/utils/haversine.util';
import { HospitalStatus, Prisma } from '@prisma/client';
import axios from 'axios';
import NodeCache from 'node-cache';
import { v4 as uuidv4 } from 'uuid';

export interface GeocodingResult {
  name: string;
  displayName: string;
  latitude: number;
  longitude: number;
  type: string;
  importance?: number;
}

export interface NearbyHospitalResult {
  hospital: {
    id: string;
    name: string;
    hospitalCode: string;
    type: string;
    hasEmergencyDepartment: boolean;
    latitude: number | null;
    longitude: number | null;
    address: string | null;
    emergencyContact: string | null;
  };
  distanceKm: number;
  estimatedDrivingMinutes: number;
  availableBeds: number;
  availableICUBeds: number;
  availableOxygen: number;
  hasEmergencyCapability: boolean;
  currentOpdLoad: string;
  recommendationScore: number;
  reasons: string[];
}

@Injectable()
export class LocationService {
  private readonly logger = new Logger(LocationService.name);
  private readonly geocodeCache = new NodeCache({ stdTTL: 3600 }); // 1 hour
  private nominatimLastCall = 0;
  private readonly NOMINATIM_DELAY_MS = 1100; // Respect 1 req/sec

  constructor(
    private readonly prisma: PrismaService,
    private readonly config: ConfigService,
  ) {}

  async geocode(query: string): Promise<GeocodingResult[]> {
    const cacheKey = `geocode:${query.toLowerCase().trim()}`;
    const cached = this.geocodeCache.get<GeocodingResult[]>(cacheKey);
    if (cached) return cached;

    // Rate limit Nominatim
    await this.respectNominatimRateLimit();

    try {
      const nominatimUrl = this.config.get('app.nominatimUrl');
      const userAgent = this.config.get('app.nominatimUserAgent');

      const response = await axios.get(`${nominatimUrl}/search`, {
        params: {
          q: query,
          format: 'json',
          limit: 10,
          addressdetails: 1,
          countrycodes: 'in', // India only
        },
        headers: { 'User-Agent': userAgent },
        timeout: 8000,
      });

      const results: GeocodingResult[] = (
        response.data as Array<{
          display_name: string;
          name?: string;
          lat: string;
          lon: string;
          type?: string;
          importance?: number;
        }>
      ).map((r) => ({
        name: r.name || r.display_name.split(',')[0],
        displayName: r.display_name,
        latitude: parseFloat(r.lat),
        longitude: parseFloat(r.lon),
        type: r.type || 'location',
        importance: r.importance,
      }));

      this.geocodeCache.set(cacheKey, results);

      // Persist to DB cache
      await this.persistGeocodingCache(query, results);

      return results;
    } catch (err) {
      this.logger.warn(`Geocoding failed for "${query}": ${err}`);
      // Try DB cache as fallback
      return this.getFromDbCache(query);
    }
  }

  async reverseGeocode(lat: number, lon: number): Promise<string> {
    const cacheKey = `reverse:${lat.toFixed(4)},${lon.toFixed(4)}`;
    const cached = this.geocodeCache.get<string>(cacheKey);
    if (cached) return cached;

    await this.respectNominatimRateLimit();

    try {
      const nominatimUrl = this.config.get('app.nominatimUrl');
      const userAgent = this.config.get('app.nominatimUserAgent');

      const response = await axios.get(`${nominatimUrl}/reverse`, {
        params: { lat, lon, format: 'json' },
        headers: { 'User-Agent': userAgent },
        timeout: 8000,
      });

      const displayName =
        (response.data as { display_name: string }).display_name ||
        `${lat}, ${lon}`;
      this.geocodeCache.set(cacheKey, displayName);
      return displayName;
    } catch {
      return `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
    }
  }

  async findNearbyHospitals(params: {
    lat: number;
    lon: number;
    radiusKm?: number;
    department?: string;
    urgency?: string;
    emergencyRequired?: boolean;
    limit?: number;
  }): Promise<NearbyHospitalResult[]> {
    const {
      lat,
      lon,
      radiusKm = 50,
      department,
      urgency = 'ROUTINE',
      emergencyRequired = false,
      limit = 10,
    } = params;

    // Get all active hospitals with coordinates
    const hospitals = await this.prisma.hospital.findMany({
      where: {
        status: HospitalStatus.ACTIVE,
        latitude: { not: null },
        longitude: { not: null },
        deletedAt: null,
        ...(emergencyRequired && { hasEmergencyDepartment: true }),
      },
      include: {
        beds: {
          where: { deletedAt: null },
          select: { bedType: true, status: true },
        },
        hospitalResources: {
          where: { deletedAt: null },
          select: { resourceType: true, status: true, availableCount: true },
        },
        departments: {
          where: { deletedAt: null, status: 'ACTIVE' },
          select: { name: true, code: true },
        },
      },
    });

    const results: NearbyHospitalResult[] = [];

    for (const hospital of hospitals) {
      if (!hospital.latitude || !hospital.longitude) continue;

      const distanceKm = haversineDistance(
        lat,
        lon,
        hospital.latitude,
        hospital.longitude,
      );
      if (distanceKm > radiusKm) continue;

      // Count available resources
      const availableBeds = hospital.beds.filter(
        (b) => b.bedType === 'GENERAL_BED' && b.status === 'AVAILABLE',
      ).length;
      const availableICU = hospital.beds.filter(
        (b) => b.bedType === 'ICU_BED' && b.status === 'AVAILABLE',
      ).length;
      const availableOxygen = hospital.hospitalResources
        .filter(
          (r) =>
            r.resourceType.startsWith('OXYGEN') && r.status === 'AVAILABLE',
        )
        .reduce((sum, r) => sum + r.availableCount, 0);

      const estimatedMinutes = estimateDrivingMinutes(distanceKm);

      const reasons: string[] = [];
      if (hospital.hasEmergencyDepartment)
        reasons.push('Emergency department available');
      if (availableICU > 0)
        reasons.push(`${availableICU} ICU bed(s) available`);
      if (availableOxygen > 0) reasons.push('Oxygen available');
      if (availableBeds > 0)
        reasons.push(`${availableBeds} general bed(s) available`);
      reasons.push(`${distanceKm.toFixed(1)} km away`);
      reasons.push(`Est. ${estimatedMinutes} min travel`);

      // Scoring algorithm
      let score = 1000 - distanceKm * 2; // Closer = higher base score
      if (urgency === 'EMERGENCY') {
        if (hospital.hasEmergencyDepartment) score += 500;
        if (availableICU > 0) score += 300;
        if (availableOxygen > 0) score += 200;
        score -= estimatedMinutes * 3; // Penalize travel time more for emergencies
      } else {
        if (availableBeds > 0) score += 100;
      }

      results.push({
        hospital: {
          id: hospital.id,
          name: hospital.name,
          hospitalCode: hospital.hospitalCode,
          type: hospital.type,
          hasEmergencyDepartment: hospital.hasEmergencyDepartment,
          latitude: hospital.latitude,
          longitude: hospital.longitude,
          address: hospital.address,
          emergencyContact: hospital.emergencyContact,
        },
        distanceKm: parseFloat(distanceKm.toFixed(2)),
        estimatedDrivingMinutes: estimatedMinutes,
        availableBeds,
        availableICUBeds: availableICU,
        availableOxygen,
        hasEmergencyCapability: hospital.hasEmergencyDepartment,
        currentOpdLoad:
          availableBeds > 10 ? 'LOW' : availableBeds > 3 ? 'MEDIUM' : 'HIGH',
        recommendationScore: parseFloat(score.toFixed(2)),
        reasons,
      });
    }

    // Sort by recommendation score descending
    results.sort((a, b) => b.recommendationScore - a.recommendationScore);
    return results.slice(0, limit);
  }

  async storeLocationRequest(
    patientId: string | undefined,
    data: {
      latitude?: number;
      longitude?: number;
      accuracy?: number;
      address?: string;
      isManual?: boolean;
    },
  ) {
    return this.prisma.locationRequest.create({
      data: {
        id: uuidv4(),
        patientId: patientId || null,
        latitude: data.latitude || null,
        longitude: data.longitude || null,
        accuracy: data.accuracy || null,
        address: data.address || null,
        isManual: data.isManual || false,
      },
    });
  }

  private async respectNominatimRateLimit() {
    const now = Date.now();
    const elapsed = now - this.nominatimLastCall;
    if (elapsed < this.NOMINATIM_DELAY_MS) {
      await new Promise((resolve) =>
        setTimeout(resolve, this.NOMINATIM_DELAY_MS - elapsed),
      );
    }
    this.nominatimLastCall = Date.now();
  }

  private async persistGeocodingCache(
    query: string,
    results: GeocodingResult[],
  ) {
    try {
      await this.prisma.geocodingCache.upsert({
        where: { query },
        create: {
          id: uuidv4(),
          query,
          result: results as unknown as Prisma.InputJsonValue,
          provider: 'nominatim',
          expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
        },
        update: {
          result: results as unknown as Prisma.InputJsonValue,
          expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        },
      });
    } catch {
      // Non-critical
    }
  }

  private async getFromDbCache(query: string): Promise<GeocodingResult[]> {
    try {
      const cached = await this.prisma.geocodingCache.findUnique({
        where: { query },
      });
      if (cached && cached.expiresAt > new Date()) {
        return cached.result as unknown as GeocodingResult[];
      }
    } catch {
      // ignore
    }
    return [];
  }
}
