from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Achievement(Base):
    """成就模型"""
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    badge_icon = Column(String(255), nullable=True)  # 徽章图标URL
    points = Column(Integer, default=0)  # 成就积分
    category = Column(String(50), nullable=True)  # 分类：任务完成、目标达成等
    is_hidden = Column(Boolean, default=False)  # 是否隐藏
    unlocked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Achievement(id={self.id}, title='{self.title}', user_id={self.user_id})>"
