import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from '@nestjs/common';
import { PrismaService } from '../database/prisma.service';
import { LocationService } from '../location/location.service';
import { HospitalStatus, Prisma } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class HospitalsService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly locationService: LocationService,
  ) {}

  async findAll(query: {
    districtId?: string;
    stateId?: string;
    status?: HospitalStatus;
    emergencyOnly?: boolean;
    page?: number;
    limit?: number;
  }) {
    const {
      districtId,
      stateId,
      status,
      emergencyOnly,
      page = 1,
      limit = 20,
    } = query;
    const skip = (page - 1) * limit;

    const where: Prisma.HospitalWhereInput = {
      deletedAt: null,
      ...(districtId && { districtId }),
      ...(stateId && { stateId }),
      ...(status && { status }),
      ...(emergencyOnly && { hasEmergencyDepartment: true }),
    };

    const [hospitals, total] = await Promise.all([
      this.prisma.hospital.findMany({
        where,
        skip,
        take: limit,
        include: {
          city: true,
          district: true,
          departments: {
            where: { deletedAt: null, status: 'ACTIVE' },
            select: { name: true, code: true },
          },
        },
        orderBy: { name: 'asc' },
      }),
      this.prisma.hospital.count({ where }),
    ]);

    return {
      hospitals,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit),
    };
  }

  async findOne(id: string) {
    const hospital = await this.prisma.hospital.findUnique({
      where: { id },
      include: {
        city: true,
        district: true,
        departments: { where: { deletedAt: null } },
        beds: {
          where: { deletedAt: null },
          select: { bedType: true, status: true },
        },
        hospitalResources: { where: { deletedAt: null } },
      },
    });
    if (!hospital) throw new NotFoundException(`Hospital ${id} not found`);
    return hospital;
  }

  async findNearby(params: {
    lat: number;
    lon: number;
    radiusKm?: number;
    department?: string;
    urgency?: string;
    emergencyRequired?: boolean;
    limit?: number;
  }) {
    return this.locationService.findNearbyHospitals(params);
  }

  async getAvailabilitySummary(hospitalId: string) {
    const [beds, resources, activeSlots] = await Promise.all([
      this.prisma.bed.groupBy({
        by: ['bedType', 'status'],
        where: { hospitalId, deletedAt: null },
        _count: true,
      }),
      this.prisma.hospitalResource.groupBy({
        by: ['resourceType', 'status'],
        where: { hospitalId, deletedAt: null },
        _count: true,
        _sum: { availableCount: true },
      }),
      this.prisma.oPDSlot.count({
        where: {
          hospitalId,
          status: { in: ['OPEN', 'NEAR_FULL'] },
          date: { gte: new Date() },
        },
      }),
    ]);

    return { beds, resources, activeOpdSlots: activeSlots };
  }

  async getDepartments(hospitalId: string) {
    return this.prisma.department.findMany({
      where: { hospitalId, deletedAt: null },
      orderBy: { name: 'asc' },
    });
  }
}
