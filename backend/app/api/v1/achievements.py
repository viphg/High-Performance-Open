from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Achievement
from app.utils.dependencies import get_current_user
from app.models import User
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/achievements", tags=["achievements"])


class AchievementResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    points: int
    category: Optional[str]
    unlocked_at: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True


@router.get("/", response_model=list[AchievementResponse])
async def list_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """列出用户已解锁的成就"""
    achievements = (
        db.query(Achievement)
        .filter(Achievement.user_id == current_user.id, Achievement.unlocked_at.isnot(None))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return achievements


@router.get("/stats", response_model=dict)
async def get_achievement_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取成就统计"""
    unlocked = (
        db.query(Achievement)
        .filter(Achievement.user_id == current_user.id, Achievement.unlocked_at.isnot(None))
        .all()
    )
    
    total_points = sum(a.points for a in unlocked)
    
    return {
        "total_unlocked": len(unlocked),
        "total_points": total_points,
        "unlocked": [
            {
                "id": a.id,
                "title": a.title,
                "points": a.points,
                "category": a.category,
            }
            for a in unlocked
        ],
    }
