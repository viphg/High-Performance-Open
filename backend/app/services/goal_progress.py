from sqlalchemy.orm import Session
from app.models import Goal, Task
from typing import Optional


def update_goal_progress(db: Session, goal_id: Optional[int]) -> None:
    """
    更新目标进度和状态

    Args:
        db: 数据库会话
        goal_id: 目标ID，如果为None则不执行更新
    """
    if goal_id is None:
        return

    # 获取目标
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        return

    # 获取目标下的所有任务
    tasks = db.query(Task).filter(Task.goal_id == goal_id).all()

    if not tasks:
        # 如果没有任务，保持现状或重置进度
        goal.progress = 0.0
        goal.status = "not_started"
        db.add(goal)
        db.commit()
        return

    # 计算完成百分比
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == 'completed')
    progress = (completed_tasks / total_tasks) * 100

    # 根据任务状态决定目标状态
    has_in_progress = any(task.status == 'in_progress' for task in tasks)
    has_not_started = any(task.status == 'not_started' for task in tasks)

    if progress == 100:
        # 所有任务完成
        goal.status = "completed"
    elif has_in_progress:
        # 有进行中的任务
        goal.status = "in_progress"
    elif has_not_started:
        # 所有任务未开始
        goal.status = "not_started"
    else:
        # 其他情况（比如有取消的任务）
        goal.status = "not_started"

    # 更新进度
    goal.progress = round(progress, 1)

    db.add(goal)
    db.commit()