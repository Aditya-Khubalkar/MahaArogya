import { registerAs } from '@nestjs/config';

export default registerAs('app', () => ({
  port: parseInt(process.env.PORT || '4000', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  apiPrefix: process.env.API_PREFIX || 'api/v1',
  jwtSecret: process.env.JWT_SECRET || 'fallback-secret-change-in-production',
  jwtExpiry: process.env.JWT_EXPIRY || '24h',
  demoMode: process.env.DEMO_MODE === 'true',
  mockAI: process.env.MOCK_AI === 'true',
  mockCCTV: process.env.MOCK_CCTV === 'true',
  logLevel: process.env.LOG_LEVEL || 'info',
  aiServiceEnabled: process.env.AI_SERVICE_ENABLED === 'true',
  aiServiceUrl: process.env.AI_SERVICE_URL || 'http://localhost:8001',
  cctvServiceEnabled: process.env.CCTV_SERVICE_ENABLED === 'true',
  cctvServiceUrl: process.env.CCTV_SERVICE_URL || 'http://localhost:8002',
  redisEnabled: process.env.REDIS_ENABLED === 'true',
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',
  nominatimUrl:
    process.env.NOMINATIM_URL || 'https://nominatim.openstreetmap.org',
  nominatimUserAgent:
    process.env.NOMINATIM_USER_AGENT || 'MahaArogya-Hackathon/1.0',
  corsOrigins: (
    process.env.CORS_ORIGINS || 'http://localhost:4000,http://localhost:5173'
  ).split(','),
  resourceHoldExpiryMinutes: parseInt(
    process.env.RESOURCE_HOLD_EXPIRY_MINUTES || '30',
    10,
  ),
  databaseUrl: process.env.DATABASE_URL,
}));
