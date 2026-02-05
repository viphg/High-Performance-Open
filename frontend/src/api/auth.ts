import client from './client'
import type { LoginRequest, LoginResponse, RegisterRequest, User } from '../types'

export const authAPI = {
  // 登录
  login: (data: LoginRequest) =>
    client.post<LoginResponse>('/v1/auth/login', data),

  // 注册
  register: (data: RegisterRequest) =>
    client.post<User>('/v1/auth/register', data),

  // 获取当前用户信息
  getCurrentUser: () =>
    client.get<User>('/v1/auth/me'),

  // 登出
  logout: () =>
    client.post('/v1/auth/logout'),
}
