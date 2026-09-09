import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../database/prisma.service';
import { AuditService } from '../audit/audit.service';
import { NotificationsService } from '../notifications/notifications.service';
import { RealtimeGateway } from '../realtime/realtime.gateway';
import { CCTVOccupancyStatus, BedStatus } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';

export interface CCTVOccupancyEventDto {
  deviceId?: string;
  deviceCode: string;
  zoneId?: string;
  bedId?: string; // bedCode
  occupancy: CCTVOccupancyStatus;
  confidence: number;
  timestamp?: string;
  isMock?: boolean;
}

@Injectable()
export class CCTVService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly audit: AuditService,
    private readonly notifications: NotificationsService,
    private readonly realtime: RealtimeGateway,
  ) {}

  async ingestOccupancyEvent(dto: CCTVOccupancyEventDto) {
    // Resolve device
    const device = await this.prisma.cCTVDevice.findFirst({
      where: { deviceCode: dto.deviceCode, isActive: true },
    });
    if (!device)
      throw new NotFoundException(`CCTV device ${dto.deviceCode} not found`);

    const event = await this.prisma.cCTVOccupancyEvent.create({
      data: {
        id: uuidv4(),
        deviceId: device.id,
        zoneId: dto.zoneId || null,
        bedId: dto.bedId || null, // stored as bedCode
        occupancy: dto.occupancy,
        confidence: dto.confidence,
        isProcessed: false,
        isMock: dto.isMock ?? false,
      },
    });

    // Only process if confidence is above threshold
    if (dto.confidence >= 0.7 && dto.bedId) {
      await this.processEvent(
        event.id,
        dto.bedId,
        dto.occupancy,
        dto.confidence,
        device.hospitalId,
      );
    }

    return event;
  }

  private async processEvent(
    eventId: string,
    bedCode: string,
    cctvStatus: CCTVOccupancyStatus,
    confidence: number,
    hospitalId: string,
  ) {
    const bed = await this.prisma.bed.findFirst({
      where: { bedCode, hospitalId },
    });
    if (!bed) return;

    // Map CCTV status to authoritative bed status
    const cctvToBed: Record<CCTVOccupancyStatus, BedStatus> = {
      AVAILABLE: 'AVAILABLE',
      OCCUPIED: 'OCCUPIED',
      UNKNOWN: 'UNKNOWN',
      BLOCKED: 'MAINTENANCE',
    };
    const predictedBedStatus = cctvToBed[cctvStatus];

    // Check for discrepancy
    if (bed.status !== predictedBedStatus && bed.status !== 'HELD') {
      // Create discrepancy record
      const discrepancy = await this.prisma.cCTVDiscrepancy.create({
        data: {
          id: uuidv4(),
          eventId,
          bedCode,
          cctvStatus,
          authoritativeStatus: bed.status,
          confidence,
          isResolved: false,
        },
      });

      // Emit realtime alert
      this.realtime.emitToHospital(hospitalId, 'hospital.cctv.discrepancy', {
        discrepancyId: discrepancy.id,
        bedCode,
        cctvStatus,
        authoritativeStatus: bed.status,
        confidence,
      });

      // Notify hospital staff
      await this.notifications.notifyHospitalStaff(
        hospitalId,
        'CCTV_DISCREPANCY',
        '📷 CCTV Bed Status Discrepancy',
        `CCTV shows ${bedCode} as ${cctvStatus} but system shows ${bed.status}. Please verify.`,
        { discrepancyId: discrepancy.id, bedCode },
      );

      await this.audit.log({
        action: 'CCTV_DISCREPANCY_CREATED',
        entity: 'CCTVDiscrepancy',
        entityId: discrepancy.id,
        newValue: {
          bedCode,
          cctvStatus,
          authoritativeStatus: bed.status,
          confidence,
        },
      });
    }

    await this.prisma.cCTVOccupancyEvent.update({
      where: { id: eventId },
      data: { isProcessed: true },
    });
  }

  async resolveDiscrepancy(
    discrepancyId: string,
    resolution:
      'CONFIRMED_CCTV' | 'CONFIRMED_AUTHORITATIVE' | 'MANUAL_OVERRIDE',
    newStatus: BedStatus | null,
    resolvedBy: string,
    actorId: string,
    actorRole: string,
    notes?: string,
  ) {
    const discrepancy = await this.prisma.cCTVDiscrepancy.findUnique({
      where: { id: discrepancyId },
    });
    if (!discrepancy) throw new NotFoundException('Discrepancy not found');

    // Update authoritative status if CCTV is confirmed correct
    if (resolution === 'CONFIRMED_CCTV' || resolution === 'MANUAL_OVERRIDE') {
      const targetStatus =
        newStatus ||
        (discrepancy.cctvStatus === 'AVAILABLE' ? 'AVAILABLE' : 'OCCUPIED');
      const bed = await this.prisma.bed.findFirst({
        where: { bedCode: discrepancy.bedCode },
      });
      if (bed) {
        const oldStatus = bed.status;
        await this.prisma.bed.update({
          where: { id: bed.id },
          data: { status: targetStatus },
        });
        await this.prisma.bedStatusHistory.create({
          data: {
            id: uuidv4(),
            bedId: bed.id,
            oldStatus,
            newStatus: targetStatus,
            changedBy: resolvedBy,
            reason: `CCTV discrepancy resolved: ${resolution}`,
            source: 'CCTV',
          },
        });
        this.realtime.emitToHospital(bed.hospitalId, 'hospital.bed.updated', {
          bedId: bed.id,
          bedCode: bed.bedCode,
          oldStatus,
          newStatus: targetStatus,
          source: 'CCTV_RESOLUTION',
        });
      }
    }

    await this.prisma.cCTVDiscrepancy.update({
      where: { id: discrepancyId },
      data: {
        isResolved: true,
        resolvedBy,
        resolvedAt: new Date(),
        resolution,
        notes,
      },
    });

    await this.audit.log({
      actorId,
      actorRole,
      action: 'CCTV_DISCREPANCY_RESOLVED',
      entity: 'CCTVDiscrepancy',
      entityId: discrepancyId,
      newValue: { resolution, notes },
    });

    return { success: true, resolution };
  }

  async getUnresolvedDiscrepancies(hospitalId: string) {
    const devices = await this.prisma.cCTVDevice.findMany({
      where: { hospitalId },
      select: { id: true },
    });
    const deviceIds = devices.map((d) => d.id);

    return this.prisma.cCTVDiscrepancy.findMany({
      where: {
        isResolved: false,
        event: { deviceId: { in: deviceIds } },
      },
      include: { event: { include: { device: true } } },
      orderBy: { createdAt: 'desc' },
    });
  }

  async getDevices(hospitalId: string) {
    return this.prisma.cCTVDevice.findMany({
      where: { hospitalId },
      include: {
        zones: { include: { bedMappings: { include: { bed: true } } } },
      },
    });
  }

  // Mock CCTV event generator for demos
  async generateMockCCTVEvent(hospitalId: string) {
    const device = await this.prisma.cCTVDevice.findFirst({
      where: { hospitalId, isMock: true },
      include: {
        zones: { include: { bedMappings: { include: { bed: true } } } },
      },
    });
    if (!device) return { message: 'No mock CCTV device found' };

    const beds = device.zones.flatMap((z) => z.bedMappings.map((bm) => bm.bed));
    if (beds.length === 0) return { message: 'No beds mapped to CCTV device' };

    const randomBed = beds[Math.floor(Math.random() * beds.length)];
    const statuses: CCTVOccupancyStatus[] = [
      'AVAILABLE',
      'OCCUPIED',
      'UNKNOWN',
    ];
    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
    const confidence = 0.7 + Math.random() * 0.3;

    return this.ingestOccupancyEvent({
      deviceCode: device.deviceCode,
      zoneId: device.zones[0]?.id,
      bedId: randomBed.bedCode,
      occupancy: randomStatus,
      confidence,
      isMock: true,
    });
  }
}
