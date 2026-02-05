import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/context/ToastContext'
import client from '@/api/client'
import { Task, TaskCreate, Goal } from '@/types'

export default function TaskDetailPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const { user } = useAuthStore()
  const { addToast } = useToast()
  const [task, setTask] = useState<Task | null>(null)
  const [goals, setGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState<TaskCreate>({
    title: '',
    description: '',
    goal_id: undefined,
    priority: 0,
    due_date: '',
    estimated_hours: undefined,
  })

  useEffect(() => {
    if (!user) {
      navigate('/auth/login')
    } else if (id) {
      loadData()
    }
  }, [user, id, navigate])

  const loadData = async () => {
    try {
      setLoading(true)
      const [taskRes, goalsRes] = await Promise.all([
        client.get(`/v1/tasks/${id}`),
        client.get('/v1/goals'),
      ])
      const taskData: Task = taskRes.data
      setTask(taskData)
      setGoals(goalsRes.data)
      setFormData({
        title: taskData.title,
        description: taskData.description,
        goal_id: taskData.goal_id,
        priority: taskData.priority,
        due_date: taskData.due_date,
        estimated_hours: taskData.estimated_hours,
      })
    } catch (err) {
      setError('加载任务失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]:
        name === 'priority' || name === 'goal_id' ? (value ? parseInt(value) : name === 'goal_id' ? undefined : 0) : value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!task) return

    try {
      setError('')
      await client.put(`/v1/tasks/${task.id}`, formData)
      addToast('任务已更新', 'success')
      navigate('/tasks')
    } catch (err) {
      const errMsg = '更新失败，请重试'
      setError(errMsg)
      addToast(errMsg, 'error')
      console.error(err)
    }
  }

  const handleDelete = async () => {
    if (!task || !window.confirm('确认删除此任务吗？')) return

    try {
      await client.delete(`/v1/tasks/${task.id}`)
      addToast('任务已删除', 'success')
      navigate('/tasks')
    } catch (err) {
      const errMsg = '删除失败，请重试'
      setError(errMsg)
      addToast(errMsg, 'error')
      console.error(err)
    }
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

  if (!task) {
    return (
      <div className="max-w-4xl mx-auto">
        {error && (
          <div className="mb-4 p-4 bg-red-50 border-2 border-red-300 text-red-700 rounded-xl font-medium">
            {error}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      {error && (
        <div className="mb-4 p-4 bg-red-50 border-2 border-red-300 text-red-700 rounded-xl font-medium">
          {error}
        </div>
      )}

      <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
        <h2 className="text-3xl font-bold text-gray-900 mb-8">编辑任务</h2>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-bold text-gray-800 mb-2">任务标题</label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-800 mb-2">描述</label>
            <textarea
              name="description"
              value={formData.description || ''}
              onChange={handleInputChange}
              rows={4}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-gray-800 mb-2">所属目标</label>
              <select
                name="goal_id"
                value={formData.goal_id || ''}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
              >
                <option value="">不关联目标</option>
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
                name="priority"
                value={formData.priority}
                onChange={handleInputChange}
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
                name="due_date"
                value={formData.due_date || ''}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
              />
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-800 mb-2">预计小时数</label>
              <input
                type="number"
                name="estimated_hours"
                value={formData.estimated_hours || ''}
                onChange={handleInputChange}
                step="0.5"
                min="0"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition"
              />
            </div>
          </div>

          <div className="flex space-x-3">
            <button
              type="submit"
              className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 px-4 rounded-xl hover:shadow-lg transform hover:scale-105 transition font-bold"
            >
              保存更改
            </button>
            <button
              type="button"
              onClick={handleDelete}
              className="flex-1 bg-gradient-to-r from-red-500 to-red-600 text-white py-3 px-4 rounded-xl hover:shadow-lg transition font-bold"
            >
              删除任务
            </button>
            <button
              type="button"
              onClick={() => navigate('/tasks')}
              className="flex-1 bg-gray-200 text-gray-700 py-3 px-4 rounded-xl hover:bg-gray-300 hover:shadow-lg transition font-bold"
            >
              返回
            </button>
          </div>
        </form>

        {/* Task Info */}
        <div className="mt-8 pt-8 border-t-2 border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4">任务信息</h3>
          <dl className="grid grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-indigo-50 to-purple-50 p-4 rounded-xl border border-indigo-200">
              <dt className="text-sm font-bold text-indigo-700 uppercase">状态</dt>
              <dd className="text-sm font-bold text-gray-900 mt-2">
                <span className="px-3 py-1 rounded-full text-xs bg-indigo-200 text-indigo-800 font-bold">
                  {task.status === 'not_started' && '未开始'}
                  {task.status === 'in_progress' && '进行中'}
                  {task.status === 'completed' && '已完成'}
                  {task.status === 'cancelled' && '已取消'}
                </span>
              </dd>
            </div>
            <div className="bg-gradient-to-br from-orange-50 to-yellow-50 p-4 rounded-xl border border-orange-200">
              <dt className="text-sm font-bold text-orange-700 uppercase">实际工时</dt>
              <dd className="text-3xl font-bold text-orange-600 mt-2">{task.actual_hours || 0} 小时</dd>
            </div>
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-4 rounded-xl border border-blue-200">
              <dt className="text-sm font-bold text-blue-700 uppercase">创建时间</dt>
              <dd className="text-sm font-bold text-gray-900 mt-2">
                {new Date(task.created_at).toLocaleDateString('zh-CN')}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  )
}
