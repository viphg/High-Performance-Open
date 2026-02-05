from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class AchievementType(str, enum.Enum):
    """成就类型枚举"""
    TASK_MASTER = "task_master"
    GOAL_ACHIEVER = "goal_achiever"
    PRODUCTIVITY_NINJA = "productivity_ninja"
    TIME_MANAGER = "time_manager"
    CONSISTENT_PERFORMER = "consistent_performer"
    EARLY_BIRD = "early_bird"
    DEADLINE_DEFENDER = "deadline_defender"
    MULTI_GOAL_CHAMPION = "multi_goal_champion"

# Achievement class already exists in achievement.py, so we'll only define the additional classes here

class UserAchievement(Base):
    """用户成就解锁记录"""
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False, index=True)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
    progress_value = Column(Integer, default=0)  # 进度值（如：10/20个任务）
    is_completed = Column(Boolean, default=False)  # 是否完全达成
    
    # 关系
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", backref="user_unlocks")
    
    def __repr__(self):
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id}, progress={self.progress_value}/{self.is_completed})>"


class UserStreak(Base):
    """用户连续记录"""
    __tablename__ = "user_streaks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    streak_type = Column(String(50), nullable=False, index=True)  # streak类型：daily_task, weekly_goal等
    current_streak = Column(Integer, default=0, index=True)  # 当前连续天数
    max_streak = Column(Integer, default=0, index=True)  # 历史最长连续天数
    last_activity_date = Column(DateTime(timezone=True), nullable=True)  # 最后活动日期
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="streaks")
    
    def __repr__(self):
        return f"<UserStreak(user_id={self.user_id}, type={self.streak_type}, current={self.current_streak}, max={self.max_streak})>"


class Notification(Base):
    """通知系统"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False, index=True)  # 通知类型：goal_deadline, task_reminder, achievement等
    related_id = Column(Integer, nullable=True, index=True)  # 相关的ID（如目标ID、任务ID）
    is_read = Column(Boolean, default=False, index=True)
    is_action_required = Column(Boolean, default=False)  # 是否需要用户操作
    action_url = Column(String(255), nullable=True)  # 操作链接
    expires_at = Column(DateTime(timezone=True), nullable=True)  # 过期时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, read={self.is_read})>"
