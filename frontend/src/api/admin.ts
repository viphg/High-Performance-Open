import client from './client'
import type { User } from '@/types'

export interface UserListResponse {
  total: number
  users: User[]
}

export interface AdminStats {
  total_users: number
  active_users: number
  inactive_users: number
  admin_users: number
  new_users_today: number
  new_users_this_week: number
  new_users_this_month: number
}

export interface UserUpdateAdmin {
  is_active?: boolean
  is_admin?: boolean
  full_name?: string
  email?: string
}

export interface PasswordResetData {
  new_password: string
  confirm_password: string
}

export const adminAPI = {
  // 获取用户列表
  getUsers: (params?: {
    skip?: number
    limit?: number
    is_active?: boolean
    is_admin?: boolean
    search?: string
  }) =>
    client.get<UserListResponse>('/v1/admin/users', { params }),

  // 获取用户详情
  getUser: (userId: number) =>
    client.get<User>(`/v1/admin/users/${userId}`),

  // 更新用户信息
  updateUser: (userId: number, data: UserUpdateAdmin) =>
    client.put<User>(`/v1/admin/users/${userId}`, data),

  // 删除用户（软删除）
  deleteUser: (userId: number) =>
    client.delete(`/v1/admin/users/${userId}`),

  // 激活用户
  activateUser: (userId: number) =>
    client.post<User>(`/v1/admin/users/${userId}/activate`),

  // 禁用用户
  deactivateUser: (userId: number) =>
    client.post<User>(`/v1/admin/users/${userId}/deactivate`),

  // 设置管理员权限
  setAdmin: (userId: number, isAdmin: boolean = true) =>
    client.post<User>(`/v1/admin/users/${userId}/set-admin`, null, {
      params: { is_admin: isAdmin }
    }),

  // 重置用户密码
  resetPassword: (userId: number, data: PasswordResetData) =>
    client.post<User>(`/v1/admin/users/${userId}/reset-password`, data),

  // 获取统计信息
  getStats: () =>
    client.get<AdminStats>('/v1/admin/stats'),
}
