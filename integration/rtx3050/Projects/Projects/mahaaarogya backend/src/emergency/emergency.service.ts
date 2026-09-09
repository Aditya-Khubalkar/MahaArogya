import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../database/prisma.service';
import { AuditService } from '../audit/audit.service';
import { NotificationsService } from '../notifications/notifications.service';
import { RealtimeGateway } from '../realtime/realtime.gateway';
import { HospitalResourcesService } from '../hospital-resources/hospital-resources.service';
import { LocationService } from '../location/location.service';
import { EmergencyCaseStatus, TriageCategory, Prisma } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';

export interface CreateEmergencyDto {
  patientId: string;
  triageId?: string;
  symptoms?: string[];
  patientLatitude?: number;
  patientLongitude?: number;
  requiredResources?: string[]; // ICU_BED, OXYGEN etc.
}

@Injectable()
export class EmergencyService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly audit: AuditService,
    private readonly notifications: NotificationsService,
    private readonly realtime: RealtimeGateway,
    private readonly resourcesService: HospitalResourcesService,
    private readonly locationService: LocationService,
  ) {}

  private async resolvePatientId(userIdOrPatientId: string): Promise<string> {
    const profile = await this.prisma.patientProfile.findFirst({
      where: { OR: [{ id: userIdOrPatientId }, { userId: userIdOrPatientId }] },
    });
    return profile ? profile.id : userIdOrPatientId;
  }

  async createEmergencyCase(
    dto: CreateEmergencyDto,
    actorId: string,
    actorRole: string,
  ) {
    const resolvedPatientId = await this.resolvePatientId(dto.patientId);
    const caseCode = `EMR-${Date.now()}-${Math.random().toString(36).substr(2, 4).toUpperCase()}`;

    // Find suitable hospitals
    let nearbyHospitals: Awaited<
      ReturnType<LocationService['findNearbyHospitals']>
    > = [];
    if (dto.patientLatitude && dto.patientLongitude) {
      nearbyHospitals = await this.locationService.findNearbyHospitals({
        lat: dto.patientLatitude,
        lon: dto.patientLongitude,
        radiusKm: 50,
        urgency: 'EMERGENCY',
        emergencyRequired: true,
        limit: 5,
      });
    }

    const emergencyCase = await this.prisma.$transaction(async (tx) => {
      const ec = await tx.emergencyCase.create({
        data: {
          id: uuidv4(),
          caseCode,
          patientId: resolvedPatientId,
          triageId: dto.triageId || null,
          status: 'ACTIVE',
          symptoms: dto.symptoms ? { symptoms: dto.symptoms } : undefined,
          patientLatitude: dto.patientLatitude || null,
          patientLongitude: dto.patientLongitude || null,
        },
      });

      // Create routing recommendations
      for (const hospital of nearbyHospitals.slice(0, 3)) {
        await tx.emergencyRouting.create({
          data: {
            id: uuidv4(),
            emergencyCaseId: ec.id,
            hospitalId: hospital.hospital.id,
            distanceKm: hospital.distanceKm,
            estimatedMinutes: hospital.estimatedDrivingMinutes,
            routingScore: hospital.recommendationScore,
            reasons: hospital.reasons,
            isSelected: false,
          },
        });
      }

      return ec;
    });

    // Audit
    await this.audit.log({
      actorId,
      actorRole,
      action: 'EMERGENCY_CREATED',
      entity: 'EmergencyCase',
      entityId: emergencyCase.id,
      newValue: { caseCode, patientId: dto.patientId },
    });

    // Notify hospitals
    for (const hospital of nearbyHospitals.slice(0, 3)) {
      this.realtime.emitToHospital(
        hospital.hospital.id,
        'hospital.emergency.created',
        {
          caseId: emergencyCase.id,
          caseCode,
          distanceKm: hospital.distanceKm,
          estimatedMinutes: hospital.estimatedDrivingMinutes,
          reasons: hospital.reasons,
        },
      );

      await this.notifications.notifyHospitalStaff(
        hospital.hospital.id,
        'EMERGENCY_ALERT',
        '🚨 Emergency Case Alert',
        `Emergency case ${caseCode} within ${hospital.distanceKm.toFixed(1)} km. ${hospital.reasons.join(', ')}`,
        { caseId: emergencyCase.id, caseCode },
      );
    }

    return {
      emergencyCase: await this.prisma.emergencyCase.findUnique({
        where: { id: emergencyCase.id },
        include: { routings: { include: { hospital: true } } },
      }),
      nearbyHospitals,
    };
  }

  async selectHospital(
    caseId: string,
    hospitalId: string,
    actorId: string,
    actorRole: string,
  ) {
    const ec = await this.prisma.emergencyCase.findUnique({
      where: { id: caseId },
    });
    if (!ec) throw new NotFoundException('Emergency case not found');

    await this.prisma.$transaction(async (tx) => {
      await tx.emergencyRouting.updateMany({
        where: { emergencyCaseId: caseId },
        data: { isSelected: false },
      });
      await tx.emergencyRouting.updateMany({
        where: { emergencyCaseId: caseId, hospitalId },
        data: { isSelected: true },
      });
      await tx.emergencyCase.update({
        where: { id: caseId },
        data: { hospitalId, status: 'RESOURCE_HELD' },
      });
    });

    // Create resource holds for ICU if available
    const icuBed = await this.prisma.bed.findFirst({
      where: {
        hospitalId,
        bedType: 'ICU_BED',
        status: 'AVAILABLE',
        deletedAt: null,
      },
    });
    if (icuBed) {
      await this.resourcesService.createHold(
        { emergencyCaseId: caseId, bedId: icuBed.id },
        actorId,
        actorRole,
      );
    }

    await this.audit.log({
      actorId,
      actorRole,
      action: 'EMERGENCY_HOSPITAL_SELECTED',
      entity: 'EmergencyCase',
      entityId: caseId,
      newValue: { hospitalId },
    });

    this.realtime.emitToHospital(hospitalId, 'hospital.emergency.updated', {
      caseId,
      status: 'RESOURCE_HELD',
      hospitalId,
    });

    return this.prisma.emergencyCase.findUnique({
      where: { id: caseId },
      include: { routings: { include: { hospital: true } }, triage: true },
    });
  }

  async resolveCase(caseId: string, actorId: string, actorRole: string) {
    await this.prisma.emergencyCase.update({
      where: { id: caseId },
      data: { status: 'RESOLVED', resolvedAt: new Date() },
    });

    await this.audit.log({
      actorId,
      actorRole,
      action: 'EMERGENCY_RESOLVED',
      entity: 'EmergencyCase',
      entityId: caseId,
    });

    return { success: true };
  }

  async findByPatient(patientId: string) {
    const resolvedPatientId = await this.resolvePatientId(patientId);
    return this.prisma.emergencyCase.findMany({
      where: { patientId: resolvedPatientId },
      include: { routings: { include: { hospital: true } }, triage: true },
      orderBy: { createdAt: 'desc' },
    });
  }

  async findAll(
    hospitalId?: string,
    districtId?: string,
    page = 1,
    limit = 20,
  ) {
    const skip = (page - 1) * limit;
    const where = {
      ...(hospitalId && { hospitalId }),
      status: { not: 'RESOLVED' as EmergencyCaseStatus },
    };

    return this.prisma.emergencyCase.findMany({
      where,
      skip,
      take: limit,
      include: { hospital: true, triage: true },
      orderBy: { createdAt: 'desc' },
    });
  }
}
