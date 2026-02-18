from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import time


class NotificationPreference(Base):
    """用户通知偏好设置"""
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # 任务提醒设置
    task_due_email = Column(Boolean, default=True)
    task_due_web = Column(Boolean, default=True)
    task_due_hours_before = Column(Integer, default=24)  # 提前几小时提醒
    
    # 目标进度提醒
    goal_progress_email = Column(Boolean, default=False)
    goal_progress_web = Column(Boolean, default=True)
    goal_progress_percentage = Column(Integer, default=50)  # 进度达到多少提醒
    
    # 成就解锁提醒
    achievement_email = Column(Boolean, default=True)
    achievement_web = Column(Boolean, default=True)
    
    # 每日摘要
    daily_digest = Column(Boolean, default=False)
    digest_time = Column(Time, default=time(8, 0))  # 默认早上8点
    digest_email = Column(Boolean, default=True)
    digest_web = Column(Boolean, default=True)
    
    # 系统通知
    system_announcement_email = Column(Boolean, default=True)
    system_announcement_web = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="notification_preference")
    
    def __repr__(self):
        return f"<NotificationPreference(user_id={self.user_id})>"
