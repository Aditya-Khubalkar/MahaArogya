import {
  Injectable,
  NotFoundException,
  ForbiddenException,
  Inject,
} from '@nestjs/common';
import { PrismaService } from '../database/prisma.service';
import { AuditService } from '../audit/audit.service';
import { NotificationsService } from '../notifications/notifications.service';
import { RealtimeGateway } from '../realtime/realtime.gateway';
import { AI_SERVICE_TOKEN } from './ai.interface';
import type { AIServiceInterface } from './ai.interface';
import { MockAIService } from './mock-ai.service';
import { AIConversationMode, TriageCategory, Prisma } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class AIConversationService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly audit: AuditService,
    private readonly notifications: NotificationsService,
    private readonly realtime: RealtimeGateway,
    @Inject(AI_SERVICE_TOKEN) private readonly aiService: AIServiceInterface,
  ) {}

  private async resolvePatientId(userIdOrPatientId: string): Promise<string> {
    const profile = await this.prisma.patientProfile.findFirst({
      where: { OR: [{ id: userIdOrPatientId }, { userId: userIdOrPatientId }] },
    });
    return profile ? profile.id : userIdOrPatientId;
  }

  async startConversation(
    patientId: string,
    mode: AIConversationMode = 'TEXT',
    language = 'auto',
  ) {
    const resolvedPatientId = await this.resolvePatientId(patientId);
    const isMock = this.aiService instanceof MockAIService;
    const conversation = await this.prisma.aIConversation.create({
      data: {
        id: uuidv4(),
        patientId: resolvedPatientId,
        mode,
        language: language === 'auto' ? 'en' : language,
        status: 'ACTIVE',
        isAIMock: isMock,
      },
    });

    // Initial greeting
    const greetings: Record<string, string> = {
      en: 'Hello! I am MahaArogya AI. Please tell me about your health concern.',
      mr: 'Namaste! Mi MahaArogya AI aahe. Tumcha arogya problem sangaa.',
      hi: 'Namaste! Main MahaArogya AI hoon. Apni takleef bataaiye.',
    };
    const lang = ['en', 'mr', 'hi'].includes(language) ? language : 'en';

    await this.prisma.aIMessage.create({
      data: {
        id: uuidv4(),
        conversationId: conversation.id,
        role: 'ai',
        content: greetings[lang],
        language: lang,
      },
    });

    return conversation;
  }

  async sendMessage(
    conversationId: string,
    patientId: string,
    text: string,
    audioBuffer?: Buffer,
  ) {
    const resolvedPatientId = await this.resolvePatientId(patientId);
    const conversation = await this.prisma.aIConversation.findUnique({
      where: { id: conversationId },
      include: { messages: { orderBy: { createdAt: 'asc' } } },
    });

    if (!conversation) throw new NotFoundException('Conversation not found');
    if (conversation.patientId !== resolvedPatientId)
      throw new ForbiddenException('Access denied');
    if (conversation.status !== 'ACTIVE') {
      throw new ForbiddenException('Conversation is no longer active');
    }

    // Detect language
    const detectedLang = await this.aiService.detectLanguage(text);
    const lang = detectedLang || conversation.language;

    // Get current patient state
    const latestState = await this.prisma.patientStateSnapshot.findFirst({
      where: { conversationId },
      orderBy: { createdAt: 'desc' },
    });
    const currentState = latestState
      ? {
          ...(latestState as unknown as Record<string, unknown>),
          turnNumber: (latestState.turnNumber || 0) + 1,
        }
      : { turnNumber: 1 };

    // Store patient message
    await this.prisma.aIMessage.create({
      data: {
        id: uuidv4(),
        conversationId,
        role: 'patient',
        content: text,
        language: lang,
        detectedLanguage: detectedLang,
      },
    });

    // Get AI response
    const conversationHistory = conversation.messages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    const aiResponse = await this.aiService.generateResponse(
      text,
      currentState,
      lang,
    );

    // Store AI message
    const aiMessage = await this.prisma.aIMessage.create({
      data: {
        id: uuidv4(),
        conversationId,
        role: 'ai',
        content: aiResponse.text,
        language: lang,
        metadata: aiResponse.extractedInfo
          ? (aiResponse.extractedInfo as unknown as Prisma.InputJsonValue)
          : undefined,
      },
    });

    // Update patient state
    const turnNumber = currentState.turnNumber || 1;
    const newState = {
      ...currentState,
      ...(aiResponse.stateUpdate || {}),
      turnNumber,
    };
    if (aiResponse.extractedInfo?.symptoms) {
      newState.symptoms =
        aiResponse.stateUpdate?.symptoms || aiResponse.extractedInfo.symptoms;
    }

    await this.prisma.patientStateSnapshot.create({
      data: {
        id: uuidv4(),
        conversationId,
        turnNumber,
        language: lang,
        symptoms: (newState.symptoms as string[])
          ? { symptoms: newState.symptoms }
          : undefined,
        duration: (newState.duration as string) || undefined,
        severity: (newState.severity as string) || undefined,
        safetySignals: (newState.safetySignals as string[])
          ? { signals: newState.safetySignals }
          : undefined,
        triageCategory: aiResponse.suggestedTriage?.category,
        triageConfidence: aiResponse.suggestedTriage?.confidence || undefined,
      },
    });

    // Handle triage completion
    if (aiResponse.isComplete && aiResponse.suggestedTriage) {
      const triage = aiResponse.suggestedTriage;

      await this.prisma.triageAssessment.create({
        data: {
          id: uuidv4(),
          patientId: resolvedPatientId,
          conversationId,
          category: triage.category,
          confidence: triage.confidence,
          symptoms: { symptoms: (newState.symptoms as string[]) || [] },
          primarySymptom:
            ((newState.symptoms as string[]) || [])[0] || undefined,
          recommendedDepartment: triage.recommendedDepartment,
          safetySignals: { signals: triage.safetySignals },
          isAIMock: triage.isMock,
          modelVersion: triage.modelVersion,
        },
      });

      // Mark conversation complete
      await this.prisma.aIConversation.update({
        where: { id: conversationId },
        data: {
          status: 'TRIAGED',
          triageCategory: triage.category,
          completedAt: new Date(),
          language: lang,
        },
      });

      // Emit realtime event
      this.realtime.emitToUser(resolvedPatientId, 'triage.completed', {
        conversationId,
        category: triage.category,
        recommendedDepartment: triage.recommendedDepartment,
      });
    } else {
      // Update language if detected
      await this.prisma.aIConversation.update({
        where: { id: conversationId },
        data: { language: lang },
      });
    }

    return {
      messageId: aiMessage.id,
      text: aiResponse.text,
      isComplete: aiResponse.isComplete,
      triage: aiResponse.suggestedTriage,
      extractedInfo: aiResponse.extractedInfo,
      language: lang,
    };
  }

  async getConversation(conversationId: string, patientId: string) {
    const resolvedPatientId = await this.resolvePatientId(patientId);
    const conversation = await this.prisma.aIConversation.findUnique({
      where: { id: conversationId },
      include: {
        messages: { orderBy: { createdAt: 'asc' } },
        triageAssessments: { take: 1, orderBy: { createdAt: 'desc' } },
      },
    });
    if (!conversation) throw new NotFoundException('Conversation not found');
    if (conversation.patientId !== resolvedPatientId)
      throw new ForbiddenException('Access denied');
    return conversation;
  }

  async getPatientConversations(patientId: string) {
    const resolvedPatientId = await this.resolvePatientId(patientId);
    return this.prisma.aIConversation.findMany({
      where: { patientId: resolvedPatientId },
      orderBy: { createdAt: 'desc' },
      include: {
        messages: { take: 1, orderBy: { createdAt: 'desc' } },
        triageAssessments: { take: 1, orderBy: { createdAt: 'desc' } },
      },
    });
  }
}
