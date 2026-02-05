import client from './client'
import type { Task, TaskCreate } from '../types'

export const tasksAPI = {
  // 创建任务
  create: (data: TaskCreate) =>
    client.post<Task>('/v1/tasks', data),

  // 获取任务列表
  list: (skip = 0, limit = 100) =>
    client.get<Task[]>('/v1/tasks', { params: { skip, limit } }),

  // 获取单个任务
  get: (id: number) =>
    client.get<Task>(`/v1/tasks/${id}`),

  // 更新任务
  update: (id: number, data: Partial<TaskCreate> & { status?: string }) =>
    client.put<Task>(`/v1/tasks/${id}`, data),

  // 删除任务
  delete: (id: number) =>
    client.delete(`/v1/tasks/${id}`),
}
