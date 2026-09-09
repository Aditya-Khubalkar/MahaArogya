import { Controller, Post, Get, Body, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { AIConversationService } from './ai-conversation.service';
import { Permissions } from '../common/decorators/auth.decorators';
import { PERMISSIONS } from '../common/constants/permissions.constants';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import type { CurrentUserData } from '../common/decorators/current-user.decorator';
import { IsEnum, IsOptional, IsString } from 'class-validator';
import { AIConversationMode } from '@prisma/client';

class StartConversationDto {
  @IsOptional()
  @IsEnum(AIConversationMode)
  mode?: AIConversationMode;

  @IsOptional()
  @IsString()
  language?: string;
}

class SendMessageDto {
  @IsString()
  text: string;
}

@ApiTags('ai')
@ApiBearerAuth()
@Controller('ai')
export class AIConversationController {
  constructor(private readonly aiConversationService: AIConversationService) {}

  @Post('conversations')
  @Permissions(PERMISSIONS.PATIENT_USE_AI)
  @ApiOperation({ summary: 'Start a new AI health conversation' })
  startConversation(
    @Body() dto: StartConversationDto,
    @CurrentUser() user: CurrentUserData,
  ) {
    // Patients have a dedicated patient profile linked to their userId
    return this.aiConversationService.startConversation(
      user.userId,
      dto.mode || 'TEXT',
      dto.language || 'auto',
    );
  }

  @Post('conversations/:id/messages')
  @Permissions(PERMISSIONS.PATIENT_USE_AI)
  @ApiOperation({ summary: 'Send a message in a conversation' })
  sendMessage(
    @Param('id') conversationId: string,
    @Body() dto: SendMessageDto,
    @CurrentUser() user: CurrentUserData,
  ) {
    return this.aiConversationService.sendMessage(
      conversationId,
      user.userId,
      dto.text,
    );
  }

  @Get('conversations')
  @Permissions(PERMISSIONS.PATIENT_USE_AI)
  @ApiOperation({ summary: 'List my conversations' })
  getMyConversations(@CurrentUser() user: CurrentUserData) {
    return this.aiConversationService.getPatientConversations(user.userId);
  }

  @Get('conversations/:id')
  @Permissions(PERMISSIONS.PATIENT_USE_AI)
  @ApiOperation({ summary: 'Get a specific conversation with messages' })
  getConversation(
    @Param('id') conversationId: string,
    @CurrentUser() user: CurrentUserData,
  ) {
    return this.aiConversationService.getConversation(
      conversationId,
      user.userId,
    );
  }
}
