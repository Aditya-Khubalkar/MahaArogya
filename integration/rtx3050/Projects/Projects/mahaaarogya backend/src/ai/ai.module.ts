import { Module } from '@nestjs/common';
import { MockAIService } from './mock-ai.service';
import { AIConversationService } from './ai-conversation.service';
import { AIConversationController } from './ai-conversation.controller';
import { AI_SERVICE_TOKEN } from './ai.interface';
import { AuditModule } from '../audit/audit.module';
import { NotificationsModule } from '../notifications/notifications.module';
import { RealtimeModule } from '../realtime/realtime.module';
import { ConfigService } from '@nestjs/config';

@Module({
  imports: [AuditModule, NotificationsModule, RealtimeModule],
  providers: [
    {
      provide: AI_SERVICE_TOKEN,
      useFactory: (config: ConfigService) => {
        // In future: if MOCK_AI=false, inject real AI service
        // For now: always use mock
        return new MockAIService();
      },
      inject: [ConfigService],
    },
    AIConversationService,
  ],
  controllers: [AIConversationController],
  exports: [AIConversationService, AI_SERVICE_TOKEN],
})
export class AIModule {}
