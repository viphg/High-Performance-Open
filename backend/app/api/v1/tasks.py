from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Task, Goal
from app.utils.dependencies import get_current_user
from app.models import User
from app.services.goal_progress import update_goal_progress
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    goal_id: Optional[int] = None
    priority: int = 0
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    actual_hours: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: int
    due_date: Optional[datetime]
    estimated_hours: Optional[int]
    actual_hours: int
    goal_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建任务"""
    db_task = Task(
        user_id=current_user.id,
        title=task.title,
        description=task.description,
        goal_id=task.goal_id,
        priority=task.priority,
        due_date=task.due_date,
        estimated_hours=task.estimated_hours
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # 如果任务关联了目标，更新目标进度
    if db_task.goal_id:
        update_goal_progress(db, db_task.goal_id)

    return db_task


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """列出用户的任务"""
    tasks = db.query(Task).filter(Task.user_id == current_user.id).offset(skip).limit(limit).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取任务详情"""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新任务"""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    # 保存旧状态和目标ID用于进度更新
    old_status = task.status
    old_goal_id = task.goal_id

    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.add(task)
    db.commit()

    # 如果任务状态或目标ID发生变化，更新目标进度
    if 'status' in update_data or 'goal_id' in update_data:
        # 更新旧目标的进度（如果目标ID改变）
        if old_goal_id and (old_goal_id != task.goal_id):
            update_goal_progress(db, old_goal_id)
        
        # 更新新目标的进度
        if task.goal_id:
            update_goal_progress(db, task.goal_id)

    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除任务"""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    # 保存关联的目标ID
    goal_id = task.goal_id

    db.delete(task)
    db.commit()

    # 如果任务关联了目标，更新目标进度
    if goal_id:
        update_goal_progress(db, goal_id)
