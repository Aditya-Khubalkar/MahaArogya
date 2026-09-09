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
import { EmergencyService } from './emergency.service';
import { Permissions } from '../common/decorators/auth.decorators';
import { PERMISSIONS } from '../common/constants/permissions.constants';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import type { CurrentUserData } from '../common/decorators/current-user.decorator';
import { IsString, IsOptional, IsNumber, IsArray } from 'class-validator';

class CreateEmergencyDto {
  @IsOptional()
  @IsString()
  triageId?: string;

  @IsOptional()
  @IsArray()
  symptoms?: string[];

  @IsOptional()
  @IsNumber()
  patientLatitude?: number;

  @IsOptional()
  @IsNumber()
  patientLongitude?: number;
}

class SelectHospitalDto {
  @IsString()
  hospitalId: string;
}

@ApiTags('emergency')
@ApiBearerAuth()
@Controller('emergency')
export class EmergencyController {
  constructor(private readonly emergencyService: EmergencyService) {}

  @Post()
  @Permissions(PERMISSIONS.PATIENT_VIEW_OWN_EMERGENCY)
  @ApiOperation({ summary: 'Create emergency case from triage result' })
  create(
    @Body() dto: CreateEmergencyDto,
    @CurrentUser() user: CurrentUserData,
  ) {
    return this.emergencyService.createEmergencyCase(
      { ...dto, patientId: user.userId },
      user.userId,
      user.role,
    );
  }

  @Get('my')
  @Permissions(PERMISSIONS.PATIENT_VIEW_OWN_EMERGENCY)
  @ApiOperation({ summary: 'Get my emergency cases' })
  getMy(@CurrentUser() user: CurrentUserData) {
    return this.emergencyService.findByPatient(user.userId);
  }

  @Get()
  @Permissions(PERMISSIONS.HOSPITAL_VIEW_EMERGENCY)
  @ApiOperation({ summary: 'Get all active emergency cases (hospital/admin)' })
  findAll(
    @CurrentUser() user: CurrentUserData,
    @Query('page') page?: number,
    @Query('limit') limit?: number,
  ) {
    return this.emergencyService.findAll(
      user.hospitalId,
      user.districtId,
      page,
      limit,
    );
  }

  @Patch(':id/select-hospital')
  @Permissions(
    PERMISSIONS.PATIENT_VIEW_OWN_EMERGENCY,
    PERMISSIONS.HOSPITAL_VIEW_EMERGENCY,
  )
  @ApiOperation({ summary: 'Select hospital for emergency routing' })
  selectHospital(
    @Param('id') id: string,
    @Body() dto: SelectHospitalDto,
    @CurrentUser() user: CurrentUserData,
  ) {
    return this.emergencyService.selectHospital(
      id,
      dto.hospitalId,
      user.userId,
      user.role,
    );
  }

  @Patch(':id/resolve')
  @Permissions(PERMISSIONS.HOSPITAL_VIEW_EMERGENCY)
  @ApiOperation({ summary: 'Resolve emergency case' })
  resolve(@Param('id') id: string, @CurrentUser() user: CurrentUserData) {
    return this.emergencyService.resolveCase(id, user.userId, user.role);
  }
}
