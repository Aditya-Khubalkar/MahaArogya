import { Module } from '@nestjs/common';
import { CCTVService } from './cctv.service';
import { CCTVController } from './cctv.controller';
import { AuditModule } from '../audit/audit.module';
import { NotificationsModule } from '../notifications/notifications.module';
import { RealtimeModule } from '../realtime/realtime.module';

@Module({
  imports: [AuditModule, NotificationsModule, RealtimeModule],
  providers: [CCTVService],
  controllers: [CCTVController],
  exports: [CCTVService],
})
export class CCTVModule {}
