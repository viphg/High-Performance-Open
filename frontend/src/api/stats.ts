import client from './client'
import type { Stats } from '../types'

export const statsAPI = {
  // 获取统计数据
  get: () =>
    client.get<Stats>('/v1/stats/'),
}
