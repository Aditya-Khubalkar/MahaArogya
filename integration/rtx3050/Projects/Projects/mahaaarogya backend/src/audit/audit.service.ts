import { Injectable } from '@nestjs/common';
import { PrismaService } from '../database/prisma.service';
import { Prisma } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';

export interface CreateAuditLogDto {
  actorId?: string;
  actorRole?: string;
  action: string;
  entity?: string;
  entityId?: string;
  oldValue?: Record<string, unknown>;
  newValue?: Record<string, unknown>;
  reason?: string;
  requestId?: string;
  ipAddress?: string;
}

@Injectable()
export class AuditService {
  constructor(private readonly prisma: PrismaService) {}

  async log(dto: CreateAuditLogDto): Promise<void> {
    try {
      await this.prisma.auditLog.create({
        data: {
          id: uuidv4(),
          actorId: dto.actorId || null,
          actorRole: dto.actorRole || null,
          action: dto.action,
          entity: dto.entity || 'System',
          entityId: dto.entityId || null,
          oldValue: dto.oldValue
            ? (dto.oldValue as unknown as Prisma.InputJsonValue)
            : undefined,
          newValue: dto.newValue
            ? (dto.newValue as unknown as Prisma.InputJsonValue)
            : undefined,

          reason: dto.reason || null,
          requestId: dto.requestId || null,
          ipAddress: dto.ipAddress || null,
        },
      });
    } catch (err) {
      // Never let audit logging crash the main operation
      console.error('AuditLog failed:', err);
    }
  }

  async findAll(query: {
    entity?: string;
    entityId?: string;
    actorId?: string;
    action?: string;
    from?: Date;
    to?: Date;
    page?: number;
    limit?: number;
  }) {
    const {
      entity,
      entityId,
      actorId,
      action,
      from,
      to,
      page = 1,
      limit = 50,
    } = query;
    const skip = (page - 1) * limit;

    const where = {
      ...(entity && { entity }),
      ...(entityId && { entityId }),
      ...(actorId && { actorId }),
      ...(action && { action: { contains: action } }),
      ...(from || to
        ? {
            createdAt: {
              ...(from && { gte: from }),
              ...(to && { lte: to }),
            },
          }
        : {}),
    };

    const [logs, total] = await Promise.all([
      this.prisma.auditLog.findMany({
        where,
        skip,
        take: limit,
        orderBy: { createdAt: 'desc' },
        include: { actor: { select: { displayName: true, role: true } } },
      }),
      this.prisma.auditLog.count({ where }),
    ]);

    return { logs, total, page, limit };
  }
}
