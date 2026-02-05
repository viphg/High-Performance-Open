from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, or_
from app.models import Goal, Task, User
from datetime import datetime, timedelta
from typing import List, Dict, Optional


def get_progress_trends(db: Session, user_id: int, days: int = 30) -> Dict:
    """
    获取用户进度趋势数据
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        days: 分析天数，默认30天
    
    Returns:
        Dict: 包含趋势数据的字典
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 按天统计完成的任务数和目标数
    daily_stats = db.query(
        extract('day', Task.created_at).label('date'),
        func.count(func.nullif(Task.status != 'completed', True)).label('total_tasks'),
        func.count(func.nullif(Task.status == 'completed', True)).label('completed_tasks'),
        func.count(func.nullif(Goal.status == 'completed', True)).label('completed_goals')
    ).outerjoin(Goal, Task.goal_id == Goal.id).filter(
        Task.user_id == user_id,
        Task.created_at >= start_date,
        Task.created_at <= end_date
    ).group_by(
        extract('day', Task.created_at)
    ).all()
    
    # 转换为趋势数据
    trends = []
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        day_stat = next((s for s in daily_stats if s.date == current_date.day), None)
        
        trends.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'day_of_week': current_date.strftime('%A'),
            'total_tasks': day_stat.total_tasks if day_stat else 0,
            'completed_tasks': day_stat.completed_tasks if day_stat else 0,
            'completed_goals': day_stat.completed_goals if day_stat else 0,
            'task_completion_rate': (day_stat.completed_tasks / day_stat.total_tasks * 100) if day_stat and day_stat.total_tasks > 0 else 0,
        })
    
    # 计算周统计
    week_stats = []
    for week_start in range(0, days, 7):
        week_end = min(week_start + 6, days - 1)
        week_data = trends[week_start:week_end + 1]
        
        total_week_tasks = sum(d['total_tasks'] for d in week_data)
        completed_week_tasks = sum(d['completed_tasks'] for d in week_data)
        completed_week_goals = sum(d['completed_goals'] for d in week_data)
        
        week_stats.append({
            'week': f"第{week_start // 7 + 1}周",
            'total_tasks': total_week_tasks,
            'completed_tasks': completed_week_tasks,
            'completed_goals': completed_week_goals,
            'completion_rate': (completed_week_tasks / total_week_tasks * 100) if total_week_tasks > 0 else 0,
        })
    
    return {
        'daily_trends': trends,
        'weekly_summary': week_stats,
        'overall_stats': {
            'total_days': days,
            'total_tasks': sum(t['total_tasks'] for t in trends),
            'completed_tasks': sum(t['completed_tasks'] for t in trends),
            'completed_goals': sum(t['completed_goals'] for t in trends),
            'avg_daily_completion': sum(t['task_completion_rate'] for t in trends) / len(trends) if trends else 0,
        }
    }


def get_productivity_metrics(db: Session, user_id: int) -> Dict:
    """
    获取用户生产力指标
    """
    # 获取任务平均完成时间
    task_completion_times = db.query(
        func.avg(func.extract('epoch', Task.created_at) - func.extract('epoch', func.coalesce(Task.completed_at, func.now()))).label('avg_completion_seconds')
    ).filter(
        Task.user_id == user_id,
        Task.status == 'completed',
        Task.created_at >= func.now() - timedelta(days=30)
    ).scalar() or 0
    
    # 获取目标平均完成时间
    goal_completion_times = db.query(
        func.avg(func.extract('epoch', Goal.created_at) - func.extract('epoch', func.coalesce(
            db.query(func.min(Task.created_at))
            .filter(Task.goal_id == Goal.id, Task.status == 'completed')
            .correlate(Goal)
            .scalar_subquery(), func.now()
        ))).label('avg_goal_completion_seconds')
    ).filter(
        Goal.user_id == user_id,
        Goal.status == 'completed',
        Goal.created_at >= func.now() - timedelta(days=30)
    ).scalar() or 0
    
    # 获取专注度指标（连续活跃天数）
    active_days = db.query(
        func.count(func.distinct(extract('day', Task.created_at)))
    ).filter(
        Task.user_id == user_id,
        Task.created_at >= func.now() - timedelta(days=30)
    ).scalar() or 0
    
    return {
        'avg_task_completion_hours': round(task_completion_times / 3600, 2),  # 转换为小时
        'avg_goal_completion_hours': round(goal_completion_times / 3600, 2),
        'active_days_count': active_days,
        'productivity_score': min(100, round(active_days * 3.33 + (50 - min(task_completion_times / 3600, 50)))),  # 生产力评分
        'focus_index': round((active_days / 30) * 100, 1) if active_days > 0 else 0,  # 专注度指数
    }