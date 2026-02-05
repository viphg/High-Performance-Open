from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class GoalStatus(str, enum.Enum):
    """目标状态枚举"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Goal(Base):
    """目标模型"""
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # 工作、学习、健康等
    status = Column(String(20), default="not_started", index=True)
    priority = Column(Integer, default=0)  # 优先级 1-5
    start_date = Column(DateTime(timezone=True), nullable=True)
    target_date = Column(DateTime(timezone=True), nullable=True)
    progress = Column(Float, default=0.0)  # 0-100
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Goal(id={self.id}, title='{self.title}', status='{self.status}')>"
