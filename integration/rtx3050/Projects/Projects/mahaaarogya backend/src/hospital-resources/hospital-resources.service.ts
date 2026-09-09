import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../database/prisma.service';
import { AuditService } from '../audit/audit.service';
import { RealtimeGateway } from '../realtime/realtime.gateway';
import { ResourceStatus, ResourceType, Prisma } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';
import { ConfigService } from '@nestjs/config';

export interface CreateResourceHoldDto {
  emergencyCaseId: string;
  resourceId?: string;
  bedId?: string;
}

@Injectable()
export class HospitalResourcesService {
  private holdTimers = new Map<string, NodeJS.Timeout>();

  constructor(
    private readonly prisma: PrismaService,
    private readonly audit: AuditService,
    private readonly realtime: RealtimeGateway,
    private readonly config: ConfigService,
  ) {}

  async findByHospital(
    hospitalId: string,
    query: { resourceType?: ResourceType; status?: ResourceStatus },
  ) {
    return this.prisma.hospitalResource.findMany({
      where: {
        hospitalId,
        deletedAt: null,
        ...(query.resourceType && { resourceType: query.resourceType }),
        ...(query.status && { status: query.status }),
      },
      include: { statusHistory: { take: 3, orderBy: { createdAt: 'desc' } } },
    });
  }

  async createHold(
    dto: CreateResourceHoldDto,
    actorId: string,
    actorRole: string,
  ) {
    const expiryMinutes = this.config.get<number>(
      'app.resourceHoldExpiryMinutes',
      30,
    );
    const expiresAt = new Date(Date.now() + expiryMinutes * 60 * 1000);

    const hold = await this.prisma.$transaction(async (tx) => {
      const newHold = await tx.resourceHold.create({
        data: {
          id: uuidv4(),
          holdCode: `HOLD-${Date.now()}`,
          emergencyCaseId: dto.emergencyCaseId,
          resourceId: dto.resourceId || null,
          bedId: dto.bedId || null,
          status: 'ACTIVE',
          expiresAt,
        },
      });

      // Update resource status to HELD
      if (dto.resourceId) {
        await tx.hospitalResource.update({
          where: { id: dto.resourceId },
          data: { status: 'HELD' },
        });
      }
      if (dto.bedId) {
        await tx.bed.update({
          where: { id: dto.bedId },
          data: { status: 'HELD' },
        });
      }

      return newHold;
    });

    await this.audit.log({
      actorId,
      actorRole,
      action: 'RESOURCE_HELD',
      entity: 'ResourceHold',
      entityId: hold.id,
      newValue: { ...dto, expiresAt },
    });

    // Schedule expiration
    this.scheduleHoldExpiration(hold.id, expiryMinutes * 60 * 1000);

    this.realtime.emitToHospital(
      dto.emergencyCaseId,
      'hospital.resource.updated',
      { holdId: hold.id, status: 'ACTIVE', expiresAt },
    );

    return hold;
  }

  async confirmHold(holdId: string, actorId: string, actorRole: string) {
    const hold = await this.prisma.resourceHold.findUnique({
      where: { id: holdId },
    });
    if (!hold) throw new NotFoundException('Resource hold not found');

    // Cancel expiration timer
    const timer = this.holdTimers.get(holdId);
    if (timer) {
      clearTimeout(timer);
      this.holdTimers.delete(holdId);
    }

    const updated = await this.prisma.resourceHold.update({
      where: { id: holdId },
      data: { status: 'CONFIRMED', confirmedAt: new Date() },
    });

    await this.audit.log({
      actorId,
      actorRole,
      action: 'RESOURCE_HOLD_CONFIRMED',
      entity: 'ResourceHold',
      entityId: holdId,
    });

    return updated;
  }

  async releaseHold(
    holdId: string,
    actorId: string,
    actorRole: string,
    reason?: string,
  ) {
    const hold = await this.prisma.resourceHold.findUnique({
      where: { id: holdId },
    });
    if (!hold) throw new NotFoundException('Resource hold not found');

    const timer = this.holdTimers.get(holdId);
    if (timer) {
      clearTimeout(timer);
      this.holdTimers.delete(holdId);
    }

    await this.prisma.$transaction(async (tx) => {
      await tx.resourceHold.update({
        where: { id: holdId },
        data: { status: 'RELEASED', releasedAt: new Date(), notes: reason },
      });

      if (hold.resourceId) {
        await tx.hospitalResource.update({
          where: { id: hold.resourceId },
          data: { status: 'AVAILABLE' },
        });
      }
      if (hold.bedId) {
        await tx.bed.update({
          where: { id: hold.bedId },
          data: { status: 'AVAILABLE' },
        });
      }
    });

    await this.audit.log({
      actorId,
      actorRole,
      action: 'RESOURCE_RELEASED',
      entity: 'ResourceHold',
      entityId: holdId,
      reason,
    });
  }

  private scheduleHoldExpiration(holdId: string, delayMs: number) {
    const timer = setTimeout(async () => {
      await this.expireHold(holdId);
    }, delayMs);
    this.holdTimers.set(holdId, timer);
  }

  async expireHold(holdId: string) {
    const hold = await this.prisma.resourceHold.findUnique({
      where: { id: holdId },
    });
    if (!hold || hold.status !== 'ACTIVE') return;

    await this.prisma.$transaction(async (tx) => {
      await tx.resourceHold.update({
        where: { id: holdId },
        data: { status: 'EXPIRED', releasedAt: new Date() },
      });
      if (hold.resourceId) {
        await tx.hospitalResource.update({
          where: { id: hold.resourceId },
          data: { status: 'AVAILABLE' },
        });
      }
      if (hold.bedId) {
        await tx.bed.update({
          where: { id: hold.bedId },
          data: { status: 'AVAILABLE' },
        });
      }
    });

    await this.audit.log({
      action: 'RESOURCE_HOLD_EXPIRED',
      entity: 'ResourceHold',
      entityId: holdId,
    });

    this.holdTimers.delete(holdId);
  }

  async restoreActiveHolds() {
    // On server restart, reschedule any still-active holds
    const activeHolds = await this.prisma.resourceHold.findMany({
      where: { status: 'ACTIVE', expiresAt: { gt: new Date() } },
    });
    for (const hold of activeHolds) {
      const remaining = hold.expiresAt.getTime() - Date.now();
      if (remaining > 0) {
        this.scheduleHoldExpiration(hold.id, remaining);
      } else {
        await this.expireHold(hold.id);
      }
    }
  }
}
