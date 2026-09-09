import { Controller, Get, Patch, Param, Query, Body } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { BedsService } from './beds.service';
import type { UpdateBedStatusDto } from './beds.service';
import { Permissions } from '../common/decorators/auth.decorators';
import { PERMISSIONS } from '../common/constants/permissions.constants';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import type { CurrentUserData } from '../common/decorators/current-user.decorator';
import { BedType, BedStatus } from '@prisma/client';

@ApiTags('beds')
@ApiBearerAuth()
@Controller('beds')
export class BedsController {
  constructor(private readonly bedsService: BedsService) {}

  @Get('hospital/:hospitalId')
  @Permissions(PERMISSIONS.HOSPITAL_VIEW_RESOURCES)
  @ApiOperation({ summary: 'Get all beds for a hospital' })
  findAll(
    @Param('hospitalId') hospitalId: string,
    @Query('bedType') bedType?: BedType,
    @Query('status') status?: BedStatus,
    @Query('ward') ward?: string,
    @Query('page') page?: number,
    @Query('limit') limit?: number,
  ) {
    return this.bedsService.findAll(hospitalId, {
      bedType,
      status,
      ward,
      page,
      limit,
    });
  }

  @Get(':id')
  @Permissions(PERMISSIONS.HOSPITAL_VIEW_RESOURCES)
  @ApiOperation({ summary: 'Get bed details with status history' })
  findOne(@Param('id') id: string) {
    return this.bedsService.findOne(id);
  }

  @Patch(':id/status')
  @Permissions(PERMISSIONS.HOSPITAL_MANAGE_BEDS)
  @ApiOperation({ summary: 'Update bed status' })
  updateStatus(
    @Param('id') id: string,
    @Body() dto: UpdateBedStatusDto,
    @CurrentUser() user: CurrentUserData,
  ) {
    return this.bedsService.updateStatus(id, dto, user.userId, user.role);
  }

  @Get('hospital/:hospitalId/summary')
  @Permissions(PERMISSIONS.PATIENT_VIEW_HOSPITALS)
  @ApiOperation({ summary: 'Get bed availability summary by type and status' })
  getSummary(@Param('hospitalId') hospitalId: string) {
    return this.bedsService.getAvailabilitySummary(hospitalId);
  }
}
