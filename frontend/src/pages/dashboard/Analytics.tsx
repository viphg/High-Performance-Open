import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/context/ToastContext'
import { statsAPI } from '@/api/stats'
import { goalsAPI } from '@/api/goals'
import { tasksAPI } from '@/api/tasks'
import type { Stats, Goal, Task } from '@/types'

export default function AnalyticsPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { addToast } = useToast()
  const [stats, setStats] = useState<Stats | null>(null)
  const [goals, setGoals] = useState<Goal[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)

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
      const [statsRes, goalsRes, tasksRes] = await Promise.all([
        statsAPI.get(),
        goalsAPI.list(),
        tasksAPI.list(),
      ])
      setStats(statsRes.data)
      setGoals(goalsRes.data)
      setTasks(tasksRes.data)
    } catch (err) {
      addToast('加载数据失败', 'error')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getProgressColor = (progress: number) => {
    if (progress < 33) return 'bg-red-500'
    if (progress < 66) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'in_progress':
        return 'bg-blue-100 text-blue-800'
      case 'not_started':
        return 'bg-gray-100 text-gray-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
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

  return (
    <>
      <h2 className="text-3xl font-bold text-gray-900 mb-8">数据分析</h2>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl shadow-md hover:shadow-lg transition p-8 border border-blue-200">
          <div className="text-sm font-bold text-blue-700 uppercase tracking-wide">目标总数</div>
          <div className="mt-4 flex items-baseline">
            <div className="text-4xl font-bold text-blue-900">{stats?.totalGoals || 0}</div>
            <span className="text-sm text-blue-600 ml-2">个</span>
          </div>
          <div className="mt-4 pt-4 border-t-2 border-blue-300">
            <span className="text-xs text-blue-700 font-semibold">已完成:</span>
            <div className="text-2xl font-bold text-green-600 mt-1">{stats?.completedGoals || 0} 个</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-2xl shadow-md hover:shadow-lg transition p-8 border border-indigo-200">
          <div className="text-sm font-bold text-indigo-700 uppercase tracking-wide">目标完成度</div>
          <div className="mt-4">
            <div className="text-4xl font-bold text-indigo-900">{stats?.completionRate || 0}%</div>
            <div className="mt-4 relative pt-1">
              <div className="overflow-hidden h-3 text-xs flex rounded-full bg-indigo-200">
                <div
                  style={{ width: `${stats?.completionRate || 0}%` }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-2xl shadow-md hover:shadow-lg transition p-8 border border-orange-200">
          <div className="text-sm font-bold text-orange-700 uppercase tracking-wide">任务总数</div>
          <div className="mt-4 flex items-baseline">
            <div className="text-4xl font-bold text-orange-900">{stats?.totalTasks || 0}</div>
            <span className="text-sm text-orange-600 ml-2">个</span>
          </div>
          <div className="mt-4 pt-4 border-t-2 border-orange-300">
            <span className="text-xs text-orange-700 font-semibold">逾期:</span>
            <div className="text-2xl font-bold text-red-600 mt-1">{stats?.overdueTasks || 0} 个</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl shadow-md hover:shadow-lg transition p-8 border border-green-200">
          <div className="text-sm font-bold text-green-700 uppercase tracking-wide">任务完成度</div>
          <div className="mt-4">
            <div className="text-4xl font-bold text-green-900">{stats?.taskCompletionRate || 0}%</div>
            <div className="mt-4 relative pt-1">
              <div className="overflow-hidden h-3 text-xs flex rounded-full bg-green-200">
                <div
                  style={{ width: `${stats?.taskCompletionRate || 0}%` }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r from-green-500 to-green-600 rounded-full"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Goal Progress Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
          <h2 className="text-lg font-bold text-gray-900 mb-6">目标进度分布</h2>
          <div className="space-y-4">
            {goals.slice(0, 5).map((goal) => (
              <div key={goal.id}>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-semibold text-gray-800 truncate">{goal.title}</span>
                  <span className="text-sm font-bold text-indigo-600">{goal.progress}%</span>
                </div>
                <div className="overflow-hidden h-3 text-xs flex rounded-full bg-gradient-to-r from-gray-200 to-gray-300">
                  <div
                    style={{ width: `${goal.progress}%` }}
                    className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center rounded-full ${getProgressColor(
                      goal.progress
                    )}`}
                  />
                </div>
              </div>
            ))}
            {goals.length === 0 && <p className="text-gray-500 text-center py-8">暂无目标</p>}
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
          <h2 className="text-lg font-bold text-gray-900 mb-6">最近任务</h2>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {tasks.slice(0, 5).map((task) => (
              <div key={task.id} className="flex items-center justify-between p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl hover:shadow-md transition border border-indigo-100">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-bold text-gray-900 truncate">{task.title}</p>
                  <p className="text-xs text-gray-600 font-semibold">
                    截止: {task.due_date ? new Date(task.due_date).toLocaleDateString() : '-'}
                  </p>
                </div>
                <span className={`text-xs font-bold px-3 py-1 rounded-full whitespace-nowrap ml-2 ${getStatusColor(task.status)}`}>
                  {task.status === 'not_started' && '未开始'}
                  {task.status === 'in_progress' && '进行中'}
                  {task.status === 'completed' && '已完成'}
                  {task.status === 'cancelled' && '已取消'}
                </span>
              </div>
            ))}
            {tasks.length === 0 && <p className="text-gray-500 text-center py-8">暂无任务</p>}
          </div>
        </div>
      </div>

      {/* Status Summary */}
      <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 mb-12">
        <h2 className="text-lg font-bold text-gray-900 mb-6">状态统计</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: '目标-未开始', count: goals.filter((g) => g.status === 'not_started').length },
            { label: '目标-进行中', count: goals.filter((g) => g.status === 'in_progress').length },
            { label: '目标-已完成', count: goals.filter((g) => g.status === 'completed').length },
            { label: '目标-已取消', count: goals.filter((g) => g.status === 'cancelled').length },
            { label: '任务-未开始', count: tasks.filter((t) => t.status === 'not_started').length },
            { label: '任务-进行中', count: tasks.filter((t) => t.status === 'in_progress').length },
            { label: '任务-已完成', count: tasks.filter((t) => t.status === 'completed').length },
            { label: '任务-已取消', count: tasks.filter((t) => t.status === 'cancelled').length },
          ].map((item, idx) => (
            <div key={idx} className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-4 text-center hover:shadow-lg transition border-2 border-indigo-200">
              <div className="text-3xl font-bold text-indigo-600">{item.count}</div>
              <div className="text-xs text-gray-700 mt-2 font-bold">{item.label}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}
