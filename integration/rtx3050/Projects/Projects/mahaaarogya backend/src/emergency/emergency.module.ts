import { Module } from '@nestjs/common';
import { EmergencyService } from './emergency.service';
import { EmergencyController } from './emergency.controller';
import { AuditModule } from '../audit/audit.module';
import { NotificationsModule } from '../notifications/notifications.module';
import { RealtimeModule } from '../realtime/realtime.module';
import { HospitalResourcesModule } from '../hospital-resources/hospital-resources.module';
import { LocationModule } from '../location/location.module';

@Module({
  imports: [
    AuditModule,
    NotificationsModule,
    RealtimeModule,
    HospitalResourcesModule,
    LocationModule,
  ],
  providers: [EmergencyService],
  controllers: [EmergencyController],
  exports: [EmergencyService],
})
export class EmergencyModule {}
