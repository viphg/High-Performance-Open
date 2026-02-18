import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { adminAPI, type AdminStats, type UserListResponse } from '@/api/admin'


export default function AdminDashboard() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [users, setUsers] = useState<UserListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    // 检查是否是管理员
    if (!user?.is_admin) {
      navigate('/dashboard')
      return
    }

    fetchData()
  }, [user, navigate])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [statsRes, usersRes] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.getUsers({ limit: 10 })
      ])
      setStats(statsRes.data)
      setUsers(usersRes.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '获取数据失败')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">加载中...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">管理员控制台</h1>
        <p className="text-gray-500 mt-1">系统管理和用户管理</p>
      </div>

      {/* 统计卡片 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="text-sm font-medium text-gray-500">总用户数</div>
            <div className="text-3xl font-bold text-indigo-600 mt-2">{stats.total_users}</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="text-sm font-medium text-gray-500">活跃用户</div>
            <div className="text-3xl font-bold text-green-600 mt-2">{stats.active_users}</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="text-sm font-medium text-gray-500">管理员</div>
            <div className="text-3xl font-bold text-purple-600 mt-2">{stats.admin_users}</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="text-sm font-medium text-gray-500">今日新增</div>
            <div className="text-3xl font-bold text-blue-600 mt-2">{stats.new_users_today}</div>
          </div>
        </div>
      )}

      {/* 最近用户 */}
      {users && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
            <h2 className="text-xl font-bold text-gray-900">最近注册用户</h2>
            <button
              onClick={() => navigate('/admin/users')}
              className="text-indigo-600 hover:text-indigo-700 font-medium"
            >
              查看全部 →
            </button>
          </div>
          <div className="divide-y divide-gray-100">
            {users.users.map((u) => (
              <div key={u.id} className="px-6 py-4 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold">
                    {u.username.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{u.username}</div>
                    <div className="text-sm text-gray-500">{u.email}</div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {u.is_admin && (
                    <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded">
                      管理员
                    </span>
                  )}
                  <span className={`px-2 py-1 text-xs font-medium rounded ${
                    u.is_active 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {u.is_active ? '活跃' : '已禁用'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
