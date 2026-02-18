// API 基础配置
const getApiBaseUrl = () => {
  // 检查环境变量
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // 默认使用本地开发环境配置
  return 'http://localhost:8001/api'
}

export const API_BASE_URL = getApiBaseUrl()

// 认证相关
export const AUTH_TOKEN_KEY = 'access_token'
