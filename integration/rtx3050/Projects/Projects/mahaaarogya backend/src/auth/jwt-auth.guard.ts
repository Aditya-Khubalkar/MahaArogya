import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
  ForbiddenException,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import {
  PUBLIC_KEY,
  PERMISSIONS_KEY,
  ROLES_KEY,
} from '../common/decorators/auth.decorators';
import { SessionPayload } from './auth.service';

@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(
    private readonly reflector: Reflector,
    private readonly jwtService: JwtService,
    private readonly config: ConfigService,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    // Check if route is marked as public
    const isPublic = this.reflector.getAllAndOverride<boolean>(PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) return true;

    const request = context.switchToHttp().getRequest();
    const token = this.extractToken(request);

    if (!token) {
      throw new UnauthorizedException('No authentication token provided');
    }

    let payload: SessionPayload;
    try {
      payload = this.jwtService.verify<SessionPayload>(token, {
        secret: this.config.get<string>('app.jwtSecret'),
      });
    } catch {
      throw new UnauthorizedException('Invalid or expired token');
    }

    // Attach user to request
    request.user = payload;

    // Check required roles
    const requiredRoles = this.reflector.getAllAndOverride<string[]>(
      ROLES_KEY,
      [context.getHandler(), context.getClass()],
    );
    if (requiredRoles && requiredRoles.length > 0) {
      if (!requiredRoles.includes(payload.role)) {
        throw new ForbiddenException(
          `Role ${payload.role} is not allowed to access this resource`,
        );
      }
    }

    // Check required permissions
    const requiredPermissions = this.reflector.getAllAndOverride<string[]>(
      PERMISSIONS_KEY,
      [context.getHandler(), context.getClass()],
    );
    if (requiredPermissions && requiredPermissions.length > 0) {
      const userPerms = new Set(payload.permissions || []);
      const hasAny = requiredPermissions.some((p) => userPerms.has(p));
      if (!hasAny) {
        throw new ForbiddenException(
          'Insufficient permissions to access this resource',
        );
      }
    }

    return true;
  }

  private extractToken(request: {
    headers: Record<string, string | string[]>;
  }): string | null {
    const authHeader = request.headers['authorization'];
    if (typeof authHeader === 'string' && authHeader.startsWith('Bearer ')) {
      return authHeader.substring(7);
    }
    return null;
  }
}
