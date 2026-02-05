import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/context/ToastContext'
import client from '@/api/client'

interface UserProfile {
  id: number
  username: string
  full_name: string
  email: string
  avatar?: string
  created_at?: string
}

export default function ProfilePage() {
  const navigate = useNavigate()
  const { user, setUser } = useAuthStore()
  const { addToast } = useToast()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
  })
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) {
      navigate('/auth/login')
    } else {
      loadProfile()
    }
  }, [user, navigate])

  const loadProfile = async () => {
    try {
      setLoading(true)
      const response = await client.get('/v1/users/me')
      setProfile(response.data)
      setFormData({
        full_name: response.data.full_name,
        email: response.data.email,
      })
    } catch (err) {
      addToast('加载个人资料失败', 'error')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      setSaving(true)
      const response = await client.put('/v1/users/me', {
        full_name: formData.full_name,
        email: formData.email,
      })
      setProfile(response.data)
      setUser(response.data)
      addToast('个人资料已更新', 'success')
      setTimeout(() => navigate('/dashboard'), 2000)
    } catch (err: any) {
      const errMsg = err.response?.data?.detail || '更新失败'
      setError(errMsg)
      addToast(errMsg, 'error')
    } finally {
      setSaving(false)
    }
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </div>
    )
  }

  if (!profile) return null

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
        <h2 className="text-3xl font-bold text-gray-900 mb-8">个人资料</h2>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border-2 border-red-300 text-red-700 rounded-xl font-medium">
            {error}
          </div>
        )}

        {/* Avatar */}
        <div className="flex justify-center mb-8">
          <div className="w-24 h-24 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-full flex items-center justify-center">
            <span className="text-4xl font-bold text-white">{getInitials(profile.full_name)}</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-bold text-gray-800 mb-2">用户名</label>
            <div className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl bg-gray-50 text-gray-600 font-semibold">
              {profile.username}
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-800 mb-2">姓名</label>
            <input
              type="text"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
              placeholder="输入您的姓名"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-800 mb-2">邮箱</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
              placeholder="输入您的邮箱"
              required
            />
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="submit"
              disabled={saving}
              className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 px-4 rounded-xl hover:shadow-lg transform hover:scale-105 transition font-bold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? '保存中...' : '保存更改'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="flex-1 bg-gray-200 text-gray-700 py-3 px-4 rounded-xl hover:bg-gray-300 hover:shadow-lg transition font-bold"
            >
              返回
            </button>
          </div>
        </form>

        {/* User Info */}
        <div className="mt-8 pt-8 border-t-2 border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4">账户信息</h3>
          <div className="grid grid-cols-1 gap-4">
            <div className="bg-gradient-to-br from-indigo-50 to-purple-50 p-4 rounded-xl border border-indigo-200">
              <dt className="text-sm font-bold text-indigo-700 uppercase">用户ID</dt>
              <dd className="text-sm font-semibold text-gray-900 mt-2">{profile.id}</dd>
            </div>
            {profile.created_at && (
              <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-4 rounded-xl border border-blue-200">
                <dt className="text-sm font-bold text-blue-700 uppercase">注册时间</dt>
                <dd className="text-sm font-semibold text-gray-900 mt-2">
                  {new Date(profile.created_at).toLocaleDateString('zh-CN')}
                </dd>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
