import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { adminAPI, type UserListResponse, type PasswordResetData } from '@/api/admin'
import type { User } from '@/types'

// 编辑用户模态框组件
function EditUserModal({
  user,
  isOpen,
  onClose,
  onSave
}: {
  user: User | null
  isOpen: boolean
  onClose: () => void
  onSave: (data: { email: string; full_name: string }) => void
}) {
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')

  useEffect(() => {
    if (user) {
      setEmail(user.email)
      setFullName(user.full_name || '')
    }
  }, [user])

  if (!isOpen || !user) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4">
        <h2 className="text-xl font-bold text-gray-900 mb-4">编辑用户 - {user.username}</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">全名</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>
        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            取消
          </button>
          <button
            onClick={() => onSave({ email, full_name: fullName })}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  )
}

// 重置密码模态框组件
function ResetPasswordModal({
  user,
  isOpen,
  onClose,
  onReset
}: {
  user: User | null
  isOpen: boolean
  onClose: () => void
  onReset: (data: PasswordResetData) => void
}) {
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      setNewPassword('')
      setConfirmPassword('')
      setError('')
    }
  }, [isOpen])

  const handleSubmit = () => {
    if (newPassword.length < 6) {
      setError('密码长度至少为6位')
      return
    }
    if (newPassword !== confirmPassword) {
      setError('两次输入的密码不一致')
      return
    }
    onReset({ new_password: newPassword, confirm_password: confirmPassword })
  }

  if (!isOpen || !user) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4">
        <h2 className="text-xl font-bold text-gray-900 mb-4">重置密码 - {user.username}</h2>
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">新密码</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="输入新密码"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">确认密码</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="再次输入新密码"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>
        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            取消
          </button>
          <button
            onClick={handleSubmit}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
          >
            重置密码
          </button>
        </div>
      </div>
    </div>
  )
}

