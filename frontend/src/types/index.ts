// 用户相关类型
export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  is_active: boolean
  is_admin: boolean
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

// 通知相关类型
export interface Notification {
  id: number
  type: string
  title: string
  content: string
  related_type?: string
  related_id?: number
  is_read: boolean
  read_at?: string
  channel: string
  email_sent: boolean
  created_at: string
}

export interface NotificationPreference {
  id: number
  user_id: number
  task_due_email: boolean
  task_due_web: boolean
  task_due_hours_before: number
  goal_progress_email: boolean
  goal_progress_web: boolean
  goal_progress_percentage: number
  achievement_email: boolean
  achievement_web: boolean
  daily_digest: boolean
  digest_time: string
  digest_email: boolean
  digest_web: boolean
  system_announcement_email: boolean
  system_announcement_web: boolean
}

