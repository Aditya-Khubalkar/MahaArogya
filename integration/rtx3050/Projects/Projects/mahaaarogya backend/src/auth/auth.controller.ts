import {
  Controller,
  Post,
  Get,
  Body,
  Req,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBody, ApiResponse } from '@nestjs/swagger';
import { AuthService, DemoLoginDto } from './auth.service';
import { Public } from '../common/decorators/auth.decorators';
import { IsEnum, IsOptional, IsString } from 'class-validator';
import { UserRole } from '@prisma/client';
import { Request } from 'express';

class DemoLoginBodyDto {
  @IsEnum(UserRole)
  role: UserRole;

  @IsOptional()
  @IsString()
  hospitalId?: string;

  @IsOptional()
  @IsString()
  departmentId?: string;

  @IsOptional()
  @IsString()
  districtId?: string;
}

@ApiTags('auth')
@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Public()
  @Get('roles')
  @ApiOperation({ summary: 'Get all available demo roles' })
  getRoles() {
    return this.authService.getAvailableRoles();
  }

  @Public()
  @Post('demo-login')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Demo login — select a role to create a session' })
  @ApiBody({ type: DemoLoginBodyDto })
  @ApiResponse({ status: 200, description: 'Login successful with JWT token' })
  async demoLogin(@Body() dto: DemoLoginBodyDto) {
    return this.authService.demoLogin(dto);
  }

  @Post('logout')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Logout — invalidate demo session' })
  async logout(@Req() req: Request & { user?: { sessionId: string } }) {
    const sessionId = req.user?.sessionId;
    if (sessionId) {
      await this.authService.logout(sessionId);
    }
    return { message: 'Logged out successfully' };
  }

  @Get('me')
  @ApiOperation({ summary: 'Get current session info' })
  getMe(@Req() req: Request & { user?: Record<string, unknown> }) {
    return req.user;
  }
}
