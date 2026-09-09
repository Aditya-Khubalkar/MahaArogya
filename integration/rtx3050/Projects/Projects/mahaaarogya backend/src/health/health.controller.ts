import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { Public } from '../common/decorators/auth.decorators';
import { PrismaService } from '../database/prisma.service';
import { ConfigService } from '@nestjs/config';

@ApiTags('health')
@Controller('health')
export class HealthController {
  private readonly startTime = Date.now();

  constructor(
    private readonly prisma: PrismaService,
    private readonly config: ConfigService,
  ) {}

  @Public()
  @Get()
  @ApiOperation({ summary: 'Overall health check' })
  async check() {
    const dbOk = await this.prisma.healthCheck();
    return {
      status: dbOk ? 'ok' : 'degraded',
      version: '1.0.0',
      uptimeSeconds: Math.floor((Date.now() - this.startTime) / 1000),
      environment: this.config.get('app.nodeEnv'),
      demoMode: this.config.get('app.demoMode'),
      mockAI: this.config.get('app.mockAI'),
      timestamp: new Date().toISOString(),
      services: {
        database: dbOk ? 'ok' : 'error',
        ai: this.config.get('app.mockAI') ? 'mock' : 'remote',
        cctv: this.config.get('app.mockCCTV') ? 'mock' : 'remote',
        realtime: 'ok',
      },
    };
  }

  @Public()
  @Get('database')
  @ApiOperation({ summary: 'Database health check' })
  async checkDatabase() {
    const ok = await this.prisma.healthCheck();
    return {
      status: ok ? 'ok' : 'error',
      database: 'postgresql',
      message: ok ? 'Connected' : 'Connection failed',
    };
  }

  @Public()
  @Get('ai')
  @ApiOperation({ summary: 'AI service health check' })
  checkAI() {
    return {
      status: 'ok',
      mode: this.config.get('app.mockAI') ? 'MOCK' : 'REMOTE',
      enabled: this.config.get('app.aiServiceEnabled'),
      url: this.config.get('app.mockAI')
        ? 'n/a'
        : this.config.get('app.aiServiceUrl'),
      note: this.config.get('app.mockAI')
        ? 'Mock AI active. Connect real AI model by setting MOCK_AI=false and AI_SERVICE_URL.'
        : 'External AI service configured.',
    };
  }

  @Public()
  @Get('realtime')
  @ApiOperation({ summary: 'WebSocket/realtime health check' })
  checkRealtime() {
    return {
      status: 'ok',
      protocol: 'socket.io',
      namespace: '/realtime',
    };
  }
}
