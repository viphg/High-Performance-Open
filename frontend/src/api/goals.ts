import client from './client'
import type { Goal, GoalCreate } from '../types'

export const goalsAPI = {
  // 创建目标
  create: (data: GoalCreate) =>
    client.post<Goal>('/v1/goals', data),

  // 获取目标列表
  list: (skip = 0, limit = 100) =>
    client.get<Goal[]>('/v1/goals', { params: { skip, limit } }),

  // 获取单个目标
  get: (id: number) =>
    client.get<Goal>(`/v1/goals/${id}`),

  // 更新目标
  update: (id: number, data: Partial<GoalCreate>) =>
    client.put<Goal>(`/v1/goals/${id}`, data),

  // 删除目标
  delete: (id: number) =>
    client.delete(`/v1/goals/${id}`),
}
