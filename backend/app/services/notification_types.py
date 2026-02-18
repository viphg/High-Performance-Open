"""
通知类型定义和触发规则

所有通知类型都定义在这里，便于统一管理和维护
"""

from enum import Enum
from typing import Dict, Any, Callable
from datetime import datetime, timedelta


class NotificationType(str, Enum):
    """通知类型枚举"""
    # 任务相关
    TASK_DUE_SOON = "task_due_soon"           # 任务即将到期
    TASK_OVERDUE = "task_overdue"             # 任务已逾期
    TASK_COMPLETED = "task_completed"         # 任务完成
    
    # 目标相关
    GOAL_PROGRESS = "goal_progress"           # 目标进度更新
    GOAL_COMPLETED = "goal_completed"         # 目标完成
    GOAL_DUE_SOON = "goal_due_soon"           # 目标即将到期
    
    # 成就相关
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"  # 成就解锁
    STREAK_MILESTONE = "streak_milestone"     # 连续打卡里程碑
    
    # 系统相关
    WELCOME = "welcome"                       # 欢迎新用户
    SYSTEM_ANNOUNCEMENT = "system_announcement"  # 系统公告
    DAILY_DIGEST = "daily_digest"             # 每日摘要
    
    # 提醒相关
    REMINDER = "reminder"                     # 自定义提醒


class NotificationChannel(str, Enum):
    """通知渠道"""
    WEB = "web"           # 站内通知
    EMAIL = "email"       # 邮件通知
    PUSH = "push"         # 推送通知（未来支持）


# 通知触发规则定义
NOTIFICATION_RULES: Dict[NotificationType, Dict[str, Any]] = {
    NotificationType.TASK_DUE_SOON: {
        "name": "任务到期提醒",
        "description": "任务即将到期时发送提醒",
        "default_channels": [NotificationChannel.WEB, NotificationChannel.EMAIL],
        "configurable": True,
        "trigger": "time_based",
        "conditions": {
            "hours_before": 24,  # 默认提前24小时
        }
    },
    
    NotificationType.TASK_OVERDUE: {
        "name": "任务逾期提醒",
        "description": "任务已逾期时发送提醒",
        "default_channels": [NotificationChannel.WEB, NotificationChannel.EMAIL],
        "configurable": True,
        "trigger": "time_based",
        "conditions": {
            "check_interval": 60,  # 每60分钟检查一次
        }
    },
    
    NotificationType.TASK_COMPLETED: {
        "name": "任务完成",
        "description": "完成任务后发送祝贺",
        "default_channels": [NotificationChannel.WEB],
        "configurable": False,
        "trigger": "event_based",
    },
    
    NotificationType.GOAL_PROGRESS: {
        "name": "目标进度",
        "description": "目标进度达到里程碑时提醒",
        "default_channels": [NotificationChannel.WEB],
        "configurable": True,
        "trigger": "progress_based",
        "conditions": {
            "milestones": [25, 50, 75, 100],  # 25%, 50%, 75%, 100%
        }
    },
    
    NotificationType.GOAL_COMPLETED: {
        "name": "目标完成",
        "description": "目标100%完成时发送祝贺",
        "default_channels": [NotificationChannel.WEB, NotificationChannel.EMAIL],
        "configurable": False,
        "trigger": "event_based",
    },
    
    NotificationType.GOAL_DUE_SOON: {
        "name": "目标到期提醒",
        "description": "目标截止日期临近时提醒",
        "default_channels": [NotificationChannel.WEB, NotificationChannel.EMAIL],
        "configurable": True,
        "trigger": "time_based",
        "conditions": {
            "days_before": 7,  # 默认提前7天
        }
    },
    
    NotificationType.ACHIEVEMENT_UNLOCKED: {
        "name": "成就解锁",
        "description": "解锁新成就时发送通知",
        "default_channels": [NotificationChannel.WEB, NotificationChannel.EMAIL],
        "configurable": True,
        "trigger": "event_based",
    },
    
    NotificationType.STREAK_MILESTONE: {
        "name": "连续打卡",
        "description": "连续打卡达到里程碑",
        "default_channels": [NotificationChannel.WEB],
        "configurable": False,
        "trigger": "event_based",
        "conditions": {
            "milestones": [3, 7, 14, 30, 60, 90, 180, 365],
        }
    },
    
    NotificationType.WELCOME: {
        "name": "欢迎",
        "description": "新用户注册欢迎",
        "default_channels": [NotificationChannel.WEB, NotificationChannel.EMAIL],
        "configurable": False,
        "trigger": "event_based",
    },
    
    NotificationType.SYSTEM_ANNOUNCEMENT: {
        "name": "系统公告",
        "description": "系统重要通知",
        "default_channels": [NotificationChannel.WEB, NotificationChannel.EMAIL],
        "configurable": True,
        "trigger": "admin_based",
    },
    
    NotificationType.DAILY_DIGEST: {
        "name": "每日摘要",
        "description": "每日任务和目标摘要",
        "default_channels": [NotificationChannel.EMAIL],
        "configurable": True,
        "trigger": "scheduled",
        "conditions": {
            "send_time": "08:00",  # 默认早上8点
        }
    },
}


