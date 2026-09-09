import { Injectable } from '@nestjs/common';
import { PrismaService } from '../database/prisma.service';
import { RealtimeGateway } from '../realtime/realtime.gateway';
import { Prisma } from '@prisma/client';
import { NotificationType, NotificationChannel } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';

export interface CreateNotificationDto {
  userId: string;
  type: NotificationType;
  title: string;
  body: string;
  data?: Record<string, unknown>;
  channel?: NotificationChannel;
}

@Injectable()
export class NotificationsService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly realtime: RealtimeGateway,
  ) {}

  async create(dto: CreateNotificationDto) {
    const notification = await this.prisma.notification.create({
      data: {
        id: uuidv4(),
        userId: dto.userId,
        type: dto.type,
        title: dto.title,
        body: dto.body,
        data: dto.data
          ? (dto.data as unknown as Prisma.InputJsonValue)
          : undefined,

        channel: dto.channel || 'IN_APP',
        status: 'PENDING',
      },
    });

    // Always push via WebSocket
    this.realtime.emitToUser(dto.userId, 'notification.created', {
      id: notification.id,
      type: notification.type,
      title: notification.title,
      body: notification.body,
      data: notification.data,
      createdAt: notification.createdAt,
    });

    // Mark as sent
    await this.prisma.notification.update({
      where: { id: notification.id },
      data: { status: 'SENT' },
    });

    return notification;
  }

  async findForUser(
    userId: string,
    query: { unreadOnly?: boolean; page?: number; limit?: number },
  ) {
    const { unreadOnly = false, page = 1, limit = 20 } = query;
    const skip = (page - 1) * limit;

    const where = {
      userId,
      ...(unreadOnly && { readAt: null }),
    };

    const [notifications, total] = await Promise.all([
      this.prisma.notification.findMany({
        where,
        skip,
        take: limit,
        orderBy: { createdAt: 'desc' },
      }),
      this.prisma.notification.count({ where }),
    ]);

    return { notifications, total, page, limit };
  }

  async markRead(id: string, userId: string) {
    return this.prisma.notification.updateMany({
      where: { id, userId },
      data: { readAt: new Date(), status: 'READ' },
    });
  }

  async markAllRead(userId: string) {
    return this.prisma.notification.updateMany({
      where: { userId, readAt: null },
      data: { readAt: new Date(), status: 'READ' },
    });
  }

  async notifyHospitalStaff(
    hospitalId: string,
    type: NotificationType,
    title: string,
    body: string,
    data?: Record<string, unknown>,
  ) {
    // Get all active hospital staff
    const staff = await this.prisma.user.findMany({
      where: {
        hospitalId,
        isActive: true,
        role: {
          in: [
            'HOSPITAL_ADMIN',
            'HOSPITAL_HEAD',
            'DOCTOR',
            'NURSE',
            'RECEPTION',
          ],
        },
      },
      select: { id: true },
    });

    for (const member of staff) {
      await this.create({ userId: member.id, type, title, body, data });
    }
  }
}
