import { useState, useEffect } from 'react'
import { notificationAPI } from '@/api/notifications'
import type { NotificationPreference } from '@/types'

export default function NotificationSettings() {
  const [preferences, setPreferences] = useState<NotificationPreference | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchPreferences()
  }, [])

  const fetchPreferences = async () => {
    try {
      const response = await notificationAPI.getPreferences()
      setPreferences(response.data)
    } catch (error) {
      console.error('获取偏好设置失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!preferences) return
    
    try {
      setSaving(true)
      await notificationAPI.updatePreferences({
        task_due_email: preferences.task_due_email,
        task_due_web: preferences.task_due_web,
        task_due_hours_before: preferences.task_due_hours_before,
        goal_progress_email: preferences.goal_progress_email,
        goal_progress_web: preferences.goal_progress_web,
        achievement_email: preferences.achievement_email,
        achievement_web: preferences.achievement_web,
        daily_digest: preferences.daily_digest,
        digest_time: preferences.digest_time,
        digest_email: preferences.digest_email,
        digest_web: preferences.digest_web
      })
      setMessage('设置已保存')
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      setMessage('保存失败')
    } finally {
      setSaving(false)
    }
  }

  const handleChange = (field: keyof NotificationPreference, value: any) => {
    if (!preferences) return
    setPreferences({ ...preferences, [field]: value })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">加载中...</div>
      </div>
    )
  }

  if (!preferences) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        加载设置失败
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">通知设置</h1>
      <p className="text-gray-500 mb-8">自定义您希望接收的通知类型和方式</p>

      {message && (
        <div className={`mb-6 p-4 rounded-lg ${
          message.includes('失败') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
        }`}>
          {message}
        </div>
      )}

      <div className="space-y-8">
        {/* 任务提醒 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">📋 任务提醒</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-700">站内通知</p>
                <p className="text-sm text-gray-500">在网站内接收任务提醒</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.task_due_web}
                  onChange={(e) => handleChange('task_due_web', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-700">邮件通知</p>
                <p className="text-sm text-gray-500">通过邮件接收任务提醒</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.task_due_email}
                  onChange={(e) => handleChange('task_due_email', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>

            <div className="pt-4 border-t border-gray-100">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                提前提醒时间
              </label>
              <select
                value={preferences.task_due_hours_before}
                onChange={(e) => handleChange('task_due_hours_before', parseInt(e.target.value))}
                className="block w-full max-w-xs px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value={1}>1小时前</option>
                <option value={6}>6小时前</option>
                <option value={12}>12小时前</option>
                <option value={24}>24小时前</option>
                <option value={48}>48小时前</option>
              </select>
            </div>
          </div>
        </div>

        {/* 目标进度 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">🎯 目标进度</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-700">站内通知</p>
                <p className="text-sm text-gray-500">目标进度更新时通知</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.goal_progress_web}
                  onChange={(e) => handleChange('goal_progress_web', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-700">邮件通知</p>
                <p className="text-sm text-gray-500">通过邮件接收进度更新</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.goal_progress_email}
                  onChange={(e) => handleChange('goal_progress_email', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* 成就解锁 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">🏆 成就解锁</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-700">站内通知</p>
                <p className="text-sm text-gray-500">解锁成就时显示通知</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.achievement_web}
                  onChange={(e) => handleChange('achievement_web', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-700">邮件通知</p>
                <p className="text-sm text-gray-500">通过邮件接收成就通知</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.achievement_email}
                  onChange={(e) => handleChange('achievement_email', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* 每日摘要 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">📊 每日摘要</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-700">启用每日摘要</p>
                <p className="text-sm text-gray-500">每天接收任务和目标摘要</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.daily_digest}
                  onChange={(e) => handleChange('daily_digest', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>

            {preferences.daily_digest && (
              <>
                <div className="pt-4 border-t border-gray-100">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    发送时间
                  </label>
                  <input
                    type="time"
                    value={preferences.digest_time}
                    onChange={(e) => handleChange('digest_time', e.target.value)}
                    className="block w-full max-w-xs px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div className="pt-4 border-t border-gray-100 space-y-3">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.digest_email}
                      onChange={(e) => handleChange('digest_email', e.target.checked)}
                      className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    />
                    <span className="ml-2 text-gray-700">通过邮件发送</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.digest_web}
                      onChange={(e) => handleChange('digest_web', e.target.checked)}
                      className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    />
                    <span className="ml-2 text-gray-700">站内通知</span>
                  </label>
                </div>
              </>
            )}
          </div>
        </div>

        {/* 保存按钮 */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
          >
            {saving ? '保存中...' : '保存设置'}
          </button>
        </div>
      </div>
    </div>
  )
}
