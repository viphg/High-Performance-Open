import client from './client'

export interface Achievement {
  id: number
  title: string
  points: number
  category?: string
}

export interface AchievementStats {
  total_unlocked: number
  total_points: number
  unlocked: Achievement[]
}

export const achievementApi = {
  list: async (skip = 0, limit = 100): Promise<Achievement[]> => {
    const response = await client.get('/v1/achievements', {
      params: { skip, limit },
    })
    return response.data
  },

  stats: async (): Promise<AchievementStats> => {
    const response = await client.get('/v1/achievements/stats')
    return response.data
  },
}
