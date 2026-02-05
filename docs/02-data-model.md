# 数据模型设计 (Data Model)

## 概述

本文档定义了 High-Performance 系统的数据模型，包括关系设计、字段定义、索引策略和约束条件。

---

## 1. 用户相关模型

### 1.1 users (用户表)
```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    
    -- 个人信息
    nickname VARCHAR(50),
    avatar_url TEXT,
    bio VARCHAR(500),
    
    -- 系统设置
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'zh-CN',
    is_active BOOLEAN DEFAULT TRUE,
    
    -- 认证信息
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP,
    
    -- 时间戳
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_is_active ON users(is_active);
```

**字段说明**:
- `id`: 用户唯一标识（雪花 ID）
- `email`: 邮箱（唯一，用于登录和邮件发送）
- `username`: 用户名（唯一，3-20 字符）
- `nickname`: 显示名称（可选，1-50 字符）
- `avatar_url`: 头像 CDN 链接
- `timezone`: 用户时区（影响邮件发送和数据统计）
- `language`: 首选语言
- `is_active`: 账户状态
- `deleted_at`: 软删除时间戳

---

### 1.2 user_settings (用户设置表)
```sql
CREATE TABLE user_settings (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL UNIQUE,
    
    -- 邮件设置
    email_task_reminder BOOLEAN DEFAULT TRUE,
    email_achievement_notification BOOLEAN DEFAULT TRUE,
    email_weekly_report BOOLEAN DEFAULT TRUE,
    email_monthly_report BOOLEAN DEFAULT TRUE,
    email_reminder_time VARCHAR(5) DEFAULT '08:00',  -- HH:MM 格式
    do_not_disturb_start VARCHAR(5),  -- 勿扰时间段
    do_not_disturb_end VARCHAR(5),
    
    -- 隐私设置
    profile_visibility VARCHAR(20) DEFAULT 'private',  -- private/friends/public
    achievements_visibility VARCHAR(20) DEFAULT 'private',
    goals_visibility VARCHAR(20) DEFAULT 'private',
    
    -- 通知设置
    in_app_notifications BOOLEAN DEFAULT TRUE,
    browser_notifications BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 2. 目标相关模型

### 2.1 goals (目标表)
```sql
CREATE TABLE goals (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    
    -- 基本信息
    title VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,  -- career, health, learning, finance, personal
    goal_type VARCHAR(20),  -- short_term(<90d), medium_term(90-365d), long_term(>365d)
    
    -- 目标日期
    target_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- active, paused, completed, failed
    
    -- 进度追踪
    progress_percentage INT DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    
    -- 元数据
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CHECK (target_date >= CURRENT_DATE)
);

-- 索引
CREATE INDEX idx_goals_user_id ON goals(user_id);
CREATE INDEX idx_goals_status ON goals(status);
CREATE INDEX idx_goals_target_date ON goals(target_date);
CREATE INDEX idx_goals_created_at ON goals(created_at DESC);
```

**字段说明**:
- `category`: 目标分类，预定义值为 career/health/learning/finance/personal
- `goal_type`: 根据 target_date 自动计算
- `progress_percentage`: 0-100，代表完成度百分比
- `status`: 流转状态 (active → paused/completed/failed)
- `is_public`: 目标是否可公开查看

---

### 2.2 goal_milestones (目标里程碑表)
```sql
CREATE TABLE goal_milestones (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    goal_id BIGINT NOT NULL,
    
    title VARCHAR(200) NOT NULL,
    description TEXT,
    target_date DATE NOT NULL,
    progress_percentage INT DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
);

