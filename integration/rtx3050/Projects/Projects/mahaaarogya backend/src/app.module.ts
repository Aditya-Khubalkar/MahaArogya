import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { APP_GUARD, APP_FILTER, APP_INTERCEPTOR } from '@nestjs/core';

import configuration from './config/configuration';
import { PrismaModule } from './database/prisma.module';
import { AuthModule } from './auth/auth.module';
import { JwtAuthGuard } from './auth/jwt-auth.guard';
import { AllExceptionsFilter } from './common/filters/all-exceptions.filter';
import { ResponseTransformInterceptor } from './common/interceptors/response-transform.interceptor';
import { RequestLoggerInterceptor } from './common/interceptors/request-logger.interceptor';

// Feature Modules
import { AuditModule } from './audit/audit.module';
import { RealtimeModule } from './realtime/realtime.module';
import { NotificationsModule } from './notifications/notifications.module';
import { LocationModule } from './location/location.module';
import { HospitalsModule } from './hospitals/hospitals.module';
import { AppointmentsModule } from './appointments/appointments.module';
import { BedsModule } from './beds/beds.module';
import { HospitalResourcesModule } from './hospital-resources/hospital-resources.module';
import { EmergencyModule } from './emergency/emergency.module';
import { AIModule } from './ai/ai.module';
import { CCTVModule } from './cctv/cctv.module';
import { AnalyticsModule } from './analytics/analytics.module';
import { HealthModule } from './health/health.module';

@Module({
  imports: [
    // Configuration — must be first
    ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration],
      envFilePath: '.env',
    }),

    // Database
    PrismaModule,

    // Auth
    AuthModule,

    // Infrastructure
    AuditModule,
    RealtimeModule,
    NotificationsModule,

    // Features
    LocationModule,
    HospitalsModule,
    AppointmentsModule,
    BedsModule,
    HospitalResourcesModule,
    EmergencyModule,
    AIModule,
    CCTVModule,
    AnalyticsModule,
    HealthModule,
  ],
  providers: [
    // Global JWT auth guard — all routes require auth unless @Public()
    {
      provide: APP_GUARD,
      useClass: JwtAuthGuard,
    },
    // Global exception filter — standardizes all error responses
    {
      provide: APP_FILTER,
      useClass: AllExceptionsFilter,
    },
    // Global response transformer — wraps all responses in { success, data, ... }
    {
      provide: APP_INTERCEPTOR,
      useClass: ResponseTransformInterceptor,
    },
    // Global request logger
    {
      provide: APP_INTERCEPTOR,
      useClass: RequestLoggerInterceptor,
    },
  ],
})
export class AppModule {}
