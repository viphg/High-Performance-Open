import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { notificationAPI } from '@/api/notifications'
import type { Notification } from '@/types'

export default function NotificationBell() {
  const navigate = useNavigate()
  const [isOpen, setIsOpen] = useState(false)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // 获取通知列表
  const fetchNotifications = async () => {
    try {
      setLoading(true)
      const response = await notificationAPI.getNotifications({ limit: 10 })
      setNotifications(response.data.notifications)
      setUnreadCount(response.data.unread_count)
    } catch (error) {
      console.error('获取通知失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 获取未读数量
  const fetchUnreadCount = async () => {
    try {
      const response = await notificationAPI.getUnreadCount()
      setUnreadCount(response.data.unread_count)
    } catch (error) {
      console.error('获取未读数量失败:', error)
    }
  }

  // 标记为已读
  const handleMarkAsRead = async (notification: Notification, e: React.MouseEvent) => {
    e.stopPropagation()
    if (notification.is_read) return

    try {
      await notificationAPI.markAsRead(notification.id)
      fetchNotifications()
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }

  // 标记全部已读
  const handleMarkAllAsRead = async () => {
    try {
      await notificationAPI.markAllAsRead()
      fetchNotifications()
    } catch (error) {
      console.error('标记全部已读失败:', error)
    }
  }

  // 点击通知
  const handleNotificationClick = (notification: Notification) => {
    // 标记为已读
    if (!notification.is_read) {
      notificationAPI.markAsRead(notification.id)
    }

    // 跳转到相关页面
    if (notification.related_type && notification.related_id) {
      switch (notification.related_type) {
        case 'task':
          navigate(`/tasks/${notification.related_id}`)
          break
        case 'goal':
          navigate(`/goals/${notification.related_id}`)
          break
      }
    }

    setIsOpen(false)
  }

  // 获取图标
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

  // 格式化时间
  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    
    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`
    return date.toLocaleDateString('zh-CN')
  }

  // 初始加载和定时刷新
  useEffect(() => {
    fetchNotifications()
    fetchUnreadCount()

    // 每30秒刷新一次未读数量
    const interval = setInterval(() => {
      fetchUnreadCount()
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  // 点击外部关闭
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="relative" ref={dropdownRef}>
      {/* 铃铛按钮 */}
      <button
        onClick={() => {
          setIsOpen(!isOpen)
          if (!isOpen) fetchNotifications()
        }}
        className="relative p-2 text-gray-600 hover:text-indigo-600 transition"
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>
        
        {/* 未读数量徽章 */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* 下拉菜单 */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-lg border border-gray-100 z-50">
          {/* 头部 */}
          <div className="flex justify-between items-center px-4 py-3 border-b border-gray-100">
            <h3 className="font-bold text-gray-900">通知</h3>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllAsRead}
                className="text-sm text-indigo-600 hover:text-indigo-700"
              >
                全部已读
              </button>
            )}
          </div>

          {/* 通知列表 */}
          <div className="max-h-96 overflow-y-auto">
            {loading ? (
              <div className="px-4 py-8 text-center text-gray-500">
                加载中...
              </div>
            ) : notifications.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-500">
                <div className="text-4xl mb-2">🔔</div>
                <p>暂无通知</p>
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  onClick={() => handleNotificationClick(notification)}
                  className={`px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-50 last:border-b-0 ${
                    !notification.is_read ? 'bg-indigo-50' : ''
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">{getIcon(notification.type)}</span>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 text-sm">
                        {notification.title}
                      </p>
                      <p className="text-gray-600 text-sm mt-1 line-clamp-2">
                        {notification.content}
                      </p>
                      <div className="flex justify-between items-center mt-2">
                        <span className="text-xs text-gray-400">
                          {formatTime(notification.created_at)}
                        </span>
                        {!notification.is_read && (
                          <button
                            onClick={(e) => handleMarkAsRead(notification, e)}
                            className="text-xs text-indigo-600 hover:text-indigo-700"
                          >
                            标记已读
                          </button>
                        )}
                      </div>
                    </div>
                    {!notification.is_read && (
                      <span className="w-2 h-2 bg-indigo-500 rounded-full flex-shrink-0 mt-1"></span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* 底部 */}
          <div className="px-4 py-3 border-t border-gray-100 text-center">
            <button
              onClick={() => {
                navigate('/notifications')
                setIsOpen(false)
              }}
              className="text-sm text-gray-600 hover:text-indigo-600"
            >
              查看全部通知
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
