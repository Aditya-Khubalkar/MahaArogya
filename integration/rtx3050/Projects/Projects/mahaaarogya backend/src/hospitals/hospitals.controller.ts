import { Controller, Get, Param, Query } from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiBearerAuth,
  ApiQuery,
} from '@nestjs/swagger';
import { HospitalsService } from './hospitals.service';
import { Permissions, Public } from '../common/decorators/auth.decorators';
import { PERMISSIONS } from '../common/constants/permissions.constants';

@ApiTags('hospitals')
@ApiBearerAuth()
@Controller('hospitals')
export class HospitalsController {
  constructor(private readonly hospitalsService: HospitalsService) {}

  @Public()
  @Get()
  @ApiOperation({ summary: 'List all hospitals' })
  findAll(
    @Query('districtId') districtId?: string,
    @Query('stateId') stateId?: string,
    @Query('page') page?: number,
    @Query('limit') limit?: number,
  ) {
    return this.hospitalsService.findAll({ districtId, stateId, page, limit });
  }

  @Public()
  @Get('nearby')
  @ApiOperation({ summary: 'Find hospitals near a location (Haversine)' })
  @ApiQuery({ name: 'lat', description: 'Latitude', example: 21.1458 })
  @ApiQuery({ name: 'lon', description: 'Longitude', example: 79.0882 })
  @ApiQuery({
    name: 'radius',
    required: false,
    description: 'Radius in km',
    example: 20,
  })
  @ApiQuery({
    name: 'urgency',
    required: false,
    enum: ['ROUTINE', 'PRIORITY', 'URGENT', 'EMERGENCY'],
  })
  @ApiQuery({ name: 'emergencyOnly', required: false })
  findNearby(
    @Query('lat') lat: string,
    @Query('lon') lon: string,
    @Query('radius') radius?: string,
    @Query('department') department?: string,
    @Query('urgency') urgency?: string,
    @Query('emergencyOnly') emergencyOnly?: string,
  ) {
    return this.hospitalsService.findNearby({
      lat: parseFloat(lat),
      lon: parseFloat(lon),
      radiusKm: radius ? parseFloat(radius) : undefined,
      department,
      urgency,
      emergencyRequired: emergencyOnly === 'true',
    });
  }

  @Public()
  @Get(':id')
  @ApiOperation({ summary: 'Get hospital details' })
  findOne(@Param('id') id: string) {
    return this.hospitalsService.findOne(id);
  }

  @Get(':id/availability')
  @Permissions(PERMISSIONS.PATIENT_VIEW_HOSPITALS)
  @ApiOperation({ summary: 'Get hospital resource availability summary' })
  getAvailability(@Param('id') id: string) {
    return this.hospitalsService.getAvailabilitySummary(id);
  }

  @Public()
  @Get(':id/departments')
  @ApiOperation({ summary: 'Get hospital departments' })
  getDepartments(@Param('id') id: string) {
    return this.hospitalsService.getDepartments(id);
  }
}
