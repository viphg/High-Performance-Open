from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, extract, func
from app.models import Task, Goal, User, Notification
from app.services.achievements_service import AchievementService
from datetime import datetime, timedelta
from typing import List, Dict


class NotificationService:
    """通知服务"""
    
    @staticmethod
    def create_notification(db: Session, user_id: int, title: str, message: str, 
                            notification_type: str, related_id: Optional[int] = None, 
                            action_required: bool = False, action_url: Optional[str] = None,
                            expires_hours: Optional[int] = None) -> Notification:
        """创建通知"""
        expires_at = datetime.now() + timedelta(hours=expires_hours) if expires_hours else None
        
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            related_id=related_id,
            is_action_required=action_required,
            action_url=action_url,
            expires_at=expires_at
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def check_goal_deadlines(db: Session, user_id: int) -> List[Notification]:
        """检查目标截止日期"""
        notifications = []
        
        # 查找即将到期的目标（3天内）
        upcoming_deadlines = db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status != 'completed',
            Goal.target_date.isnot(None),
            Goal.target_date <= datetime.now() + timedelta(days=3),
            Goal.target_date >= datetime.now()
        ).all()
        
        for goal in upcoming_deadlines:
            days_left = (goal.target_date - datetime.now()).days
            
            if days_left == 0:
                urgency = "今天截止"
                title = "目标即将到期！"
            elif days_left == 1:
                urgency = "明天截止"
                title = "目标明天到期"
            else:
                urgency = f"{days_left}天后到期"
                title = "目标即将到期"
            
            message = f"目标「{goal.title}」{urgency}"
            
            # 检查是否已存在相同通知
            existing = db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.type == 'goal_deadline',
                Notification.related_id == goal.id,
                Notification.created_at >= datetime.now() - timedelta(hours=1)
            ).first()
            
            if not existing:
                notification = NotificationService.create_notification(
                    db=db,
                    user_id=user_id,
                    title=title,
                    message=message,
                    notification_type='goal_deadline',
                    related_id=goal.id,
                    action_required=True,
                    action_url=f"/goals/{goal.id}",
                    expires_hours=24
                )
                notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def check_task_reminders(db: Session, user_id: int) -> List[Notification]:
        """检查任务提醒"""
        notifications = []
        
        # 查找今天应该开始但未开始的任务
        today_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            or_(
                and_(Task.status == 'not_started', Task.start_date <= datetime.now()),
                and_(Task.status == 'in_progress', Task.completed_at < datetime.now() - timedelta(days=3))  # 进行中超过3天
            )
        ).all()
        
        for task in today_tasks:
            if task.status == 'not_started':
                title = "任务等待开始"
                message = f"任务「{task.title}」今天应该开始"
                notification_type = 'task_start_reminder'
            else:
                title = "任务进度滞后"
                message = f"任务「{task.title}」已进行3天未更新，请检查进度"
                notification_type = 'task_progress_lag'
            
            # 检查是否已存在相同通知
            existing = db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.type == notification_type,
                Notification.related_id == task.id,
                Notification.created_at >= datetime.now() - timedelta(hours=12)
            ).first()
            
            if not existing:
                notification = NotificationService.create_notification(
                    db=db,
                    user_id=user_id,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    related_id=task.id,
                    action_required=True,
                    action_url=f"/tasks/{task.id}",
                    expires_hours=12
                )
                notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def create_achievement_notification(db: Session, user_id: int, achievement_title: str, points: int) -> Notification:
        """创建成就解锁通知"""
        title = "🎉 新成就解锁！"
        message = f"恭喜你解锁了「{achievement_title}」成就，获得 {points} 积分！"
        
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title=title,
            message=message,
            notification_type='achievement_unlocked',
            action_required=False,
            action_url="/achievements",
            expires_hours=168  # 7天后过期
        )
    
    @staticmethod
    def create_weekly_summary(db: Session, user_id: int) -> Notification:
        """创建周总结通知"""
        # 获取本周统计数据
        week_ago = datetime.now() - timedelta(days=7)
        
        completed_tasks = db.query(func.count(Task.id)).filter(
            Task.user_id == user_id,
            Task.status == 'completed',
            Task.completed_at >= week_ago
        ).scalar()
        
        completed_goals = db.query(func.count(Goal.id)).filter(
            Goal.user_id == user_id,
            Goal.status == 'completed',
            Goal.updated_at >= week_ago
        ).scalar()
        
        if completed_tasks > 0 or completed_goals > 0:
            title = "📊 本周总结"
            message = f"本周你完成了 {completed_tasks} 个任务和 {completed_goals} 个目标，继续加油！"
            
            return NotificationService.create_notification(
                db=db,
                user_id=user_id,
                title=title,
                message=message,
                notification_type='weekly_summary',
                action_required=False,
                expires_hours=168
            )
        
        return None
    
    @staticmethod
    def get_user_notifications(db: Session, user_id: int, unread_only: bool = False, limit: int = 50) -> List[Notification]:
        """获取用户通知列表"""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        query = query.order_by(Notification.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def mark_as_read(db: Session, user_id: int, notification_id: int) -> bool:
        """标记通知为已读"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification and not notification.is_read:
            notification.is_read = True
            db.add(notification)
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def cleanup_expired_notifications(db: Session, user_id: int) -> int:
        """清理过期通知"""
        expired_count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.expires_at < datetime.now()
        ).count()
        
        db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.expires_at < datetime.now()
        ).delete()
        
        db.commit()
        return expired_count


class ReminderService:
    """提醒服务"""
    
    @staticmethod
    def generate_smart_reminders(db: Session, user_id: int) -> List[Dict]:
        """生成智能提醒"""
        reminders = []
        
        # 分析用户的任务模式
        user_tasks = db.query(Task).filter(Task.user_id == user_id).all()
        
        if not user_tasks:
            return reminders
        
        # 找出高优先级任务
        high_priority_tasks = [t for t in user_tasks if t.priority == 2 and t.status != 'completed']
        
        for task in high_priority_tasks:
            if task.due_date:
                days_left = (task.due_date - datetime.now()).days
                
                if days_left <= 1:
                    reminders.append({
                        'type': 'urgent',
                        'title': f"高优先级任务即将到期",
                        'message': f"「{task.title}」{days_left == 0 and '今天' or '明天'}到期",
                        'task_id': task.id,
                        'priority': 'high'
                    })
        
        # 找出长时间未更新的任务
        stale_threshold = datetime.now() - timedelta(days=7)
        stale_tasks = [t for t in user_tasks 
                      if t.status == 'in_progress' and t.updated_at < stale_threshold]
        
        for task in stale_tasks:
            days_stale = (datetime.now() - task.updated_at).days
            reminders.append({
                'type': 'stale',
                'title': f"任务进度滞后",
                'message': f"「{task.title}」已{days_stale}天未更新，请检查进度",
                'task_id': task.id,
                'priority': 'medium'
            })
        
        return reminders