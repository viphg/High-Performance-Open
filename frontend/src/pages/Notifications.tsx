import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { notificationAPI } from '@/api/notifications'
import type { Notification } from '@/types'

export default function NotificationsPage() {
  const navigate = useNavigate()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'all' | 'unread'>('all')

  const fetchNotifications = async () => {
    try {
      setLoading(true)
      const response = await notificationAPI.getNotifications({
        unread_only: activeTab === 'unread',
        limit: 50
      })
      setNotifications(response.data.notifications)
    } catch (error) {
      console.error('获取通知失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkAsRead = async (notification: Notification) => {
    if (notification.is_read) return
    try {
      await notificationAPI.markAsRead(notification.id)
      fetchNotifications()
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      await notificationAPI.markAllAsRead()
      fetchNotifications()
    } catch (error) {
      console.error('标记全部已读失败:', error)
    }
  }

  const handleDelete = async (notificationId: number) => {
    if (!confirm('确定要删除这条通知吗？')) return
    try {
      await notificationAPI.deleteNotification(notificationId)
      fetchNotifications()
    } catch (error) {
      console.error('删除通知失败:', error)
    }
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'task_due_soon':
      case 'task_overdue':
        return '⏰'
      case 'task_completed':
        return '✅'
      case 'goal_progress':
      case 'goal_completed':
        return '📈'
      case 'achievement_unlocked':
        return '🏆'
      case 'welcome':
        return '👋'
      case 'daily_digest':
        return '📊'
      default:
        return '🔔'
    }
  }

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  useEffect(() => {
    fetchNotifications()
  }, [activeTab])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">加载中...</div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">通知中心</h1>
        <button
          onClick={() => navigate('/settings/notifications')}
          className="text-indigo-600 hover:text-indigo-700"
        >
          通知设置 ⚙️
        </button>
      </div>

      {/* 标签页 */}
      <div className="flex space-x-4 mb-6 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('all')}
          className={`pb-3 px-2 font-medium ${
            activeTab === 'all'
              ? 'text-indigo-600 border-b-2 border-indigo-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          全部通知
        </button>
        <button
          onClick={() => setActiveTab('unread')}
          className={`pb-3 px-2 font-medium ${
            activeTab === 'unread'
              ? 'text-indigo-600 border-b-2 border-indigo-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          未读通知
        </button>
        {activeTab === 'unread' && notifications.length > 0 && (
          <button
            onClick={handleMarkAllAsRead}
            className="pb-3 px-2 text-sm text-indigo-600 hover:text-indigo-700 ml-auto"
          >
            全部已读
          </button>
        )}
      </div>

      {/* 通知列表 */}
      <div className="space-y-4">
        {notifications.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔔</div>
            <p className="text-gray-500">暂无通知</p>
          </div>
        ) : (
          notifications.map((notification) => (
            <div
              key={notification.id}
              className={`bg-white rounded-xl shadow-sm border p-6 ${
                !notification.is_read ? 'border-indigo-200 bg-indigo-50' : 'border-gray-100'
              }`}
            >
              <div className="flex items-start space-x-4">
                <span className="text-3xl">{getIcon(notification.type)}</span>
                <div className="flex-1">
                  <div className="flex justify-between items-start">
                    <h3 className="font-bold text-gray-900">{notification.title}</h3>
                    <span className="text-sm text-gray-400">
                      {formatTime(notification.created_at)}
                    </span>
                  </div>
                  <p className="text-gray-600 mt-2">{notification.content}</p>
                  <div className="flex space-x-4 mt-4">
                    {!notification.is_read && (
                      <button
                        onClick={() => handleMarkAsRead(notification)}
                        className="text-sm text-indigo-600 hover:text-indigo-700"
                      >
                        标记为已读
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(notification.id)}
                      className="text-sm text-red-600 hover:text-red-700"
                    >
                      删除
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
