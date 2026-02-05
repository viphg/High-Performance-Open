from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.dependencies import get_current_user
from app.models import User
from app.services.analytics import get_progress_trends, get_productivity_metrics
from app.services.time_management import TimeManagementService
from app.services.achievements_service import AchievementService, StreakService
from app.services.notifications import NotificationService, ReminderService
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/insights", tags=["insights"])


class ProgressTrendsResponse(BaseModel):
    daily_trends: List[dict]
    weekly_summary: List[dict]
    overall_stats: dict


class ProductivityMetricsResponse(BaseModel):
    avg_task_completion_hours: float
    avg_goal_completion_hours: float
    active_days_count: int
    productivity_score: int
    focus_index: float


class TimeTrackingResponse(BaseModel):
    period_days: int
    total_tasks: int
    priority_distribution: dict
    hourly_distribution: dict
    best_productive_hour: int
    best_productive_hour_data: dict
    avg_start_delay_hours: float
    focus_period_hours: str


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: str
    related_id: Optional[int]
    is_read: bool
    is_action_required: bool
    action_url: Optional[str]
    created_at: str


class StreakResponse(BaseModel):
    current_streak: int
    max_streak: int
    is_active_today: bool


@router.get("/progress-trends", response_model=ProgressTrendsResponse)
async def get_progress_trends(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取进度趋势数据"""
    return get_progress_trends(db, current_user.id, days)


@router.get("/productivity-metrics", response_model=ProductivityMetricsResponse)
async def get_productivity_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取生产力指标"""
    return get_productivity_metrics(db, current_user.id)


@router.get("/time-tracking", response_model=TimeTrackingResponse)
async def get_time_tracking(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取时间管理统计"""
    return TimeManagementService.get_time_tracking_summary(db, current_user.id, days)


@router.get("/goal-completion-patterns")
async def get_goal_completion_patterns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取目标完成模式"""
    return TimeManagementService.get_goal_completion_patterns(db, current_user.id)


@router.get("/time-efficiency")
async def get_time_efficiency_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取时间效率指标"""
    return TimeManagementService.get_time_efficiency_metrics(db, current_user.id)


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取通知列表"""
    notifications = NotificationService.get_user_notifications(db, current_user.id, unread_only, limit)
    
    # 转换为响应模型
    return [
        {
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.type,
            'related_id': n.related_id,
            'is_read': n.is_read,
            'is_action_required': n.is_action_required,
            'action_url': n.action_url,
            'created_at': n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifications
    ]


@router.post("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记通知为已读"""
    success = NotificationService.mark_as_read(db, current_user.id, notification_id)
    return {'success': success, 'message': '已标记为已读' if success else '通知不存在或已读'}


@router.get("/streak/daily-tasks", response_model=StreakResponse)
async def get_daily_task_streak(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取每日任务连续记录"""
    return StreakService.update_daily_task_streak(db, current_user.id)


@router.get("/smart-reminders")
async def get_smart_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取智能提醒"""
    return ReminderService.generate_smart_reminders(db, current_user.id)


@router.post("/achievements/check")
async def check_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """检查并解锁成就"""
    try:
        AchievementService.check_task_master(db, current_user.id)
        AchievementService.check_goal_achiever(db, current_user.id)
        AchievementService.check_early_bird(db, current_user.id)
        AchievementService.check_deadline_defender(db, current_user.id)
        AchievementService.check_productivity(db, current_user.id)
        AchievementService.check_consistent_performer(db, current_user.id)
        
        return {'message': '成就检查完成', 'new_unlocks': '见通知列表'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"成就检查失败: {str(e)}")

    """清理过期通知"""

@router.delete("/notifications/cleanup")
async def cleanup_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    清理过期通知
    count = NotificationService.cleanup_expired_notifications(db, current_user.id)
    return {'message': f'已清理 {count} 个过期通知'}
