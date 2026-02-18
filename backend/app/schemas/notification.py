from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    """通知响应模型"""
    id: int
    type: str
    title: str
    content: str
    related_type: Optional[str]
    related_id: Optional[int]
    is_read: bool
    read_at: Optional[datetime]
    channel: str
    email_sent: bool
    created_at: datetime
    
    class Config:
        orm_mode = True


class NotificationListResponse(BaseModel):
    """通知列表响应"""
    total: int
    unread_count: int
    notifications: List[NotificationResponse]


class NotificationCountResponse(BaseModel):
    """未读通知数量响应"""
    unread_count: int


class NotificationPreferenceResponse(BaseModel):
    """通知偏好响应"""
    id: int
    user_id: int
    
    # 任务提醒
    task_due_email: bool
    task_due_web: bool
    task_due_hours_before: int
    
    # 目标进度
    goal_progress_email: bool
    goal_progress_web: bool
    goal_progress_percentage: int
    
    # 成就解锁
    achievement_email: bool
    achievement_web: bool
    
    # 每日摘要
    daily_digest: bool
    digest_time: time
    digest_email: bool
    digest_web: bool
    
    # 系统通知
    system_announcement_email: bool
    system_announcement_web: bool
    
    class Config:
        orm_mode = True


class NotificationPreferenceUpdate(BaseModel):
    """更新通知偏好请求"""
    task_due_email: Optional[bool] = None
    task_due_web: Optional[bool] = None
    task_due_hours_before: Optional[int] = None
    goal_progress_email: Optional[bool] = None
    goal_progress_web: Optional[bool] = None
    goal_progress_percentage: Optional[int] = None
    achievement_email: Optional[bool] = None
    achievement_web: Optional[bool] = None
    daily_digest: Optional[bool] = None
    digest_time: Optional[time] = None
    digest_email: Optional[bool] = None
    digest_web: Optional[bool] = None
    system_announcement_email: Optional[bool] = None
    system_announcement_web: Optional[bool] = None
