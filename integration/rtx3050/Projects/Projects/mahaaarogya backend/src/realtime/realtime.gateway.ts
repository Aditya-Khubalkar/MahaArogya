import {
  WebSocketGateway,
  WebSocketServer,
  OnGatewayConnection,
  OnGatewayDisconnect,
  SubscribeMessage,
  MessageBody,
  ConnectedSocket,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { Logger } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { SessionPayload } from '../auth/auth.service';

@WebSocketGateway({
  cors: {
    origin: '*', // Configured properly via ConfigService in production
  },
  namespace: '/realtime',
})
export class RealtimeGateway
  implements OnGatewayConnection, OnGatewayDisconnect
{
  @WebSocketServer()
  server: Server;

  private readonly logger = new Logger(RealtimeGateway.name);

  // Track connected clients: socketId → user info
  private connectedClients = new Map<
    string,
    { userId: string; role: string; hospitalId?: string; districtId?: string }
  >();

  constructor(
    private readonly jwtService: JwtService,
    private readonly config: ConfigService,
  ) {}

  async handleConnection(client: Socket) {
    const token = client.handshake.auth?.token as string;
    if (!token) {
      this.logger.warn(
        `Client ${client.id} connected without token — disconnecting`,
      );
      client.disconnect();
      return;
    }

    try {
      const payload = this.jwtService.verify<SessionPayload>(token, {
        secret: this.config.get<string>('app.jwtSecret'),
      });

      this.connectedClients.set(client.id, {
        userId: payload.userId,
        role: payload.role,
        hospitalId: payload.hospitalId,
        districtId: payload.districtId,
      });

      // Auto-join appropriate rooms based on role
      if (payload.hospitalId) {
        await client.join(`hospital:${payload.hospitalId}`);
      }
      if (payload.districtId) {
        await client.join(`district:${payload.districtId}`);
      }
      await client.join(`user:${payload.userId}`);
      await client.join(`role:${payload.role}`);

      this.logger.log(`Client connected: ${client.id} role=${payload.role}`);
    } catch {
      this.logger.warn(`Client ${client.id} invalid token — disconnecting`);
      client.disconnect();
    }
  }

  handleDisconnect(client: Socket) {
    this.connectedClients.delete(client.id);
    this.logger.log(`Client disconnected: ${client.id}`);
  }

  @SubscribeMessage('join-room')
  handleJoinRoom(
    @ConnectedSocket() client: Socket,
    @MessageBody() data: { room: string },
  ) {
    const user = this.connectedClients.get(client.id);
    if (!user) return;

    // Only allow joining rooms the user is scoped to
    const allowed = this.isAllowedRoom(user, data.room);
    if (allowed) {
      client.join(data.room);
      return { joined: data.room };
    }
    return { error: 'Not authorized to join this room' };
  }

  // ── Emit helpers ──────────────────────────────────────────

  emitToHospital(hospitalId: string, event: string, data: unknown) {
    this.server.to(`hospital:${hospitalId}`).emit(event, data);
  }

  emitToDistrict(districtId: string, event: string, data: unknown) {
    this.server.to(`district:${districtId}`).emit(event, data);
  }

  emitToUser(userId: string, event: string, data: unknown) {
    this.server.to(`user:${userId}`).emit(event, data);
  }

  emitToRole(role: string, event: string, data: unknown) {
    this.server.to(`role:${role}`).emit(event, data);
  }

  emitToAll(event: string, data: unknown) {
    this.server.emit(event, data);
  }

  private isAllowedRoom(
    user: {
      userId: string;
      role: string;
      hospitalId?: string;
      districtId?: string;
    },
    room: string,
  ): boolean {
    if (room === `user:${user.userId}`) return true;
    if (room === `role:${user.role}`) return true;
    if (user.hospitalId && room === `hospital:${user.hospitalId}`) return true;
    if (user.districtId && room === `district:${user.districtId}`) return true;
    if (['GOVERNMENT_OFFICIAL', 'SYSTEM_ADMIN'].includes(user.role))
      return true;
    return false;
  }
}