# 通知模板
NOTIFICATION_TEMPLATES: Dict[NotificationType, Dict[str, str]] = {
    NotificationType.TASK_DUE_SOON: {
        "title": "⏰ 任务即将到期",
        "content": "任务【{task_title}】将在 {hours} 小时后到期，请及时完成！",
        "email_subject": "任务到期提醒 - {task_title}",
        "email_body": """
        <h2>任务到期提醒</h2>
        <p>您好！</p>
        <p>您的任务 <strong>{task_title}</strong> 将在 <strong>{hours} 小时</strong> 后到期。</p>
        <p>任务详情：{task_description}</p>
        <p><a href="{task_link}">查看任务</a></p>
        """
    },
    
    NotificationType.TASK_OVERDUE: {
        "title": "⚠️ 任务已逾期",
        "content": "任务【{task_title}】已逾期 {days} 天，请尽快处理！",
        "email_subject": "⚠️ 任务逾期提醒 - {task_title}",
        "email_body": """
        <h2>任务逾期提醒</h2>
        <p>您好！</p>
        <p>您的任务 <strong>{task_title}</strong> 已逾期 <strong>{days} 天</strong>。</p>
        <p>请尽快处理或调整截止日期。</p>
        <p><a href="{task_link}">查看任务</a></p>
        """
    },
    
    NotificationType.TASK_COMPLETED: {
        "title": "✅ 任务完成",
        "content": "恭喜！您已完成任务【{task_title}】",
        "email_subject": "✅ 任务完成",
        "email_body": """
        <h2>恭喜！</h2>
        <p>您已成功完成任务 <strong>{task_title}</strong>！</p>
        <p>继续保持，加油！💪</p>
        """
    },
    
    NotificationType.GOAL_PROGRESS: {
        "title": "📈 目标进度更新",
        "content": "目标【{goal_title}】进度已达 {progress}%",
        "email_subject": "目标进度更新 - {goal_title}",
        "email_body": """
        <h2>目标进度更新</h2>
        <p>您的目标 <strong>{goal_title}</strong> 进度已达到 <strong>{progress}%</strong>！</p>
        <p>继续保持，目标即将达成！</p>
        """
    },
    
    NotificationType.GOAL_COMPLETED: {
        "title": "🎉 目标达成！",
        "content": "太棒了！您已完成目标【{goal_title}】",
        "email_subject": "🎉 恭喜！目标达成",
        "email_body": """
        <h1>🎉 恭喜！</h1>
        <p>您已成功完成目标 <strong>{goal_title}</strong>！</p>
        <p>您的努力和坚持值得赞赏，继续加油！</p>
        """
    },
    
    NotificationType.GOAL_DUE_SOON: {
        "title": "📅 目标即将到期",
        "content": "目标【{goal_title}】将在 {days} 天后到期",
        "email_subject": "目标到期提醒 - {goal_title}",
        "email_body": """
        <h2>目标到期提醒</h2>
        <p>您的目标 <strong>{goal_title}</strong> 将在 <strong>{days} 天</strong> 后到期。</p>
        <p>当前进度：{progress}%</p>
        <p>加油，最后冲刺！</p>
        """
    },
    
    NotificationType.ACHIEVEMENT_UNLOCKED: {
        "title": "🏆 新成就解锁！",
        "content": "恭喜解锁成就【{achievement_title}】！{achievement_description}",
        "email_subject": "🏆 新成就解锁！",
        "email_body": """
        <h1>🏆 恭喜解锁新成就！</h1>
        <h2>{achievement_title}</h2>
        <p>{achievement_description}</p>
        <p>获得 {points} 积分！</p>
        <p>继续挑战更多成就吧！</p>
        """
    },
    
    NotificationType.STREAK_MILESTONE: {
        "title": "🔥 连续打卡 {days} 天！",
        "content": "太棒了！您已连续打卡 {days} 天，保持这个节奏！",
        "email_subject": "🔥 连续打卡里程碑",
        "email_body": """
        <h2>🔥 连续打卡里程碑</h2>
        <p>恭喜！您已连续打卡 <strong>{days} 天</strong>！</p>
        <p>坚持就是胜利，继续保持！</p>
        """
    },
    
    NotificationType.WELCOME: {
        "title": "👋 欢迎来到 High-Performance！",
        "content": "感谢您的注册！开始设定您的第一个目标吧！",
        "email_subject": "👋 欢迎加入 High-Performance",
        "email_body": """
        <h1>欢迎来到 High-Performance！</h1>
        <p>亲爱的 {username}，</p>
        <p>感谢您加入我们的个人成长管理平台！</p>
        <p>在这里，您可以：</p>
        <ul>
            <li>设定清晰的目标</li>
            <li>分解为可执行的任务</li>
            <li>追踪进度并获得成就</li>
            <li>养成良好的习惯</li>
        </ul>
        <p><a href="{dashboard_link}">开始您的旅程</a></p>
        <p>祝您使用愉快！</p>
        """
    },
    
    NotificationType.DAILY_DIGEST: {
        "title": "📊 今日任务摘要",
        "content": "今天有 {task_count} 个待办任务，{overdue_count} 个已逾期",
        "email_subject": "📊 您的每日摘要 - {date}",
        "email_body": """
        <h2>📊 今日任务摘要 ({date})</h2>
        
        <h3>待办任务 ({pending_count})</h3>
        {pending_tasks}
        
        <h3>今日截止 ({due_today_count})</h3>
        {due_today_tasks}
        
        <h3>已逾期 ({overdue_count})</h3>
        {overdue_tasks}
        
        <p><a href="{dashboard_link}">查看详情</a></p>
        """
    },
}
