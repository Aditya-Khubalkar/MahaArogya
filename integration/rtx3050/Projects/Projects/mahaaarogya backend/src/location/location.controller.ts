import { Controller, Get, Post, Body, Query } from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiBearerAuth,
  ApiQuery,
} from '@nestjs/swagger';
import { LocationService } from './location.service';
import { Public, Permissions } from '../common/decorators/auth.decorators';
import { PERMISSIONS } from '../common/constants/permissions.constants';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import type { CurrentUserData } from '../common/decorators/current-user.decorator';
import { IsNumber, IsOptional, IsBoolean, IsString } from 'class-validator';

class StoreLocationDto {
  @IsOptional()
  @IsNumber()
  latitude?: number;

  @IsOptional()
  @IsNumber()
  longitude?: number;

  @IsOptional()
  @IsNumber()
  accuracy?: number;

  @IsOptional()
  @IsString()
  address?: string;

  @IsOptional()
  @IsBoolean()
  isManual?: boolean;
}

@ApiTags('location')
@ApiBearerAuth()
@Controller('location')
export class LocationController {
  constructor(private readonly locationService: LocationService) {}

  @Public()
  @Get('search')
  @ApiOperation({
    summary: 'Geocode a location query (free, Nominatim/OpenStreetMap)',
  })
  @ApiQuery({
    name: 'q',
    description: 'Search query e.g. "Nagpur Railway Station"',
  })
  search(@Query('q') q: string) {
    if (!q || q.trim().length < 2) {
      return [];
    }
    return this.locationService.geocode(q);
  }

  @Public()
  @Get('reverse')
  @ApiOperation({ summary: 'Reverse geocode lat/lon to address' })
  reverse(@Query('lat') lat: string, @Query('lon') lon: string) {
    return this.locationService.reverseGeocode(
      parseFloat(lat),
      parseFloat(lon),
    );
  }

  @Post('current')
  @Permissions(PERMISSIONS.PATIENT_SEARCH_LOCATION)
  @ApiOperation({ summary: 'Store patient current location (non-tracking)' })
  storeLocation(
    @Body() dto: StoreLocationDto,
    @CurrentUser() user: CurrentUserData,
  ) {
    return this.locationService.storeLocationRequest(user.userId, dto);
  }
}
