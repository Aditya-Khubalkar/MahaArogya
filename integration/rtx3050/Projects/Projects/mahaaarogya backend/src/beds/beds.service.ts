import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from '@nestjs/common';
import { PrismaService } from '../database/prisma.service';
import { AuditService } from '../audit/audit.service';
import { NotificationsService } from '../notifications/notifications.service';
import { RealtimeGateway } from '../realtime/realtime.gateway';
import { BedStatus, BedType, Prisma } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';

export interface UpdateBedStatusDto {
  status: BedStatus;
  reason?: string;
  source?: string;
}

@Injectable()
export class BedsService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly audit: AuditService,
    private readonly notifications: NotificationsService,
    private readonly realtime: RealtimeGateway,
  ) {}

  async findAll(
    hospitalId: string,
    query: {
      bedType?: BedType;
      status?: BedStatus;
      ward?: string;
      page?: number;
      limit?: number;
    },
  ) {
    const { bedType, status, ward, page = 1, limit = 50 } = query;
    const skip = (page - 1) * limit;

    const where: Prisma.BedWhereInput = {
      hospitalId,
      deletedAt: null,
      ...(bedType && { bedType }),
      ...(status && { status }),
      ...(ward && { wardName: { contains: ward, mode: 'insensitive' } }),
    };

    const [beds, total] = await Promise.all([
      this.prisma.bed.findMany({
        where,
        skip,
        take: limit,
        include: { statusHistory: { take: 1, orderBy: { createdAt: 'desc' } } },
        orderBy: { bedCode: 'asc' },
      }),
      this.prisma.bed.count({ where }),
    ]);

    return { beds, total, page, limit, totalPages: Math.ceil(total / limit) };
  }

  async findOne(id: string) {
    const bed = await this.prisma.bed.findUnique({
      where: { id },
      include: {
        statusHistory: { take: 10, orderBy: { createdAt: 'desc' } },
        cameraMappings: { include: { zone: true } },
      },
    });
    if (!bed) throw new NotFoundException(`Bed ${id} not found`);
    return bed;
  }

  async updateStatus(
    id: string,
    dto: UpdateBedStatusDto,
    actorId: string,
    actorRole: string,
  ) {
    const bed = await this.prisma.bed.findUnique({ where: { id } });
    if (!bed) throw new NotFoundException(`Bed ${id} not found`);

    const oldStatus = bed.status;
    if (oldStatus === dto.status) return bed;

    const updated = await this.prisma.$transaction(async (tx) => {
      const updatedBed = await tx.bed.update({
        where: { id },
        data: { status: dto.status, updatedAt: new Date() },
      });

      await tx.bedStatusHistory.create({
        data: {
          id: uuidv4(),
          bedId: id,
          oldStatus,
          newStatus: dto.status,
          changedBy: actorId,
          reason: dto.reason,
          source: dto.source || 'MANUAL',
        },
      });

      return updatedBed;
    });

    // Audit
    await this.audit.log({
      actorId,
      actorRole,
      action: 'BED_STATUS_CHANGED',
      entity: 'Bed',
      entityId: id,
      oldValue: { status: oldStatus },
      newValue: { status: dto.status },
      reason: dto.reason,
    });

    // Broadcast realtime event
    this.realtime.emitToHospital(bed.hospitalId, 'hospital.bed.updated', {
      bedId: id,
      bedCode: bed.bedCode,
      oldStatus,
      newStatus: dto.status,
      hospitalId: bed.hospitalId,
    });

    return updated;
  }

  async getAvailabilitySummary(hospitalId: string) {
    const beds = await this.prisma.bed.groupBy({
      by: ['bedType', 'status'],
      where: { hospitalId, deletedAt: null },
      _count: true,
    });

    const summary: Record<string, Record<string, number>> = {};
    for (const b of beds) {
      if (!summary[b.bedType]) summary[b.bedType] = {};
      summary[b.bedType][b.status] = b._count;
    }
    return summary;
  }
}
