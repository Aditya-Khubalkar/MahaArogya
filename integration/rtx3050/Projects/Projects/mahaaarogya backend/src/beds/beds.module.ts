import { Module } from '@nestjs/common';
import { BedsService } from './beds.service';
import { BedsController } from './beds.controller';
import { AuditModule } from '../audit/audit.module';
import { NotificationsModule } from '../notifications/notifications.module';
import { RealtimeModule } from '../realtime/realtime.module';

@Module({
  imports: [AuditModule, NotificationsModule, RealtimeModule],
  providers: [BedsService],
  controllers: [BedsController],
  exports: [BedsService],
})
export class BedsModule {}
