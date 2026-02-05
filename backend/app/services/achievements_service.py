from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from app.models.achievement import Achievement
from app.models.achievements import UserAchievement, UserStreak, AchievementType
from app.models import Task, Goal, User
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class AchievementService:
    """成就系统服务"""
    
    @staticmethod
    def check_task_master(db: Session, user_id: int) -> None:
        """检查任务大师成就：完成10个任务"""
        task_count = db.query(func.count(Task.id)).filter(
            Task.user_id == user_id,
            Task.status == 'completed'
        ).scalar()
        
        AchievementService._unlock_achievement(db, user_id, AchievementType.TASK_MASTER, task_count, 10)
    
    @staticmethod
    def check_goal_achiever(db: Session, user_id: int) -> None:
        """检查目标达成者：完成5个目标"""
        goal_count = db.query(func.count(Goal.id)).filter(
            Goal.user_id == user_id,
            Goal.status == 'completed'
        ).scalar()
        
        AchievementService._unlock_achievement(db, user_id, AchievementType.GOAL_ACHIEVER, goal_count, 5)
    
    @staticmethod
    def check_early_bird(db: Session, user_id: int) -> None:
        """检查早鸟成就：早上8点前完成任务"""
        morning_tasks = db.query(func.count(Task.id)).filter(
            Task.user_id == user_id,
            Task.status == 'completed',
            extract('hour', Task.completed_at) < 8
        ).scalar()
        
        AchievementService._unlock_achievement(db, user_id, AchievementType.EARLY_BIRD, morning_tasks, 1)
    
    @staticmethod
    def check_deadline_defender(db: Session, user_id: int) -> None:
        """检查截止日期守护者：在截止日期前完成任务"""
        on_time_tasks = db.query(func.count(Task.id)).filter(
            Task.user_id == user_id,
            Task.status == 'completed',
            Task.completed_at <= Task.due_date
        ).scalar()
        
        AchievementService._unlock_achievement(db, user_id, AchievementType.DEADLINE_DEFENDER, on_time_tasks, 5)
    
    @staticmethod
    def check_productivity(db: Session, user_id: int) -> None:
        """检查生产力忍者：一天完成5个任务"""
        today = datetime.now().date()
        today_tasks = db.query(func.count(Task.id)).filter(
            Task.user_id == user_id,
            Task.status == 'completed',
            extract('date', Task.completed_at) == today
        ).scalar()
        
        AchievementService._unlock_achievement(db, user_id, AchievementType.PRODUCTIVITY_NINJA, today_tasks, 5)
    
    @staticmethod
    def check_consistent_performer(db: Session, user_id: int) -> None:
        """检查持续表现者：连续7天完成任务"""
        last_7_days = datetime.now() - timedelta(days=7)
        active_days = db.query(func.count(func.distinct(extract('date', Task.completed_at)))).filter(
            Task.user_id == user_id,
            Task.status == 'completed',
            Task.completed_at >= last_7_days
        ).scalar()
        
        AchievementService._unlock_achievement(db, user_id, AchievementType.CONSISTENT_PERFORMER, active_days, 7)
    
    @staticmethod
    def _unlock_achievement(db: Session, user_id: int, achievement_type: AchievementType, current_value: int, target_value: int) -> None:
        """解锁成就"""
        # 查找成就定义
        achievement = db.query(Achievement).filter(
            Achievement.type == achievement_type,
            Achievement.condition_value == target_value
        ).first()
        
        if not achievement:
            return
        
        # 查找用户是否已解锁
        user_achievement = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement.id
        ).first()
        
        if user_achievement:
            # 更新进度
            if not user_achievement.is_completed and current_value >= target_value:
                user_achievement.progress_value = target_value
                user_achievement.is_completed = True
                db.add(user_achievement)
        elif not user_achievement:
            # 创建新的解锁记录
            is_completed = current_value >= target_value
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id,
                progress_value=min(current_value, target_value),
                is_completed=is_completed
            )
            db.add(user_achievement)
        
        db.commit()


class StreakService:
    """连续记录服务"""
    
    @staticmethod
    def update_daily_task_streak(db: Session, user_id: int) -> Dict:
        """更新每日任务连续记录"""
        today = datetime.now().date()
        
        # 查找或创建连续记录
        streak = db.query(UserStreak).filter(
            UserStreak.user_id == user_id,
            UserStreak.streak_type == 'daily_task'
        ).first()
        
        if not streak:
            streak = UserStreak(
                user_id=user_id,
                streak_type='daily_task',
                current_streak=0,
                max_streak=0
            )
            db.add(streak)
            db.flush()
        
        # 检查今天是否有完成任务
        today_completed = db.query(func.count(Task.id)).filter(
            Task.user_id == user_id,
            Task.status == 'completed',
            extract('date', Task.completed_at) == today
        ).scalar() > 0
        
        # 获取昨天的日期
        yesterday = today - timedelta(days=1)
        yesterday_completed = db.query(func.count(Task.id)).filter(
            Task.user_id == user_id,
            Task.status == 'completed',
            extract('date', Task.completed_at) == yesterday
        ).scalar() > 0
        
        if yesterday_completed and not streak.last_activity_date:
            # 如果昨天完成了但最后活动日期为空，重置连续记录
            streak.current_streak = 1 if today_completed else 0
        elif today_completed:
            # 如果今天完成了，增加连续记录
            if yesterday_completed and streak.last_activity_date == yesterday:
                streak.current_streak += 1
            else:
                streak.current_streak = 1
            
            # 更新最大连续记录
            streak.max_streak = max(streak.max_streak, streak.current_streak)
        
        streak.last_activity_date = datetime.now() if today_completed else streak.last_activity_date
        db.add(streak)
        db.commit()
        
        return {
            'current_streak': streak.current_streak,
            'max_streak': streak.max_streak,
            'is_active_today': today_completed
        }