import {
  Injectable,
  NotFoundException,
  BadRequestException,
  ForbiddenException,
} from '@nestjs/common';
import { PrismaService } from '../database/prisma.service';
import { AuditService } from '../audit/audit.service';
import { NotificationsService } from '../notifications/notifications.service';
import { RealtimeGateway } from '../realtime/realtime.gateway';
import { AppointmentStatus, OPDSlotStatus, Prisma } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';

export interface BookAppointmentDto {
  hospitalId: string;
  departmentId: string;
  doctorId?: string;
  slotId?: string;
  appointmentDate: Date;
  reason?: string;
}

@Injectable()
export class AppointmentsService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly audit: AuditService,
    private readonly notifications: NotificationsService,
    private readonly realtime: RealtimeGateway,
  ) {}

  private async resolvePatientId(userIdOrPatientId: string): Promise<string> {
    const profile = await this.prisma.patientProfile.findFirst({
      where: { OR: [{ id: userIdOrPatientId }, { userId: userIdOrPatientId }] },
    });
    return profile ? profile.id : userIdOrPatientId;
  }

  async bookAppointment(
    patientId: string,
    dto: BookAppointmentDto,
    actorId: string,
    actorRole: string,
  ) {
    const resolvedPatientId = await this.resolvePatientId(patientId);
    // Validate hospital exists
    const hospital = await this.prisma.hospital.findUnique({
      where: { id: dto.hospitalId },
    });
    if (!hospital) throw new NotFoundException('Hospital not found');

    // Validate slot if provided
    let slot: any = null;
    if (dto.slotId) {
      slot = await this.prisma.oPDSlot.findUnique({
        where: { id: dto.slotId },
      });
      if (!slot) throw new NotFoundException('OPD slot not found');
      if (slot.status === 'FULL')
        throw new BadRequestException('This slot is full');
      if (slot.status === 'CLOSED' || slot.status === 'CANCELLED') {
        throw new BadRequestException('This slot is not available');
      }
    }

    const appointmentCode = `APT-${Date.now()}-${Math.random().toString(36).substr(2, 4).toUpperCase()}`;

    const appointment = await this.prisma.$transaction(async (tx) => {
      const apt = await tx.appointment.create({
        data: {
          id: uuidv4(),
          appointmentCode,
          patientId: resolvedPatientId,
          hospitalId: dto.hospitalId,
          departmentId: dto.departmentId,
          doctorId: dto.doctorId || null,
          slotId: dto.slotId || null,
          status: 'BOOKED',
          appointmentDate: dto.appointmentDate,
          reason: dto.reason || null,
          source: 'ONLINE',
        },
      });

      // Update slot count if slot selected
      if (dto.slotId && slot) {
        const newCount = slot.bookedCount + 1;
        const newStatus: OPDSlotStatus =
          newCount >= slot.capacity
            ? 'FULL'
            : newCount >= slot.capacity * 0.8
              ? 'NEAR_FULL'
              : 'OPEN';

        await tx.oPDSlot.update({
          where: { id: dto.slotId },
          data: { bookedCount: newCount, status: newStatus },
        });
      }

      // Create arrival record
      await tx.patientArrival.create({
        data: {
          id: uuidv4(),
          appointmentId: apt.id,
          status: 'EXPECTED',
        },
      });

      // Generate token
      const tokenCount = await tx.oPDToken.count({
        where: {
          appointment: {
            hospitalId: dto.hospitalId,
            departmentId: dto.departmentId,
            appointmentDate: dto.appointmentDate,
          },
        },
      });
      const tokenNumber = tokenCount + 1;
      const deptCode = await tx.department.findUnique({
        where: { id: dto.departmentId },
        select: { code: true },
      });
      const displayCode = `${deptCode?.code || 'GEN'}-${String(tokenNumber).padStart(3, '0')}`;

      await tx.oPDToken.create({
        data: {
          id: uuidv4(),
          appointmentId: apt.id,
          tokenNumber,
          displayCode,
          status: 'GENERATED',
        },
      });

      return apt;
    });

    // Audit
    await this.audit.log({
      actorId,
      actorRole,
      action: 'APPOINTMENT_BOOKED',
      entity: 'Appointment',
      entityId: appointment.id,
      newValue: { hospitalId: dto.hospitalId, slotId: dto.slotId },
    });

    // Realtime
    this.realtime.emitToHospital(dto.hospitalId, 'hospital.queue.updated', {
      hospitalId: dto.hospitalId,
      departmentId: dto.departmentId,
      event: 'APPOINTMENT_BOOKED',
    });

    return this.prisma.appointment.findUnique({
      where: { id: appointment.id },
      include: { token: true, slot: true, department: true, hospital: true },
    });
  }

  async findByPatient(
    patientId: string,
    query: { status?: AppointmentStatus; page?: number; limit?: number },
  ) {
    const resolvedPatientId = await this.resolvePatientId(patientId);
    const { status, page = 1, limit = 20 } = query;
    const skip = (page - 1) * limit;

    return this.prisma.appointment.findMany({
      where: {
        patientId: resolvedPatientId,
        deletedAt: null,
        ...(status && { status }),
      },
      skip,
      take: limit,
      include: {
        token: true,
        slot: true,
        department: true,
        hospital: true,
        arrival: true,
      },
      orderBy: { appointmentDate: 'desc' },
    });
  }

  async findOne(id: string, patientId: string, requirePatientMatch = true) {
    const resolvedPatientId = await this.resolvePatientId(patientId);
    const apt = await this.prisma.appointment.findUnique({
      where: { id },
      include: {
        token: true,
        slot: true,
        department: true,
        hospital: true,
        arrival: true,
        consultation: true,
      },
    });
    if (!apt) throw new NotFoundException('Appointment not found');
    if (requirePatientMatch && apt.patientId !== resolvedPatientId) {
      throw new ForbiddenException('Access denied');
    }
    return apt;
  }

  async cancelAppointment(
    id: string,
    patientId: string,
    actorId: string,
    actorRole: string,
  ) {
    const resolvedPatientId = await this.resolvePatientId(patientId);
    const apt = await this.prisma.appointment.findUnique({ where: { id } });
    if (!apt) throw new NotFoundException('Appointment not found');
    if (apt.patientId !== resolvedPatientId)
      throw new ForbiddenException('Access denied');
    if (!['BOOKED', 'CONFIRMED'].includes(apt.status)) {
      throw new BadRequestException('This appointment cannot be cancelled');
    }

    await this.prisma.$transaction(async (tx) => {
      await tx.appointment.update({
        where: { id },
        data: { status: 'CANCELLED' },
      });
      if (apt.slotId) {
        const slot = await tx.oPDSlot.findUnique({
          where: { id: apt.slotId },
        });
        if (slot && slot.bookedCount > 0) {
          await tx.oPDSlot.update({
            where: { id: apt.slotId },
            data: { bookedCount: slot.bookedCount - 1, status: 'OPEN' },
          });
        }
      }
    });

    await this.audit.log({
      actorId,
      actorRole,
      action: 'APPOINTMENT_CANCELLED',
      entity: 'Appointment',
      entityId: id,
    });

    return { success: true };
  }

  async getAvailableSlots(
    hospitalId: string,
    departmentId: string,
    date: Date,
  ) {
    const slots = await this.prisma.oPDSlot.findMany({
      where: {
        hospitalId,
        departmentId,
        date: date,
        status: { in: ['OPEN', 'NEAR_FULL'] },
        deletedAt: null,
      },
      include: {
        doctor: {
          include: { user: { select: { displayName: true } } },
        },
      },
      orderBy: { startTime: 'asc' },
    });

    return slots.map((slot) => ({
      ...slot,
      spotsRemaining: slot.capacity - slot.bookedCount,
      estimatedWaitMinutes: slot.bookedCount * 10, // 10 min avg consultation
    }));
  }

  // Reception: mark patient arrived
  async markArrived(
    appointmentId: string,
    hospitalId: string,
    isOffline: boolean,
    markedBy: string,
    actorId: string,
    actorRole: string,
  ) {
    const apt = await this.prisma.appointment.findUnique({
      where: { id: appointmentId },
      include: { arrival: true, token: true },
    });
    if (!apt) throw new NotFoundException('Appointment not found');
    if (apt.hospitalId !== hospitalId)
      throw new ForbiddenException('Access denied');

    const receptionistProfile = await this.prisma.receptionProfile.findUnique({
      where: { userId: markedBy },
    });
    const finalMarkedBy = receptionistProfile
      ? receptionistProfile.id
      : markedBy;

    await this.prisma.$transaction(async (tx) => {
      await tx.appointment.update({
        where: { id: appointmentId },
        data: { status: 'ARRIVED' },
      });

      if (apt.arrival) {
        await tx.patientArrival.update({
          where: { id: apt.arrival.id },
          data: {
            status: 'ARRIVED',
            arrivedAt: new Date(),
            isOfflineArrival: isOffline,
            markedBy: finalMarkedBy,
          },
        });
      }

      if (apt.token) {
        await tx.oPDToken.update({
          where: { id: apt.token.id },
          data: { status: 'GENERATED' },
        });
      }
    });

    await this.audit.log({
      actorId,
      actorRole,
      action: 'PATIENT_CHECKED_IN',
      entity: 'Appointment',
      entityId: appointmentId,
      newValue: { isOffline, markedBy },
    });

    this.realtime.emitToHospital(hospitalId, 'hospital.patient.arrived', {
      appointmentId,
      hospitalId,
      isOffline,
    });

    return { success: true, message: 'Patient marked as arrived' };
  }
}
