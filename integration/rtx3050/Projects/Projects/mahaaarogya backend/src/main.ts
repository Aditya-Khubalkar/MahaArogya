import { NestFactory, Reflector } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe, Logger } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { ConfigService } from '@nestjs/config';
import { IoAdapter } from '@nestjs/platform-socket.io';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    logger: ['error', 'warn', 'log', 'debug', 'verbose'],
  });

  const config = app.get(ConfigService);
  const port = config.get<number>('app.port', 4000);
  const apiPrefix = config.get<string>('app.apiPrefix', 'api/v1');
  const corsOrigins = config.get<string[]>('app.corsOrigins', [
    'http://localhost:4000',
  ]);

  // ── CORS ────────────────────────────────────────────────────
  app.enableCors({
    origin: corsOrigins,
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  });

  // ── Global prefix ───────────────────────────────────────────
  app.setGlobalPrefix(apiPrefix);

  // ── Validation pipe ─────────────────────────────────────────
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true, // Strip unknown properties
      forbidNonWhitelisted: true,
      transform: true, // Auto-transform types
      transformOptions: { enableImplicitConversion: true },
    }),
  );

  // ── WebSockets ──────────────────────────────────────────────
  app.useWebSocketAdapter(new IoAdapter(app));

  // ── Swagger ─────────────────────────────────────────────────
  const swaggerConfig = new DocumentBuilder()
    .setTitle('MahaArogya — Sanjeevani Grid API')
    .setDescription(
      `
## MahaArogya Sanjeevani Grid — Complete Healthcare Router Backend

**Version**: 1.0.0 (Hackathon Prototype)

### Authentication
All endpoints require a Bearer JWT token (except public endpoints marked with 🔓).

Use **POST /api/v1/auth/demo-login** to get a token for any role.

### Demo Roles
- \`PUBLIC_PATIENT\` — Patient interface
- \`DOCTOR\` — Doctor interface
- \`NURSE\` — Nurse interface
- \`RECEPTION\` — Reception staff
- \`HOSPITAL_ADMIN\` — Hospital administrator
- \`HOSPITAL_HEAD\` — Hospital head
- \`DISTRICT_HEALTH_OFFICER\` — District health officer
- \`GOVERNMENT_OFFICIAL\` — Government dashboard
- \`SYSTEM_ADMIN\` — System administrator

### Important Notes
- ⚠️ This is a prototype. No real medical advice is provided.
- 🤖 AI is in MOCK mode — no real ML model is connected.
- 📷 CCTV is in MOCK mode — no real camera is connected.
- 🏥 All hospital data is SYNTHETIC.
      `,
    )
    .setVersion('1.0.0')
    .addBearerAuth()
    .addTag('auth', 'Authentication — Demo session management')
    .addTag('hospitals', 'Hospital search, listing, and availability')
    .addTag('location', 'Geocoding, reverse geocoding, nearby hospitals')
    .addTag('appointments', 'OPD booking, slots, tokens, queue')
    .addTag('beds', 'Bed management and status')
    .addTag('hospital-resources', 'ICU, oxygen, ventilator resources')
    .addTag('emergency', 'Emergency case routing and resource holds')
    .addTag('ai', 'AI conversation, PatientState, triage')
    .addTag('cctv', 'CCTV occupancy events and discrepancy resolution')
    .addTag('analytics', 'Hospital, district, and government dashboards')
    .addTag('notifications', 'In-app notifications')
    .addTag('audit', 'Audit logs (System Admin)')
    .addTag('health', 'Health checks')
    .build();

  const swaggerDocument = SwaggerModule.createDocument(app, swaggerConfig);
  SwaggerModule.setup(`${apiPrefix}/docs`, app, swaggerDocument, {
    swaggerOptions: {
      persistAuthorization: true,
      tagsSorter: 'alpha',
      operationsSorter: 'alpha',
    },
    customSiteTitle: 'MahaArogya API Docs',
  });

  await app.listen(port);

  const logger = new Logger('Bootstrap');
  logger.log(`🚀 MahaArogya Backend running on http://localhost:${port}`);
  logger.log(`📖 Swagger UI: http://localhost:${port}/${apiPrefix}/docs`);
  logger.log(`🏥 Environment: ${config.get('app.nodeEnv')}`);
  logger.log(`🤖 Mock AI: ${config.get('app.mockAI')}`);
  logger.log(`📷 Mock CCTV: ${config.get('app.mockCCTV')}`);
}

bootstrap().catch((err) => {
  console.error('Failed to start MahaArogya backend:', err);
  process.exit(1);
});
