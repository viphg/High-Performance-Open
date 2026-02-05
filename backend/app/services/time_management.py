from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, or_
from app.models import Task, Goal, User
from app.services.analytics import get_productivity_metrics
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class TimeManagementService:
    """时间管理服务"""
    
    @staticmethod
    def get_time_tracking_summary(db: Session, user_id: int, days: int = 30) -> Dict:
        """获取时间追踪汇总"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 获取时间分布统计
        time_distribution = db.query(
            func.count(Task.id).label('task_count'),
            Task.priority.label('priority_level'),
            extract('hour', Task.created_at).label('hour')
        ).filter(
            Task.user_id == user_id,
            Task.created_at >= start_date,
            Task.created_at <= end_date
        ).group_by(
            Task.priority,
            extract('hour', Task.created_at)
        ).all()
        
        # 按优先级和时间分组
        hourly_stats = {}
        priority_stats = {0: 0, 1: 0, 2: 0}  # 低、中、高
        
        for stat in time_distribution:
            hour = stat.hour
            priority = stat.priority
            count = stat.task_count
            
            if hour not in hourly_stats:
                hourly_stats[hour] = {'low': 0, 'medium': 0, 'high': 0}
            
            if priority == 0:
                hourly_stats[hour]['low'] = count
            elif priority == 1:
                hourly_stats[hour]['medium'] = count
            elif priority == 2:
                hourly_stats[hour]['high'] = count
            
            priority_stats[priority] += count
        
        # 计算平均响应时间（创建到开始的时间）
        avg_start_time = db.query(
            func.avg(func.extract('epoch', func.coalesce(Task.started_at, Task.created_at)) - func.extract('epoch', Task.created_at))
        ).filter(
            Task.user_id == user_id,
            Task.status != 'not_started',
            Task.started_at.isnot(None),
            Task.created_at >= start_date
        ).scalar() or 0
        
        # 获取最佳工作时间（按任务完成率）
        best_hour = max(hourly_stats.items(), key=lambda x: sum(x[1].values()), default=(0, {})) if hourly_stats else (0, {})
        
        return {
            'period_days': days,
            'total_tasks': sum(priority_stats.values()),
            'priority_distribution': {
                'low': priority_stats[0],
                'medium': priority_stats[1],
                'high': priority_stats[2]
            },
            'hourly_distribution': hourly_stats,
            'best_productive_hour': best_hour[0],
            'best_productive_hour_data': best_hour[1],
            'avg_start_delay_hours': avg_start_time / 3600,  # 转换为小时
            'focus_period_hours': '9-17',  # 建议的专注时间段
        }
    
    @staticmethod
    def get_goal_completion_patterns(db: Session, user_id: int) -> Dict:
        """获取目标完成模式分析"""
        # 获取已完成的的目标
        completed_goals = db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == 'completed'
        ).all()
        
        if not completed_goals:
            return {'message': '暂无已完成的目标'}
        
        # 分析完成时间模式
        completion_times = [g.created_at for g in completed_goals]
        completion_hours = [c.hour for c in completion_times]
        completion_days = [c.weekday() for c in completion_times]
        
        # 按星期统计
        weekday_counts = {}
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        for day, name in enumerate(weekday_names):
            weekday_counts[name] = sum(1 for d in completion_days if d == day)
        
        # 计算平均完成时间
        avg_completion_days = sum([(g.created_at - g.created_at).days for g in completed_goals]) / len(completed_goals)
        
        return {
            'total_completed_goals': len(completed_goals),
            'weekday_completion_pattern': weekday_counts,
            'most_productive_weekday': max(weekday_counts.items(), key=lambda x: x[1])[0] if weekday_counts else None,
            'avg_completion_days': round(avg_completion_days, 1),
            'completion_trend': 'improving' if len(completed_goals) > 1 else 'stable',
            'category_analysis': TimeManagementService._analyze_category_patterns(completed_goals)
        }
    
    @staticmethod
    def _analyze_category_patterns(completed_goals: List) -> Dict:
        """分析类别模式"""
        category_counts = {}
        for goal in completed_goals:
            category = goal.category or 'uncategorized'
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            'category_distribution': category_counts,
            'most_successful_category': max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None,
            'category_success_rates': {
                cat: round(count / len(completed_goals) * 100, 1) 
                for cat, count in category_counts.items()
            }
        }
    
    @staticmethod
    def get_time_efficiency_metrics(db: Session, user_id: int) -> Dict:
        """获取时间效率指标"""
        # 获取所有任务
        all_tasks = db.query(Task).filter(Task.user_id == user_id).all()
        
        if not all_tasks:
            return {'message': '暂无任务数据'}
        
        # 计算效率指标
        total_tasks = len(all_tasks)
        completed_tasks = [t for t in all_tasks if t.status == 'completed']
        
        # 计算实际用时 vs 预估用时
        efficiency_data = []
        for task in completed_tasks:
            if task.estimated_hours and task.actual_hours > 0:
                efficiency_ratio = task.estimated_hours / task.actual_hours
                efficiency_data.append({
                    'title': task.title,
                    'estimated_hours': task.estimated_hours,
                    'actual_hours': task.actual_hours,
                    'efficiency_ratio': efficiency_ratio,
                    'is_efficient': efficiency_ratio >= 0.8
                })
        
        avg_efficiency = sum([e['efficiency_ratio'] for e in efficiency_data]) / len(efficiency_data) if efficiency_data else 1.0
        efficient_tasks = sum(1 for e in efficiency_data if e['is_efficient'])
        
        return {
            'total_tasks_analyzed': len(efficiency_data),
            'avg_efficiency_ratio': round(avg_efficiency, 2),
            'efficient_task_percentage': round(efficient_tasks / len(efficiency_data) * 100, 1) if efficiency_data else 0,
            'time_prediction_accuracy': round(100 / avg_efficiency, 1) if avg_efficiency > 0 else 100,
            'improvement_suggestions': TimeManagementService._get_efficiency_suggestions(avg_efficiency)
        }
    
    @staticmethod
    def _get_efficiency_suggestions(efficiency_ratio: float) -> List[str]:
        """获取效率提升建议"""
        suggestions = []
        
        if efficiency_ratio < 0.5:
            suggestions.append("建议分解大任务为小任务，提高完成率")
            suggestions.append("考虑使用时间块管理技巧，提高专注度")
            suggestions.append("回顾任务预估方法，积累经验")
        elif efficiency_ratio < 0.8:
            suggestions.append("尝试使用番茄工作法提高效率")
            suggestions.append("减少干扰因素，创造专注环境")
            suggestions.append("定期回顾和调整时间估算")
        else:
            suggestions.append("保持当前的工作方式，效率很高！")
        
        return suggestions