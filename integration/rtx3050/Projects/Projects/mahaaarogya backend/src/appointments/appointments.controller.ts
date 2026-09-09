import {
  Controller,
  Post,
  Get,
  Patch,
  Delete,
  Body,
  Param,
  Query,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import {
  AppointmentsService,
  BookAppointmentDto,
} from './appointments.service';
import { Permissions } from '../common/decorators/auth.decorators';
import { PERMISSIONS } from '../common/constants/permissions.constants';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import type { CurrentUserData } from '../common/decorators/current-user.decorator';
import { IsString, IsDateString, IsOptional } from 'class-validator';
import { Type } from 'class-transformer';

class BookAppointmentBodyDto {
  @IsString()
  hospitalId: string;

  @IsString()
  departmentId: string;

  @IsOptional()
  @IsString()
  doctorId?: string;

  @IsOptional()
  @IsString()
  slotId?: string;

  @IsDateString()
  appointmentDate: string;

  @IsOptional()
  @IsString()
  reason?: string;
}

class MarkArrivedDto {
  @IsString()
  appointmentId: string;

  @IsOptional()
  isOffline?: boolean;
}

@ApiTags('appointments')
@ApiBearerAuth()
@Controller('appointments')
export class AppointmentsController {
  constructor(private readonly appointmentsService: AppointmentsService) {}

  @Post()
  @Permissions(PERMISSIONS.PATIENT_BOOK_APPOINTMENT)
  @ApiOperation({ summary: 'Book an appointment' })
  book(
    @Body() dto: BookAppointmentBodyDto,
    @CurrentUser() user: CurrentUserData,
  ) {
    return this.appointmentsService.bookAppointment(
      user.userId,
      {
        ...dto,
        appointmentDate: new Date(dto.appointmentDate),
      },
      user.userId,
      user.role,
    );
  }

  @Get()
  @Permissions(PERMISSIONS.PATIENT_VIEW_OWN_APPOINTMENTS)
  @ApiOperation({ summary: 'Get my appointments' })
  getMyAppointments(
    @CurrentUser() user: CurrentUserData,
    @Query('page') page?: number,
    @Query('limit') limit?: number,
  ) {
    return this.appointmentsService.findByPatient(user.userId, { page, limit });
  }

  @Get(':id')
  @Permissions(PERMISSIONS.PATIENT_VIEW_OWN_APPOINTMENTS)
  @ApiOperation({ summary: 'Get appointment details' })
  findOne(@Param('id') id: string, @CurrentUser() user: CurrentUserData) {
    return this.appointmentsService.findOne(id, user.userId);
  }

  @Delete(':id')
  @Permissions(PERMISSIONS.PATIENT_CANCEL_APPOINTMENT)
  @ApiOperation({ summary: 'Cancel an appointment' })
  cancel(@Param('id') id: string, @CurrentUser() user: CurrentUserData) {
    return this.appointmentsService.cancelAppointment(
      id,
      user.userId,
      user.userId,
      user.role,
    );
  }

  @Get('slots/:hospitalId/:departmentId')
  @Permissions(PERMISSIONS.PATIENT_BOOK_APPOINTMENT)
  @ApiOperation({
    summary: 'Get available OPD slots for a hospital/department/date',
  })
  getSlots(
    @Param('hospitalId') hospitalId: string,
    @Param('departmentId') departmentId: string,
    @Query('date') date: string,
  ) {
    return this.appointmentsService.getAvailableSlots(
      hospitalId,
      departmentId,
      new Date(date),
    );
  }

  // Reception endpoint
  @Patch('arrive')
  @Permissions(PERMISSIONS.RECEPTION_MARK_ARRIVED)
  @ApiOperation({
    summary: 'Reception: mark patient as arrived (offline or online)',
  })
  markArrived(
    @Body() dto: MarkArrivedDto,
    @CurrentUser() user: CurrentUserData,
  ) {
    return this.appointmentsService.markArrived(
      dto.appointmentId,
      user.hospitalId!,
      dto.isOffline ?? false,
      user.userId,
      user.userId,
      user.role,
    );
  }
}
