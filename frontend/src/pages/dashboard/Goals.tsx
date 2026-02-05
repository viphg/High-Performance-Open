import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/context/ToastContext'
import { goalsAPI } from '@/api/goals'
import type { Goal } from '@/types'

export default function GoalsPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { addToast } = useToast()
  const [goals, setGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    priority: 0,
    target_date: '',
  })
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) {
      navigate('/auth/login')
    } else {
      loadGoals()
    }
  }, [user, navigate])

  const loadGoals = async () => {
    try {
      setLoading(true)
      const response = await goalsAPI.list()
      setGoals(response.data)
    } catch (err) {
      addToast('加载目标失败', 'error')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.title.trim()) {
      setError('目标标题不能为空')
      return
    }

    try {
      await goalsAPI.create({
        title: formData.title,
        description: formData.description || undefined,
        category: formData.category || undefined,
        priority: formData.priority,
        target_date: formData.target_date ? new Date(formData.target_date).toISOString() : undefined,
      })

      setFormData({ title: '', description: '', category: '', priority: 0, target_date: '' })
      setShowForm(false)
      addToast('目标创建成功', 'success')
      await loadGoals()
    } catch (err: any) {
      const errMsg = typeof err.response?.data?.detail === 'string'
        ? err.response.data.detail
        : err.response?.data?.detail?.[0]?.msg || '创建失败'
      setError(errMsg)
      addToast(errMsg, 'error')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await goalsAPI.delete(id)
      addToast('目标删除成功，相关任务的目标关联已自动解除', 'success')
      await loadGoals()
    } catch (err) {
      addToast('删除失败', 'error')
    }
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      not_started: 'bg-gray-100 text-gray-800',
      in_progress: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
    }
    const labels: Record<string, string> = {
      not_started: '未开始',
      in_progress: '进行中',
      completed: '已完成',
      cancelled: '已取消',
    }
    return { color: colors[status] || 'bg-gray-100', label: labels[status] || status }
  }

  const filteredGoals = filterStatus === 'all'
    ? goals
    : goals.filter((g) => g.status === filterStatus)

  return (
    <>
      <div className="mb-8 flex justify-between items-center">
        <h2 className="text-3xl font-bold text-gray-900">我的目标</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:shadow-lg transform hover:scale-105 transition font-medium"
        >
          {showForm ? '取消' : '+ 新建目标'}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8 border border-indigo-100">
          {error && (
            <div className="mb-4 p-4 bg-red-50 border-2 border-red-300 text-red-700 rounded-xl font-medium">
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-bold text-gray-800 mb-2">目标标题 *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
                placeholder="输入目标标题"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-800 mb-2">描述</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition h-24"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-bold text-gray-800 mb-2">分类</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
                  placeholder="工作、学习、健康等"
                />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-800 mb-2">优先级</label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: Number(e.target.value) })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
                >
                  <option value={0}>低</option>
                  <option value={1}>中</option>
                  <option value={2}>高</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-800 mb-2">目标日期</label>
              <input
                type="date"
                value={formData.target_date}
                onChange={(e) => setFormData({ ...formData, target_date: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 rounded-xl hover:shadow-lg transform hover:scale-105 transition font-bold text-lg"
            >
              创建目标
            </button>
          </form>
        </div>
      )}

      {/* Filter Buttons */}
      <div className="mb-6 flex space-x-3">
        <button
          onClick={() => setFilterStatus('all')}
          className={`px-6 py-2 rounded-full font-bold transition ${
            filterStatus === 'all'
              ? 'bg-indigo-600 text-white shadow-lg'
              : 'bg-white text-gray-700 border-2 border-gray-300 hover:border-indigo-600'
          }`}
        >
          全部
        </button>
        <button
          onClick={() => setFilterStatus('in_progress')}
          className={`px-6 py-2 rounded-full font-bold transition ${
            filterStatus === 'in_progress'
              ? 'bg-blue-600 text-white shadow-lg'
              : 'bg-white text-gray-700 border-2 border-gray-300 hover:border-blue-600'
          }`}
        >
          进行中
        </button>
        <button
          onClick={() => setFilterStatus('completed')}
          className={`px-6 py-2 rounded-full font-bold transition ${
            filterStatus === 'completed'
              ? 'bg-green-600 text-white shadow-lg'
              : 'bg-white text-gray-700 border-2 border-gray-300 hover:border-green-600'
          }`}
        >
          已完成
        </button>
      </div>

      {/* Goals List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        </div>
      ) : filteredGoals.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-100">
          <p className="text-gray-500 text-lg">还没有目标，创建一个吧！</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredGoals.map((goal) => {
            const { color, label } = getStatusBadge(goal.status)
            return (
              <div key={goal.id} className="bg-white rounded-2xl shadow-md hover:shadow-xl transition p-6 border border-gray-100">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-bold text-gray-900 flex-1">{goal.title}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${color}`}>
                    {label}
                  </span>
                </div>

                {goal.description && (
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">{goal.description}</p>
                )}

                {goal.category && (
                  <div className="mb-3">
                    <span className="inline-block bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 text-xs font-bold px-3 py-1 rounded-full">
                      {goal.category}
                    </span>
                  </div>
                )}

                <div className="mb-5 p-3 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-700 font-semibold">进度</span>
                    <span className="text-indigo-600 font-bold">{goal.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-300 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-indigo-500 to-purple-600 h-3 rounded-full transition-all"
                      style={{ width: `${goal.progress}%` }}
                    />
                  </div>
                </div>

                {goal.target_date && (
                  <p className="text-sm text-gray-500 mb-4 font-semibold">
                    目标日期：{new Date(goal.target_date).toLocaleDateString()}
                  </p>
                )}

                <div className="flex space-x-3">
                  <button
                    onClick={() => navigate(`/goals/${goal.id}`)}
                    className="flex-1 bg-indigo-100 text-indigo-600 py-2 rounded-xl hover:shadow-md font-bold text-sm transition"
                  >
                    编辑
                  </button>
                  <button
                    onClick={() => handleDelete(goal.id)}
                    className="flex-1 bg-red-100 text-red-600 py-2 rounded-xl hover:shadow-md font-bold text-sm transition"
                  >
                    删除
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </>
  )
}
