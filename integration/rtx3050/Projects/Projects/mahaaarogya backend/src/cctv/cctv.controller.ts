import {
  Controller,
  Post,
  Get,
  Patch,
  Body,
  Param,
  Query,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { CCTVService } from './cctv.service';
import type { CCTVOccupancyEventDto } from './cctv.service';
import { Permissions, Public } from '../common/decorators/auth.decorators';
import { PERMISSIONS } from '../common/constants/permissions.constants';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import type { CurrentUserData } from '../common/decorators/current-user.decorator';
import { BedStatus } from '@prisma/client';

@ApiTags('cctv')
@ApiBearerAuth()
@Controller('cctv')
export class CCTVController {
  constructor(private readonly cctvService: CCTVService) {}

  @Post('events')
  @ApiOperation({
    summary: 'Ingest CCTV occupancy event (from CV system or mock)',
  })
  ingestEvent(@Body() dto: CCTVOccupancyEventDto) {
    return this.cctvService.ingestOccupancyEvent(dto);
  }

  @Get('devices/:hospitalId')
  @Permissions(PERMISSIONS.HOSPITAL_CONFIRM_CCTV)
  @ApiOperation({ summary: 'Get CCTV devices for hospital' })
  getDevices(@Param('hospitalId') hospitalId: string) {
    return this.cctvService.getDevices(hospitalId);
  }

  @Get('discrepancies/:hospitalId')
  @Permissions(PERMISSIONS.HOSPITAL_CONFIRM_CCTV)
  @ApiOperation({ summary: 'Get unresolved CCTV discrepancies for hospital' })
  getDiscrepancies(@Param('hospitalId') hospitalId: string) {
    return this.cctvService.getUnresolvedDiscrepancies(hospitalId);
  }

  @Patch('discrepancies/:id/resolve')
  @Permissions(PERMISSIONS.HOSPITAL_CONFIRM_CCTV)
  @ApiOperation({
    summary: 'Resolve a CCTV discrepancy (staff confirms actual status)',
  })
  resolveDiscrepancy(
    @Param('id') id: string,
    @Body()
    dto: {
      resolution:
        'CONFIRMED_CCTV' | 'CONFIRMED_AUTHORITATIVE' | 'MANUAL_OVERRIDE';
      newStatus?: BedStatus;
      notes?: string;
    },
    @CurrentUser() user: CurrentUserData,
  ) {
    return this.cctvService.resolveDiscrepancy(
      id,
      dto.resolution,
      dto.newStatus || null,
      user.userId,
      user.userId,
      user.role,
      dto.notes,
    );
  }

  @Post('mock/:hospitalId')
  @Permissions(PERMISSIONS.HOSPITAL_CONFIRM_CCTV)
  @ApiOperation({
    summary: 'Generate a mock CCTV event (for testing discrepancy workflow)',
  })
  generateMock(@Param('hospitalId') hospitalId: string) {
    return this.cctvService.generateMockCCTVEvent(hospitalId);
  }
}
