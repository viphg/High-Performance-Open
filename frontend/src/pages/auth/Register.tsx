import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { authAPI } from '@/api/auth'
import type { RegisterRequest } from '@/types'

export default function RegisterPage() {
  const navigate = useNavigate()
  const { setToken, setUser } = useAuthStore()
  const [formData, setFormData] = useState<RegisterRequest>({
    email: '',
    username: '',
    password: '',
    full_name: '',
  })
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (formData.password !== confirmPassword) {
      setError('两次输入的密码不一致')
      return
    }

    if (formData.password.length < 8) {
      setError('密码长度至少8个字符')
      return
    }

    setIsLoading(true)

    try {
      const response = await authAPI.register(formData)
      const user = response.data

      const loginResponse = await authAPI.login({
        username: formData.username,
        password: formData.password,
      })

      const { access_token } = loginResponse.data

      setToken(access_token)
      setUser(user)

      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || '注册失败')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md border border-gray-100">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            High-Performance
          </h1>
          <p className="text-gray-500 mt-2 text-sm">加入成长社区</p>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border-2 border-red-300 text-red-700 rounded-xl text-sm font-medium">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-bold text-gray-800 mb-2">
              邮箱 *
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
              placeholder="输入邮箱"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-800 mb-2">
              用户名 *
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              minLength={3}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
              placeholder="至少3个字符"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-800 mb-2">
              密码 *
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              minLength={8}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
              placeholder="至少8个字符"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-800 mb-2">
              确认密码 *
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
              placeholder="再次输入密码"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-800 mb-2">
              姓名 (可选)
            </label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
              placeholder="输入姓名"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 rounded-xl font-bold hover:shadow-lg transform hover:scale-105 transition disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {isLoading ? '注册中...' : '注册'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-500 text-sm">
            已有账户？{' '}
            <Link to="/auth/login" className="text-indigo-600 hover:text-indigo-700 font-bold">
              登录
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
