import { Module } from '@nestjs/common';
import { HospitalResourcesService } from './hospital-resources.service';
import { HospitalResourcesController } from './hospital-resources.controller';
import { AuditModule } from '../audit/audit.module';
import { RealtimeModule } from '../realtime/realtime.module';

@Module({
  imports: [AuditModule, RealtimeModule],
  providers: [HospitalResourcesService],
  controllers: [HospitalResourcesController],
  exports: [HospitalResourcesService],
})
export class HospitalResourcesModule {}
