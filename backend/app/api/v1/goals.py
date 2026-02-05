from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Goal
from app.models.goal import GoalStatus
from app.utils.dependencies import get_current_user
from app.models import User
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/goals", tags=["goals"])


class GoalCreate(BaseModel):
    title: str
    description: str = ""
    category: str = ""
    priority: int = 0
    target_date: str = ""


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    progress: Optional[float] = None


class GoalResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: Optional[str]
    status: str
    priority: int
    progress: float
    target_date: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True


@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建目标"""
    
    db_goal = Goal(
        user_id=current_user.id,
        title=goal.title,
        description=goal.description,
        category=goal.category,
        priority=goal.priority,
        target_date=goal.target_date if goal.target_date else None,
        status="not_started"
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.get("/", response_model=list[GoalResponse])
async def list_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """列出用户的目标"""
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).offset(skip).limit(limit).all()
    return goals


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取目标详情"""
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目标不存在")
    return goal


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: int,
    goal_update: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新目标"""
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目标不存在")

    update_data = goal_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除目标"""
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目标不存在")

    db.delete(goal)
    db.commit()
