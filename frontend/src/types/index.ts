// 用户相关类型
export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  is_active: boolean
}

// 认证相关类型
export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
}

// 目标相关类型
export interface Goal {
  id: number
  title: string
  description?: string
  category?: string
  status: 'not_started' | 'in_progress' | 'completed' | 'cancelled'
  priority: number
  progress: number
  target_date?: string
  created_at: string
}

export interface GoalCreate {
  title: string
  description?: string
  category?: string
  priority?: number
  target_date?: string
}

// 任务相关类型
export interface Task {
  id: number
  title: string
  description?: string
  status: 'not_started' | 'in_progress' | 'completed' | 'cancelled'
  priority: number
  due_date?: string
  estimated_hours?: number
  actual_hours: number
  goal_id?: number
  created_at: string
}

export interface TaskCreate {
  title: string
  description?: string
  goal_id?: number
  priority?: number
  due_date?: string
  estimated_hours?: number
}

// 成就相关类型
export interface Achievement {
  id: number
  title: string
  description?: string
  points: number
  category?: string
  badge_icon?: string
  unlocked_at?: string
}

export interface AchievementStats {
  total_unlocked: number
  total_points: number
  unlocked: Achievement[]
}

export interface Stats {
  totalGoals: number
  completedGoals: number
  completionRate: number
  totalTasks: number
  completedTasks: number
  taskCompletionRate: number
  averageGoalProgress: number
  activeGoals: number
  activeTasks: number
  overdueTasks: number
}