CREATE INDEX idx_milestones_goal_id ON goal_milestones(goal_id);
CREATE INDEX idx_milestones_target_date ON goal_milestones(target_date);
```

---

## 3. 任务相关模型

### 3.1 tasks (任务表)
```sql
CREATE TABLE tasks (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    goal_id BIGINT,  -- 可选关联目标
    
    -- 基本信息
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',  -- high, medium, low
    status VARCHAR(20) NOT NULL DEFAULT 'todo',  -- todo, in_progress, done, cancelled
    
    -- 时间
    due_date DATE,
    estimated_hours DECIMAL(8, 2),  -- 预估耗时（小时）
    actual_hours DECIMAL(8, 2),  -- 实际耗时
    
    -- 元数据
    is_public BOOLEAN DEFAULT FALSE,
    tags JSON,  -- 存储标签数组，如 ["urgent", "work"]
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_goal_id ON tasks(goal_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

**字段说明**:
- `status`: 任务状态流转 (todo → in_progress → done 或 cancelled)
- `estimated_hours`: 预估工时，用于生成图表
- `actual_hours`: 实际工时，在标记完成时计算
- `tags`: 以 JSON 数组格式存储，便于全文搜索

---

### 3.2 task_timeLogs (任务耗时日志表)
```sql
CREATE TABLE task_time_logs (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    task_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    
    -- 耗时记录
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    duration_minutes INT NOT NULL,  -- 实际耗时（分钟）
    description TEXT,  -- 备注
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CHECK (end_time > start_time)
);

CREATE INDEX idx_time_logs_task_id ON task_time_logs(task_id);
CREATE INDEX idx_time_logs_user_id ON task_time_logs(user_id);
CREATE INDEX idx_time_logs_start_time ON task_time_logs(start_time DESC);
```

---

## 4. 成就相关模型

### 4.1 badges (徽章定义表)
```sql
CREATE TABLE badges (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url TEXT NOT NULL,
    icon_color VARCHAR(20),  -- 图标颜色代码
    
    -- 解锁条件
    condition_type VARCHAR(50) NOT NULL,  -- tasks_completed, goals_completed, streak, custom
    condition_value INT,  -- 条件值（如需完成 10 个任务）
    condition_expression JSON,  -- 复杂条件的 JSON 表达式
    
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 系统预定义徽章（由管理员初始化）
-- 示例:
-- 🎯 目标大师: condition_type='goals_completed', condition_value=10
-- ✅ 任务大师: condition_type='tasks_completed', condition_value=100
-- 🔥 连胜者: condition_type='streak', condition_value=7
```

**预定义徽章**:
| 徽章 | 条件 | 描述 |
|------|------|------|
| 🎯 目标大师 | 完成 10 个目标 | 你已完成 10 个目标，展示了非凡的执行力 |
| ✅ 任务完成者 | 完成 100 个任务 | 你已完成 100 个任务，继续保持！ |
| 🔥 连胜者 | 连续 7 天完成任务 | 连续 7 天打卡，你正在建立良好习惯 |
| 💪 坚持者 | 连续 30 天打卡 | 连续 30 天，你是持之以恒的典范 |
| ⚡ 闪电 | 1 天内完成 5 个任务 | 高效执行者，恭喜你！ |

---

### 4.2 user_achievements (用户成就表)
```sql
CREATE TABLE user_achievements (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    badge_id BIGINT NOT NULL,
    
    unlocked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_featured BOOLEAN DEFAULT FALSE,  -- 用户是否置顶展示此成就
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE RESTRICT,
    UNIQUE(user_id, badge_id)  -- 每个用户每个徽章只能解锁一次
);

CREATE INDEX idx_achievements_user_id ON user_achievements(user_id);
CREATE INDEX idx_achievements_unlocked_at ON user_achievements(unlocked_at DESC);
```

---

### 4.3 user_levels (用户等级表)
```sql
CREATE TABLE user_levels (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL UNIQUE,
    
    -- 等级信息
    current_level INT DEFAULT 1,
    total_points INT DEFAULT 0,
    points_to_next_level INT,
    
    -- 历史记录
    total_completed_tasks INT DEFAULT 0,
    total_completed_goals INT DEFAULT 0,
    total_badges_earned INT DEFAULT 0,
    longest_streak INT DEFAULT 0,  -- 最长连续打卡天数
    
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_levels_user_id ON user_levels(user_id);
CREATE INDEX idx_levels_current_level ON user_levels(current_level DESC);
CREATE INDEX idx_levels_total_points ON user_levels(total_points DESC);
```

**等级系统定义**:
```
Lv.1-10:  初心者 (0-1,000 积分)
Lv.11-20: 精英 (1,001-5,000 积分)
Lv.21-30: 大师 (5,001+ 积分)

积分来源:
- 完成任务: +10 分
- 完成目标: +100 分
- 解锁徽章: +50 分
- 连续打卡: +5 分/天
```

---

## 5. 通知相关模型

### 5.1 notification_rules (通知规则表)
```sql
CREATE TABLE notification_rules (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    
    -- 规则类型
    rule_type VARCHAR(50) NOT NULL,  -- task_due, achievement, weekly_report, monthly_report
    is_enabled BOOLEAN DEFAULT TRUE,
    
    -- 频率设置
    frequency VARCHAR(20),  -- daily, weekly, custom
    custom_schedule JSON,  -- CRON 表达式或自定义时间数组
    
    -- 内容设置
    include_details BOOLEAN DEFAULT TRUE,
    filter_priority VARCHAR(20),  -- 仅发送高优先级、或所有
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_rules_user_id ON notification_rules(user_id);
CREATE INDEX idx_rules_rule_type ON notification_rules(rule_type);
```

---

### 5.2 email_logs (邮件发送日志表)
```sql
CREATE TABLE email_logs (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    
    recipient_email VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    email_type VARCHAR(50) NOT NULL,  -- task_reminder, achievement, report, etc
    
    -- 发送状态
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, sent, failed, bounced
    error_message TEXT,
    retry_count INT DEFAULT 0 CHECK (retry_count <= 3),
    
    -- 追踪
    message_id VARCHAR(255),  -- SendGrid/SMTP 消息 ID
    opened_at TIMESTAMP,
    link_clicked_at TIMESTAMP,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_email_logs_user_id ON email_logs(user_id);
CREATE INDEX idx_email_logs_status ON email_logs(status);
CREATE INDEX idx_email_logs_created_at ON email_logs(created_at DESC);
```

---

## 6. 权限相关模型

### 6.1 resource_shares (资源共享表)
```sql
CREATE TABLE resource_shares (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    
    -- 资源信息
    resource_type VARCHAR(50) NOT NULL,  -- goal, task
    resource_id BIGINT NOT NULL,
    owner_id BIGINT NOT NULL,
    
    -- 共享设置
    share_type VARCHAR(20) NOT NULL,  -- private, link_share, public
    share_token VARCHAR(64) UNIQUE,  -- 链接分享的 token
    
    -- 权限
    can_view BOOLEAN DEFAULT TRUE,
    can_comment BOOLEAN DEFAULT FALSE,
    can_edit BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(resource_type, resource_id, share_type)
);

CREATE INDEX idx_shares_owner_id ON resource_shares(owner_id);
CREATE INDEX idx_shares_share_token ON resource_shares(share_token);
```

---

## 7. 活动日志模型

### 7.1 activity_logs (活动日志表)
```sql
CREATE TABLE activity_logs (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    
    -- 操作记录
    action VARCHAR(50) NOT NULL,  -- create, update, delete, complete, share
    entity_type VARCHAR(50) NOT NULL,  -- user, goal, task, achievement
    entity_id BIGINT,
    
    -- 详细信息
    changes JSONB,  -- 修改前后的差异记录
    description TEXT,
    
    ip_address VARCHAR(45),  -- IPv4/IPv6
    user_agent TEXT,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_action ON activity_logs(action);
CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at DESC);
```

---

## 8. 数据统计模型

### 8.1 daily_stats (每日统计表)
```sql
CREATE TABLE daily_stats (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    stat_date DATE NOT NULL,
    
    -- 任务统计
    tasks_created INT DEFAULT 0,
    tasks_completed INT DEFAULT 0,
    tasks_failed INT DEFAULT 0,
    
    -- 目标统计
    goals_created INT DEFAULT 0,
    goals_completed INT DEFAULT 0,
    
    -- 成就统计
    badges_earned INT DEFAULT 0,
    points_earned INT DEFAULT 0,
    
    -- 工时统计
    total_work_hours DECIMAL(8, 2) DEFAULT 0,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, stat_date)
);

CREATE INDEX idx_daily_stats_user_id ON daily_stats(user_id);
CREATE INDEX idx_daily_stats_stat_date ON daily_stats(stat_date DESC);
```

---

## 9. ER 图关系总览

```
users (1) ──────────────┬─────────────── (N) goals
                        ├─────────────── (N) tasks
                        ├─────────────── (N) user_levels
                        ├─────────────── (1) user_settings
                        ├─────────────── (N) user_achievements
                        ├─────────────── (N) activity_logs
                        ├─────────────── (N) daily_stats
                        ├─────────────── (N) notification_rules
                        └─────────────── (N) email_logs

goals (1) ──────────────┬─────────────── (N) tasks
                        └─────────────── (N) goal_milestones

tasks (1) ───────────────────────────── (N) task_time_logs

badges (1) ───────────────────────────── (N) user_achievements
```

---

## 10. 数据类型约定

### 时间戳
- 所有时间字段使用 `TIMESTAMP` 类型
- 存储 UTC 时间，在应用层转换为用户时区

### 金额/小数
- 使用 `DECIMAL(8, 2)` 表示（工时、积分等）

### JSON 字段
- 使用 `JSON` 或 `JSONB`（PostgreSQL）
- 用于存储可扩展数据结构（标签、配置、变更记录）

### 索引策略
- 频繁查询的列（user_id, status, date）建立索引
- 外键列自动建立索引
- 避免过多索引影响写入性能

---

## 11. 数据一致性约束

| 约束 | 规则 |
|------|------|
| **目标进度** | 自动计算：完成任务数 / 总任务数 * 100 |
| **用户等级** | 基于总积分自动计算 |
| **成就解锁** | 后台批处理每 5 分钟检查一次 |
| **软删除** | deleted_at != NULL 的记录视为已删除 |
| **邮件重试** | 失败邮件自动重试，最多 3 次 |

---

## 12. 迁移策略

### 初始化脚本
- 使用 Alembic（Python）或 Flyway（Java）管理迁移
- 所有 SQL 都在 `migrations/` 目录版本控制

### 数据备份
- 生产环境日备份（保留 90 天）
- 大型迁移前必须完整备份

---

**文档版本**: v1.0  
**最后更新**: 2026年2月2日
