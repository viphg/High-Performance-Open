import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/context/ToastContext'
import { statsAPI } from '@/api/stats'
import type { Stats } from '@/types'

export default function Dashboard() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { addToast } = useToast()
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) {
      navigate('/auth/login')
    } else {
      loadStats()
    }
  }, [user, navigate])
  const loadStats = async () => {
    try {
      setLoading(true)
      const res = await statsAPI.get()
      setStats(res.data)
    } catch (err) {
      addToast('加载统计数据失败', 'error')
      console.error(err)
    } finally {
      setLoading(false)
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
      <h2 className="text-3xl font-bold text-gray-900 mb-8">仪表盘概览</h2>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl shadow-md hover:shadow-lg transition p-8 border border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-blue-700 uppercase tracking-wide">活跃目标</div>
              <div className="mt-4 flex items-baseline">
                <div className="text-4xl font-bold text-blue-900">{stats?.activeGoals || 0}</div>
                <span className="text-sm text-blue-600 ml-2">个</span>
              </div>
              <div className="mt-4 text-xs text-blue-600">已完成: {stats?.completedGoals || 0} 个</div>
            </div>
            <div className="text-4xl opacity-20">🎯</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-2xl shadow-md hover:shadow-lg transition p-8 border border-orange-200">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-orange-700 uppercase tracking-wide">进行中的任务</div>
              <div className="mt-4 flex items-baseline">
                <div className="text-4xl font-bold text-orange-900">{stats?.activeTasks || 0}</div>
                <span className="text-sm text-orange-600 ml-2">个</span>
              </div>
              <div className="mt-4 text-xs text-orange-600">已完成: {stats?.completedTasks || 0} 个</div>
            </div>
            <div className="text-4xl opacity-20">✓</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-2xl shadow-md hover:shadow-lg transition p-8 border border-indigo-200">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-indigo-700 uppercase tracking-wide">目标完成率</div>
              <div className="mt-4 flex items-baseline">
                <div className="text-4xl font-bold text-indigo-900">{stats?.completionRate || 0}%</div>
              </div>
              <div className="mt-4 relative pt-1">
                <div className="overflow-hidden h-3 text-xs flex rounded-full bg-indigo-200">
                  <div
                    style={{ width: `${stats?.completionRate || 0}%` }}
                    className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full"
                  />
                </div>
              </div>
            </div>
            <div className="text-4xl opacity-20">📊</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl shadow-md hover:shadow-lg transition p-8 border border-green-200">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-green-700 uppercase tracking-wide">任务完成率</div>
              <div className="mt-4 flex items-baseline">
                <div className="text-4xl font-bold text-green-900">{stats?.taskCompletionRate || 0}%</div>
              </div>
              <div className="mt-4 relative pt-1">
                <div className="overflow-hidden h-3 text-xs flex rounded-full bg-green-200">
                  <div
                    style={{ width: `${stats?.taskCompletionRate || 0}%` }}
                    className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r from-green-500 to-green-600 rounded-full"
                  />
                </div>
              </div>
            </div>
            <div className="text-4xl opacity-20">🏆</div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">欢迎回来，{user?.full_name || user?.username}！</h2>
        <p className="text-gray-600 mb-6">
          {stats?.activeGoals === 0 ? (
            '现在开始制定你的目标吧！制定清晰的目标是成功的第一步。'
          ) : (
            `你有 ${stats?.activeGoals} 个活跃目标和 ${stats?.activeTasks} 个进行中的任务。继续加油！`
          )}
        </p>
        <div className="flex flex-wrap gap-4">
          <button
            onClick={() => navigate('/goals')}
            className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:shadow-lg transform hover:scale-105 transition font-medium"
          >
            创建新目标
          </button>
          <button
            onClick={() => navigate('/tasks')}
            className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-6 py-3 rounded-xl hover:shadow-lg transform hover:scale-105 transition font-medium"
          >
            创建新任务
          </button>
          <button
            onClick={() => navigate('/analytics')}
            className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-xl hover:shadow-lg transform hover:scale-105 transition font-medium"
          >
            查看分析
          </button>
        </div>
      </div>
    </>
  )
}
