from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Goal, Task
from app.utils.dependencies import get_current_user
from app.models import User
from typing import Dict

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/", response_model=Dict)
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户统计数据"""
    
    # 目标统计
    total_goals = db.query(Goal).filter(Goal.user_id == current_user.id).count()
    completed_goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.status == 'completed'
    ).count()
    completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0
    
    # 任务统计
    total_tasks = db.query(Task).filter(Task.user_id == current_user.id).count()
    completed_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == 'completed'
    ).count()
    task_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # 平均目标进度
    avg_progress = db.query(func.avg(Goal.progress)).filter(
        Goal.user_id == current_user.id
    ).scalar() or 0
    
    # 进行中的目标和任务
    active_goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.status == 'in_progress'
    ).count()
    active_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == 'in_progress'
    ).count()
    
    # 逾期任务
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc)
    overdue_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.due_date < today,
        Task.status != 'completed'
    ).count()
    
    return {
        "totalGoals": total_goals,
        "completedGoals": completed_goals,
        "completionRate": round(completion_rate, 1),
        "totalTasks": total_tasks,
        "completedTasks": completed_tasks,
        "taskCompletionRate": round(task_completion_rate, 1),
        "averageGoalProgress": round(avg_progress, 1),
        "activeGoals": active_goals,
        "activeTasks": active_tasks,
        "overdueTasks": overdue_tasks,
    }
