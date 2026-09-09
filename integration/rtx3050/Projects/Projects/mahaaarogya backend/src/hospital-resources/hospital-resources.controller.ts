import {
  Controller,
  Get,
  Patch,
  Post,
  Body,
  Param,
  Query,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { HospitalResourcesService } from './hospital-resources.service';
import { Permissions } from '../common/decorators/auth.decorators';
import { PERMISSIONS } from '../common/constants/permissions.constants';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import type { CurrentUserData } from '../common/decorators/current-user.decorator';
import { ResourceType, ResourceStatus } from '@prisma/client';

@ApiTags('hospital-resources')
@ApiBearerAuth()
@Controller('resources')
export class HospitalResourcesController {
  constructor(private readonly resourcesService: HospitalResourcesService) {}

  @Get('hospital/:hospitalId')
  @Permissions(PERMISSIONS.HOSPITAL_VIEW_RESOURCES)
  @ApiOperation({ summary: 'Get all resources for a hospital' })
  findByHospital(
    @Param('hospitalId') hospitalId: string,
    @Query('resourceType') resourceType?: ResourceType,
    @Query('status') status?: ResourceStatus,
  ) {
    return this.resourcesService.findByHospital(hospitalId, {
      resourceType,
      status,
    });
  }

  @Post('holds')
  @Permissions(PERMISSIONS.HOSPITAL_VIEW_EMERGENCY)
  @ApiOperation({ summary: 'Create a resource hold for emergency case' })
  createHold(
    @Body()
    dto: { emergencyCaseId: string; resourceId?: string; bedId?: string },
    @CurrentUser() user: CurrentUserData,
  ) {
    return this.resourcesService.createHold(dto, user.userId, user.role);
  }

  @Patch('holds/:id/confirm')
  @Permissions(PERMISSIONS.HOSPITAL_MANAGE_BEDS)
  @ApiOperation({ summary: 'Confirm a resource hold' })
  confirmHold(@Param('id') id: string, @CurrentUser() user: CurrentUserData) {
    return this.resourcesService.confirmHold(id, user.userId, user.role);
  }

  @Patch('holds/:id/release')
  @Permissions(PERMISSIONS.HOSPITAL_MANAGE_BEDS)
  @ApiOperation({ summary: 'Release a resource hold' })
  releaseHold(
    @Param('id') id: string,
    @Body() dto: { reason?: string },
    @CurrentUser() user: CurrentUserData,
  ) {
    return this.resourcesService.releaseHold(
      id,
      user.userId,
      user.role,
      dto.reason,
    );
  }
}
