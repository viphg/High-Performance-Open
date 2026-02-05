import client from './client'

export const insightsAPI = {
  // 获取进度趋势
  getProgressTrends: (days = 30) =>
    client.get(`/insights/progress-trends?days=${days}`),

  // 获取生产力指标
  getProductivityMetrics: () =>
    client.get('/insights/productivity-metrics'),

  // 获取时间管理统计
  getTimeTracking: (days = 30) =>
    client.get(`/insights/time-tracking?days=${days}`),

  // 获取目标完成模式
  getGoalCompletionPatterns: () =>
    client.get('/insights/goal-completion-patterns'),

  // 获取时间效率指标
  getTimeEfficiency: () =>
    client.get('/insights/time-efficiency'),

  // 获取通知列表
  getNotifications: (unreadOnly = false, limit = 20) =>
    client.get(`/notifications?unread_only=${unreadOnly}&limit=${limit}`),

  // 标记通知为已读
  markAsRead: (notificationId: number) =>
    client.patch(`/notifications/${notificationId}/read`),

  // 获取每日任务连续
  getDailyTaskStreak: () =>
    client.get('/streak/daily-tasks'),

  // 获取智能提醒
  getSmartReminders: () =>
    client.get('/insights/smart-reminders'),

  // 检查成就
  checkAchievements: () =>
    client.post('/achievements/check'),

  // 清理过期通知
  cleanupNotifications: () =>
    client.delete('/notifications/cleanup'),
}