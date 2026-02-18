import client from './client'
import type { Notification, NotificationPreference } from '@/types'

export interface NotificationListResponse {
  total: number
  unread_count: number
  notifications: Notification[]
}

export interface NotificationCountResponse {
  unread_count: number
}

export const notificationAPI = {
  // 获取通知列表
  getNotifications: (params?: {
    unread_only?: boolean
    limit?: number
    offset?: number
  }) => client.get<NotificationListResponse>('/v1/notifications', { params }),

  // 获取未读通知数量
  getUnreadCount: () =>
    client.get<NotificationCountResponse>('/v1/notifications/count'),

  // 标记通知为已读
  markAsRead: (notificationId: number) =>
    client.post<Notification>(`/v1/notifications/${notificationId}/read`),

  // 标记所有通知为已读
  markAllAsRead: () =>
    client.post('/v1/notifications/read-all'),

  // 删除通知
  deleteNotification: (notificationId: number) =>
    client.delete(`/v1/notifications/${notificationId}`),

  // 获取通知偏好设置
  getPreferences: () =>
    client.get<NotificationPreference>('/v1/notifications/preferences'),

  // 更新通知偏好设置
  updatePreferences: (data: Partial<NotificationPreference>) =>
    client.put<NotificationPreference>('/v1/notifications/preferences', data),
}
