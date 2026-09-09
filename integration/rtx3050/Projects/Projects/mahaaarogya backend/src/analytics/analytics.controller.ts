import { Controller, Get, Param } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { PrismaService } from '../database/prisma.service';
import { Permissions } from '../common/decorators/auth.decorators';
import { PERMISSIONS } from '../common/constants/permissions.constants';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import type { CurrentUserData } from '../common/decorators/current-user.decorator';

@ApiTags('analytics')
@ApiBearerAuth()
@Controller('analytics')
export class AnalyticsController {
  constructor(private readonly prisma: PrismaService) {}

  @Get('hospital/:hospitalId')
  @Permissions(PERMISSIONS.HOSPITAL_VIEW_ANALYTICS)
  @ApiOperation({ summary: 'Get hospital dashboard analytics' })
  async getHospitalAnalytics(@Param('hospitalId') hospitalId: string) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const [
      totalBeds,
      availableBeds,
      totalICU,
      availableICU,
      totalAppointments,
      completedConsultations,
      activeEmergencies,
      unresolvedCCTV,
    ] = await Promise.all([
      this.prisma.bed.count({ where: { hospitalId, deletedAt: null } }),
      this.prisma.bed.count({
        where: { hospitalId, status: 'AVAILABLE', deletedAt: null },
      }),
      this.prisma.bed.count({
        where: { hospitalId, bedType: 'ICU_BED', deletedAt: null },
      }),
      this.prisma.bed.count({
        where: {
          hospitalId,
          bedType: 'ICU_BED',
          status: 'AVAILABLE',
          deletedAt: null,
        },
      }),
      this.prisma.appointment.count({
        where: { hospitalId, appointmentDate: { gte: today } },
      }),
      this.prisma.consultation.count({
        where: {
          appointment: { hospitalId },
          status: 'COMPLETED',
          completedAt: { gte: today },
        },
      }),
      this.prisma.emergencyCase.count({
        where: { hospitalId, status: { in: ['ACTIVE', 'RESOURCE_HELD'] } },
      }),
      this.prisma.cCTVDiscrepancy.count({
        where: { isResolved: false, event: { device: { hospitalId } } },
      }),
    ]);

    const bedOccupancyPercent =
      totalBeds > 0
        ? Math.round(((totalBeds - availableBeds) / totalBeds) * 100)
        : 0;
    const icuOccupancyPercent =
      totalICU > 0
        ? Math.round(((totalICU - availableICU) / totalICU) * 100)
        : 0;

    return {
      hospitalId,
      date: today.toISOString().split('T')[0],
      beds: {
        total: totalBeds,
        available: availableBeds,
        occupied: totalBeds - availableBeds,
        occupancyPercent: bedOccupancyPercent,
      },
      icu: {
        total: totalICU,
        available: availableICU,
        occupied: totalICU - availableICU,
        occupancyPercent: icuOccupancyPercent,
      },
      opd: {
        totalAppointmentsToday: totalAppointments,
        completedConsultations,
      },
      emergencies: { active: activeEmergencies },
      cctv: { unresolvedDiscrepancies: unresolvedCCTV },
    };
  }

  @Get('district/:districtId')
  @Permissions(PERMISSIONS.DHO_VIEW_ANALYTICS)
  @ApiOperation({ summary: 'Get district-level analytics' })
  async getDistrictAnalytics(@Param('districtId') districtId: string) {
    const hospitals = await this.prisma.hospital.findMany({
      where: { districtId, deletedAt: null },
      select: { id: true, name: true },
    });
    const hospitalIds = hospitals.map((h) => h.id);

    const [
      totalBeds,
      availableBeds,
      totalICU,
      availableICU,
      activeEmergencies,
    ] = await Promise.all([
      this.prisma.bed.count({
        where: { hospitalId: { in: hospitalIds }, deletedAt: null },
      }),
      this.prisma.bed.count({
        where: {
          hospitalId: { in: hospitalIds },
          status: 'AVAILABLE',
          deletedAt: null,
        },
      }),
      this.prisma.bed.count({
        where: {
          hospitalId: { in: hospitalIds },
          bedType: 'ICU_BED',
          deletedAt: null,
        },
      }),
      this.prisma.bed.count({
        where: {
          hospitalId: { in: hospitalIds },
          bedType: 'ICU_BED',
          status: 'AVAILABLE',
          deletedAt: null,
        },
      }),
      this.prisma.emergencyCase.count({
        where: {
          hospitalId: { in: hospitalIds },
          status: { in: ['ACTIVE', 'RESOURCE_HELD'] },
        },
      }),
    ]);

    return {
      districtId,
      hospitalCount: hospitals.length,
      hospitals: hospitals.map((h) => h.name),
      beds: {
        total: totalBeds,
        available: availableBeds,
        occupied: totalBeds - availableBeds,
      },
      icu: { total: totalICU, available: availableICU },
      emergencies: { active: activeEmergencies },
    };
  }

  @Get('government/state')
  @Permissions(PERMISSIONS.GOVT_VIEW_STATE_OVERVIEW)
  @ApiOperation({
    summary: 'Get state-wide aggregate analytics (no patient PII)',
  })
  async getStateAnalytics() {
    const [
      totalHospitals,
      activeHospitals,
      totalBeds,
      availableBeds,
      totalICU,
      availableICU,
      activeEmergencies,
      districts,
    ] = await Promise.all([
      this.prisma.hospital.count({ where: { deletedAt: null } }),
      this.prisma.hospital.count({
        where: { status: 'ACTIVE', deletedAt: null },
      }),
      this.prisma.bed.count({ where: { deletedAt: null } }),
      this.prisma.bed.count({
        where: { status: 'AVAILABLE', deletedAt: null },
      }),
      this.prisma.bed.count({ where: { bedType: 'ICU_BED', deletedAt: null } }),
      this.prisma.bed.count({
        where: { bedType: 'ICU_BED', status: 'AVAILABLE', deletedAt: null },
      }),
      this.prisma.emergencyCase.count({
        where: { status: { in: ['ACTIVE', 'RESOURCE_HELD'] } },
      }),
      this.prisma.district.findMany({ select: { id: true, name: true } }),
    ]);

    return {
      // Aggregate only — no patient identifiers
      hospitals: { total: totalHospitals, active: activeHospitals },
      beds: {
        total: totalBeds,
        available: availableBeds,
        occupied: totalBeds - availableBeds,
        occupancyPercent:
          totalBeds > 0
            ? Math.round(((totalBeds - availableBeds) / totalBeds) * 100)
            : 0,
      },
      icu: {
        total: totalICU,
        available: availableICU,
        occupancyPercent:
          totalICU > 0
            ? Math.round(((totalICU - availableICU) / totalICU) * 100)
            : 0,
      },
      emergencies: { active: activeEmergencies },
      districts: districts.length,
    };
  }
}
