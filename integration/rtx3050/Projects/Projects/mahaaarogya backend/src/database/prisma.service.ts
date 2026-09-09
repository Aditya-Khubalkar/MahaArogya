import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class PrismaService
  extends PrismaClient
  implements OnModuleInit, OnModuleDestroy
{
  async onModuleInit() {
    await this.$connect();
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }

  async healthCheck(): Promise<boolean> {
    try {
      await this.$queryRaw`SELECT 1`;
      return true;
    } catch {
      return false;
    }
  }

  async cleanDatabase() {
    if (process.env.NODE_ENV === 'production') {
      throw new Error('cleanDatabase is not allowed in production');
    }
    // Delete in dependency order for tests
    const tables = [
      'audit_logs',
      'notifications',
      'cctv_discrepancies',
      'cctv_occupancy_events',
      'bed_camera_mappings',
      'cctv_zones',
      'cctv_devices',
      'patient_state_snapshots',
      'ai_messages',
      'ai_conversations',
      'resource_holds',
      'emergency_routings',
      'emergency_cases',
      'triage_assessments',
      'consultations',
      'patient_arrivals',
      'opd_tokens',
      'appointments',
      'opd_slots',
      'resource_status_history',
      'hospital_resources',
      'bed_status_history',
      'beds',
      'reception_profiles',
      'nurse_profiles',
      'doctor_profiles',
      'departments',
      'location_requests',
      'geocoding_cache',
      'patient_profiles',
      'demo_sessions',
      'users',
      'hospitals',
      'cities',
      'districts',
      'states',
      'analytics_snapshots',
      'system_events',
    ];
    for (const table of tables) {
      await this.$executeRawUnsafe(`TRUNCATE TABLE "${table}" CASCADE`);
    }
  }
}
