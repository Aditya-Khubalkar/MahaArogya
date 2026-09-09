import { Controller, Get, Patch, Param, Query, Req } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { NotificationsService } from './notifications.service';
import { Permissions } from '../common/decorators/auth.decorators';
import { PERMISSIONS } from '../common/constants/permissions.constants';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import type { CurrentUserData } from '../common/decorators/current-user.decorator';

@ApiTags('notifications')
@ApiBearerAuth()
@Controller('notifications')
export class NotificationsController {
  constructor(private readonly notificationsService: NotificationsService) {}

  @Get()
  @Permissions(PERMISSIONS.PATIENT_VIEW_OWN_NOTIFICATIONS)
  @ApiOperation({ summary: 'Get my notifications' })
  getMyNotifications(
    @CurrentUser() user: CurrentUserData,
    @Query('unreadOnly') unreadOnly?: boolean,
    @Query('page') page?: number,
    @Query('limit') limit?: number,
  ) {
    return this.notificationsService.findForUser(user.userId, {
      unreadOnly,
      page,
      limit,
    });
  }

  @Patch(':id/read')
  @ApiOperation({ summary: 'Mark notification as read' })
  markRead(@Param('id') id: string, @CurrentUser() user: CurrentUserData) {
    return this.notificationsService.markRead(id, user.userId);
  }

  @Patch('read-all')
  @ApiOperation({ summary: 'Mark all notifications as read' })
  markAllRead(@CurrentUser() user: CurrentUserData) {
    return this.notificationsService.markAllRead(user.userId);
  }
}