export default function UserManagement() {
  const navigate = useNavigate()
  const { user: currentUser } = useAuthStore()
  const [users, setUsers] = useState<UserListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterActive, setFilterActive] = useState<boolean | undefined>(undefined)
  const [page, setPage] = useState(0)
  const limit = 10

  // 模态框状态
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [resettingUser, setResettingUser] = useState<User | null>(null)

  useEffect(() => {
    if (!currentUser?.is_admin) {
      navigate('/dashboard')
      return
    }
    fetchUsers()
  }, [currentUser, navigate, page, filterActive])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const response = await adminAPI.getUsers({
        skip: page * limit,
        limit,
        is_active: filterActive,
        search: searchTerm || undefined
      })
      setUsers(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '获取用户列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    setPage(0)
    fetchUsers()
  }

  const handleToggleActive = async (user: User) => {
    try {
      if (user.is_active) {
        await adminAPI.deactivateUser(user.id)
      } else {
        await adminAPI.activateUser(user.id)
      }
      fetchUsers()
    } catch (err: any) {
      alert(err.response?.data?.detail || '操作失败')
    }
  }

  const handleToggleAdmin = async (user: User) => {
    if (user.id === currentUser?.id) {
      alert('不能修改自己的管理员权限')
      return
    }
    try {
      await adminAPI.setAdmin(user.id, !user.is_admin)
      fetchUsers()
    } catch (err: any) {
      alert(err.response?.data?.detail || '操作失败')
    }
  }

  const handleDelete = async (user: User) => {
    if (user.id === currentUser?.id) {
      alert('不能删除自己的账户')
      return
    }
    if (!confirm(`确定要删除用户 ${user.username} 吗？`)) {
      return
    }
    try {
      await adminAPI.deleteUser(user.id)
      fetchUsers()
    } catch (err: any) {
      alert(err.response?.data?.detail || '删除失败')
    }
  }

  const handleEditSave = async (data: { email: string; full_name: string }) => {
    if (!editingUser) return
    try {
      await adminAPI.updateUser(editingUser.id, {
        email: data.email,
        full_name: data.full_name
      })
      setEditingUser(null)
      fetchUsers()
    } catch (err: any) {
      alert(err.response?.data?.detail || '更新失败')
    }
  }

  const handlePasswordReset = async (data: PasswordResetData) => {
    if (!resettingUser) return
    try {
      await adminAPI.resetPassword(resettingUser.id, data)
      setResettingUser(null)
      alert('密码重置成功')
    } catch (err: any) {
      alert(err.response?.data?.detail || '密码重置失败')
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
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">用户管理</h1>
          <p className="text-gray-500 mt-1">管理系统所有用户</p>
        </div>
        <button
          onClick={() => navigate('/admin')}
          className="text-gray-600 hover:text-gray-800"
        >
          ← 返回控制台
        </button>
      </div>

      {/* 筛选和搜索 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex flex-wrap gap-4">
        <div className="flex-1 min-w-[200px]">
          <input
            type="text"
            placeholder="搜索用户名或邮箱..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        <select
          value={filterActive === undefined ? '' : filterActive.toString()}
          onChange={(e) => {
            const value = e.target.value
            setFilterActive(value === '' ? undefined : value === 'true')
            setPage(0)
          }}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">所有状态</option>
          <option value="true">活跃用户</option>
          <option value="false">已禁用</option>
        </select>
        <button
          onClick={handleSearch}
          className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          搜索
        </button>
      </div>

      {/* 用户列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  用户
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  角色
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {users?.users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold mr-3">
                        {user.username.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{user.username}</div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? '活跃' : '已禁用'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {user.is_admin ? (
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                        管理员
                      </span>
                    ) : (
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                        普通用户
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => setEditingUser(user)}
                        className="text-sm font-medium text-blue-600 hover:text-blue-700"
                      >
                        编辑
                      </button>
                      <button
                        onClick={() => setResettingUser(user)}
                        disabled={user.id === currentUser?.id}
                        className="text-sm font-medium text-orange-600 hover:text-orange-700 disabled:text-gray-400"
                      >
                        重置密码
                      </button>
                      <button
                        onClick={() => handleToggleActive(user)}
                        disabled={user.id === currentUser?.id}
                        className={`text-sm font-medium ${
                          user.is_active
                            ? 'text-red-600 hover:text-red-700'
                            : 'text-green-600 hover:text-green-700'
                        } disabled:text-gray-400`}
                      >
                        {user.is_active ? '禁用' : '激活'}
                      </button>
                      <button
                        onClick={() => handleToggleAdmin(user)}
                        disabled={user.id === currentUser?.id}
                        className={`text-sm font-medium ${
                          user.is_admin
                            ? 'text-purple-600 hover:text-purple-700'
                            : 'text-indigo-600 hover:text-indigo-700'
                        } disabled:text-gray-400`}
                      >
                        {user.is_admin ? '取消管理' : '设为管理'}
                      </button>
                      <button
                        onClick={() => handleDelete(user)}
                        disabled={user.id === currentUser?.id}
                        className="text-sm font-medium text-red-600 hover:text-red-700 disabled:text-gray-400"
                      >
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* 分页 */}
        {users && (
          <div className="px-6 py-4 border-t border-gray-100 flex justify-between items-center">
            <div className="text-sm text-gray-500">
              共 {users.total} 条记录
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setPage(Math.max(0, page - 1))}
                disabled={page === 0}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                上一页
              </button>
              <span className="px-4 py-2 text-gray-600">
                第 {page + 1} 页
              </span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={!users.users.length || users.users.length < limit}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                下一页
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 编辑用户模态框 */}
      <EditUserModal
        user={editingUser}
        isOpen={!!editingUser}
        onClose={() => setEditingUser(null)}
        onSave={handleEditSave}
      />

      {/* 重置密码模态框 */}
      <ResetPasswordModal
        user={resettingUser}
        isOpen={!!resettingUser}
        onClose={() => setResettingUser(null)}
        onReset={handlePasswordReset}
      />
    </div>
  )
}
