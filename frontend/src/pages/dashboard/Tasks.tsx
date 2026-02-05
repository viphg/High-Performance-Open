import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/context/ToastContext'
import { tasksAPI } from '@/api/tasks'
import { goalsAPI } from '@/api/goals'
import type { Task, Goal } from '@/types'

export default function TasksPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { addToast } = useToast()
  const [tasks, setTasks] = useState<Task[]>([])
  const [goals, setGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    goal_id: '',
    priority: 0,
    due_date: '',
    estimated_hours: '',
  })
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) {
      navigate('/auth/login')
    } else {
      loadData()
    }
  }, [user, navigate])

  const loadData = async () => {
    try {
      setLoading(true)
      const [tasksRes, goalsRes] = await Promise.all([
        tasksAPI.list(),
        goalsAPI.list(),
      ])
      setTasks(tasksRes.data)
      setGoals(goalsRes.data)
    } catch (err) {
      addToast('加载数据失败', 'error')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.title.trim()) {
      setError('任务标题不能为空')
      return
    }

    try {
      await tasksAPI.create({
        title: formData.title,
        description: formData.description || undefined,
        goal_id: formData.goal_id ? Number(formData.goal_id) : undefined,
        priority: formData.priority,
        due_date: formData.due_date ? new Date(formData.due_date).toISOString() : undefined,
        estimated_hours: formData.estimated_hours ? Number(formData.estimated_hours) : undefined,
      })

      setFormData({
        title: '',
        description: '',
        goal_id: '',
        priority: 0,
        due_date: '',
        estimated_hours: '',
      })
      setShowForm(false)
      addToast('任务创建成功，目标进度已同步更新', 'success')
      await loadData()
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
      await tasksAPI.delete(id)
      addToast('任务删除成功，目标进度已同步更新', 'success')
      await loadData()
    } catch (err) {
      addToast('删除失败', 'error')
    }
  }

  const handleStatusChange = async (id: number, newStatus: string) => {
    try {
      await tasksAPI.update(id, { status: newStatus })
      addToast('任务状态更新成功，目标进度已同步更新', 'success')
      await loadData()
    } catch (err) {
      addToast('更新失败', 'error')
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

  const getGoalTitle = (goalId?: number) => {
    if (!goalId) return '无关联目标'
    return goals.find((g) => g.id === goalId)?.title || '已删除的目标'
  }

  const filteredTasks = filterStatus === 'all'
    ? tasks
    : tasks.filter((t) => t.status === filterStatus)

  return (
    <>
      <div className="mb-8 flex justify-between items-center">
        <h2 className="text-3xl font-bold text-gray-900">我的任务</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:shadow-lg transform hover:scale-105 transition font-medium"
        >
          {showForm ? '取消' : '+ 新建任务'}
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
              <label className="block text-sm font-bold text-gray-800 mb-2">任务名称 *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
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
                <label className="block text-sm font-bold text-gray-800 mb-2">关联目标</label>
                <select
                  value={formData.goal_id}
                  onChange={(e) => setFormData({ ...formData, goal_id: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
                >
                  <option value="">无关联</option>
                  {goals.map((goal) => (
                    <option key={goal.id} value={goal.id}>
                      {goal.title}
                    </option>
                  ))}
                </select>
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

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-bold text-gray-800 mb-2">截止日期</label>
                <input
                  type="date"
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-800 mb-2">预计耗时 (小时)</label>
                <input
                  type="number"
                  value={formData.estimated_hours}
                  onChange={(e) => setFormData({ ...formData, estimated_hours: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
                  min="0"
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 rounded-xl hover:shadow-lg transform hover:scale-105 transition font-bold text-lg"
            >
              创建任务
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

      {/* Tasks List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        </div>
      ) : filteredTasks.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-100">
          <p className="text-gray-500 text-lg">还没有任务，创建一个吧！</p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-100">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gradient-to-r from-gray-50 to-gray-100 border-b-2 border-gray-300">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-bold text-gray-800 uppercase tracking-wider">
                  任务
                </th>
                <th className="px-6 py-4 text-left text-sm font-bold text-gray-800 uppercase tracking-wider">
                  目标
                </th>
                <th className="px-6 py-4 text-left text-sm font-bold text-gray-800 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-6 py-4 text-left text-sm font-bold text-gray-800 uppercase tracking-wider">
                  截止日期
                </th>
                <th className="px-6 py-4 text-left text-sm font-bold text-gray-800 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredTasks.map((task) => {
                const { color } = getStatusBadge(task.status)
                return (
                  <tr key={task.id} className="hover:bg-gradient-to-r hover:from-indigo-50 hover:to-purple-50 transition">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <p className="text-sm font-bold text-gray-900">{task.title}</p>
                        {task.description && (
                          <p className="text-sm text-gray-600 line-clamp-1">{task.description}</p>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <p className="text-sm text-gray-900 font-semibold">{getGoalTitle(task.goal_id)}</p>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <select
                        value={task.status}
                        onChange={(e) => handleStatusChange(task.id, e.target.value)}
                        className={`px-3 py-1 rounded-full text-xs font-bold ${color} border-none cursor-pointer bg-opacity-100 hover:shadow-md transition`}
                      >
                        <option value="not_started">未开始</option>
                        <option value="in_progress">进行中</option>
                        <option value="completed">已完成</option>
                        <option value="cancelled">已取消</option>
                      </select>
                    </td>
                     <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-700">
                       {task.due_date ? new Date(task.due_date).toLocaleDateString('zh-CN') : '-'}
                     </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold">
                      <div className="flex space-x-3">
                        <button
                          onClick={() => navigate(`/tasks/${task.id}`)}
                          className="text-indigo-600 hover:text-indigo-900 hover:bg-indigo-50 px-3 py-1 rounded-lg transition"
                        >
                          编辑
                        </button>
                        <button
                          onClick={() => handleDelete(task.id)}
                          className="text-red-600 hover:text-red-900 hover:bg-red-50 px-3 py-1 rounded-lg transition"
                        >
                          删除
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
