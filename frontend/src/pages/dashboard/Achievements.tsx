import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/context/ToastContext'
import client from '@/api/client'

interface Achievement {
  id: number
  title: string
  points: number
  category?: string
}

interface Stats {
  total_unlocked: number
  total_points: number
  unlocked: Achievement[]
}

export default function AchievementsPage() {
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
      const response = await client.get('/v1/achievements/stats')
      setStats(response.data)
    } catch (err) {
      addToast('加载成就失败', 'error')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const badgeColors: Record<string, string> = {
    目标完成: 'from-purple-50 to-purple-100 border-purple-200',
    任务完成: 'from-blue-50 to-blue-100 border-blue-200',
    连续打卡: 'from-orange-50 to-orange-100 border-orange-200',
    高效完成: 'from-green-50 to-green-100 border-green-200',
    新手: 'from-yellow-50 to-yellow-100 border-yellow-200',
    默认: 'from-yellow-50 to-yellow-100 border-yellow-200',
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

  if (!stats) return null

  return (
    <>
      <h2 className="text-3xl font-bold text-gray-900 mb-8">我的成就</h2>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl shadow-md hover:shadow-lg transition p-8 border border-purple-200">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-bold text-purple-700 uppercase tracking-wide">总成就解锁</div>
              <div className="mt-4 flex items-baseline">
                <div className="text-4xl font-bold text-purple-900">{stats.total_unlocked}</div>
                <span className="text-sm text-purple-600 ml-2">个</span>
              </div>
            </div>
            <div className="text-4xl opacity-30">🎖️</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-2xl shadow-md hover:shadow-lg transition p-8 border border-yellow-200">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-bold text-yellow-700 uppercase tracking-wide">获得积分</div>
              <div className="mt-4 flex items-baseline">
                <div className="text-4xl font-bold text-yellow-900">{stats.total_points}</div>
                <span className="text-sm text-yellow-600 ml-2">分</span>
              </div>
            </div>
            <div className="text-4xl opacity-30">⭐</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-2xl shadow-md hover:shadow-lg transition p-8 border border-indigo-200">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-bold text-indigo-700 uppercase tracking-wide">完成率</div>
              <div className="mt-4 flex items-baseline">
                <div className="text-4xl font-bold text-indigo-900">{stats.unlocked.length > 0 ? '100' : '0'}%</div>
              </div>
              <div className="mt-4 relative pt-1">
                <div className="overflow-hidden h-3 text-xs flex rounded-full bg-indigo-200">
                  <div
                    className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full"
                    style={{ width: stats.unlocked.length > 0 ? '100%' : '0%' }}
                  />
                </div>
              </div>
            </div>
            <div className="text-4xl opacity-30">🏅</div>
          </div>
        </div>
      </div>

      {/* Achievements Grid */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">已解锁成就</h2>
        {stats.unlocked.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-100">
            <p className="text-gray-500 text-lg">还未解锁任何成就，继续加油！</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.unlocked.map((achievement) => {
              const colorClass = badgeColors[achievement.category || '默认'] || badgeColors['默认']
              return (
                <div
                  key={achievement.id}
                  className={`bg-gradient-to-br ${colorClass} rounded-2xl shadow-md hover:shadow-xl transition p-8 text-center border`}
                >
                  <div className="text-5xl mb-4 opacity-80">🏆</div>
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{achievement.title}</h3>
                  <p className="text-sm text-gray-700 font-semibold mb-3">{achievement.category}</p>
                  <div className="text-3xl font-bold text-yellow-500">+{achievement.points}</div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Available Achievements */}
      <div className="mt-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">可获取成就</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { title: '初出茅庐', points: 10, category: '新手' },
            { title: '百发百中', points: 50, category: '目标完成' },
            { title: '铁血战士', points: 100, category: '连续打卡' },
            { title: '高效能人士', points: 75, category: '高效完成' },
          ].map((achievement, idx) => {
            const colorClass = badgeColors[achievement.category || '默认'] || badgeColors['默认']
            return (
              <div
                key={idx}
                className={`bg-gradient-to-br ${colorClass} rounded-2xl shadow-md p-8 text-center opacity-60 border`}
              >
                <div className="text-5xl mb-4 opacity-50">🎯</div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{achievement.title}</h3>
                <p className="text-sm text-gray-700 font-semibold mb-3">{achievement.category}</p>
                <div className="text-3xl font-bold text-gray-400">+{achievement.points}</div>
                <p className="text-xs text-gray-600 mt-3 font-bold">未获得</p>
              </div>
            )
          })}
        </div>
      </div>
    </>
  )
}
