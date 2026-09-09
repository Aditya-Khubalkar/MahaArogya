import {
  Injectable,
  UnauthorizedException,
  BadRequestException,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../database/prisma.service';
import { ROLE_PERMISSIONS } from '../common/constants/permissions.constants';
import { UserRole } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';

export interface DemoLoginDto {
  role: UserRole;
  hospitalId?: string;
  departmentId?: string;
  districtId?: string;
}

export interface SessionPayload {
  sessionId: string;
  userId: string;
  role: string;
  hospitalId?: string;
  departmentId?: string;
  districtId?: string;
  permissions: string[];
}

@Injectable()
export class AuthService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly jwtService: JwtService,
    private readonly config: ConfigService,
  ) {}

  async demoLogin(dto: DemoLoginDto): Promise<{
    token: string;
    user: Record<string, unknown>;
    permissions: string[];
  }> {
    const { role, hospitalId, departmentId, districtId } = dto;

    if (!Object.values(UserRole).includes(role)) {
      throw new BadRequestException(`Invalid role: ${role}`);
    }

    // Find or use the demo user for this role
    let user = await this.prisma.user.findFirst({
      where: { role, isActive: true },
    });

    if (!user) {
      // Create a demo user on the fly if none exists
      user = await this.prisma.user.create({
        data: {
          id: uuidv4(),
          demoUsername: `demo-${role.toLowerCase()}-${Date.now()}`,
          displayName: `Demo ${role.replace(/_/g, ' ')}`,
          role,
          hospitalId: hospitalId || null,
          departmentId: departmentId || null,
          districtId: districtId || null,
          isActive: true,
        },
      });
    }

    const permissions = ROLE_PERMISSIONS[role] || [];
    const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24h

    // Create session record
    const session = await this.prisma.demoSession.create({
      data: {
        id: uuidv4(),
        userId: user.id,
        token: uuidv4(), // Will be replaced below
        role: role,
        hospitalId: hospitalId || user.hospitalId || null,
        departmentId: departmentId || user.departmentId || null,
        districtId: districtId || user.districtId || null,
        permissions,
        expiresAt,
        isActive: true,
      },
    });

    const payload: SessionPayload = {
      sessionId: session.id,
      userId: user.id,
      role,
      hospitalId: session.hospitalId || undefined,
      departmentId: session.departmentId || undefined,
      districtId: session.districtId || undefined,
      permissions,
    };

    const token = this.jwtService.sign(payload, {
      expiresIn: '24h',
    });

    // Store the actual JWT token reference
    await this.prisma.demoSession.update({
      where: { id: session.id },
      data: { token },
    });

    return {
      token,
      user: {
        id: user.id,
        displayName: user.displayName,
        role: user.role,
        hospitalId: session.hospitalId,
        departmentId: session.departmentId,
        districtId: session.districtId,
      },
      permissions,
    };
  }

  async validateToken(token: string): Promise<SessionPayload | null> {
    try {
      const payload = this.jwtService.verify<SessionPayload>(token);

      // Verify session still active in DB
      const session = await this.prisma.demoSession.findFirst({
        where: {
          userId: payload.userId,
          isActive: true,
          expiresAt: { gt: new Date() },
        },
      });

      if (!session) {
        return null;
      }

      return payload;
    } catch {
      return null;
    }
  }

  async logout(sessionId: string): Promise<void> {
    await this.prisma.demoSession.updateMany({
      where: { id: sessionId },
      data: { isActive: false },
    });
  }

  getAvailableRoles(): Record<string, string> {
    return {
      PUBLIC_PATIENT: 'Public / Patient',
      DOCTOR: 'Doctor',
      NURSE: 'Nurse',
      RECEPTION: 'Reception Staff',
      HOSPITAL_ADMIN: 'Hospital Administrator',
      HOSPITAL_HEAD: 'Hospital Head',
      DISTRICT_HEALTH_OFFICER: 'District Health Officer',
      GOVERNMENT_OFFICIAL: 'Government Official',
      SYSTEM_ADMIN: 'System Administrator',
    };
  }
}
