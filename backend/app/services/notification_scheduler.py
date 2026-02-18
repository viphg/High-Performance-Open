from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from app.database import SessionLocal
from app.models import User, NotificationPreference
from app.models.task import Task
from app.models.goal import Goal
from app.services.notification_service import NotificationService
from app.services.email_service import email_service
from app.services.notification_types import NotificationType

logger = logging.getLogger(__name__)


class NotificationScheduler:
    """通知定时任务调度器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """设置定时任务"""
        # 每30分钟检查一次即将到期的任务
        self.scheduler.add_job(
            self.check_due_tasks,
            'interval',
            minutes=30,
            id='check_due_tasks',
            replace_existing=True
        )
        
        # 每小时检查一次逾期任务
        self.scheduler.add_job(
            self.check_overdue_tasks,
            'interval',
            minutes=60,
            id='check_overdue_tasks',
            replace_existing=True
        )
        
        # 每天检查即将到期的目标（早上9点）
        self.scheduler.add_job(
            self.check_due_goals,
            CronTrigger(hour=9, minute=0),
            id='check_due_goals',
            replace_existing=True
        )
        
        # 发送每日摘要（根据用户设置的时间）
        self.scheduler.add_job(
            self.send_daily_digests,
            CronTrigger(hour=8, minute=0),
            id='send_daily_digests',
            replace_existing=True
        )
        
        logger.info("通知定时任务已设置")
    
    def start(self):
        """启动调度器"""
        self.scheduler.start()
        logger.info("通知调度器已启动")
    
    def shutdown(self):
        """关闭调度器"""
        self.scheduler.shutdown()
        logger.info("通知调度器已关闭")
    
    def check_due_tasks(self):
        """检查即将到期的任务"""
        db = SessionLocal()
        try:
            logger.info("开始检查即将到期的任务...")
            
            now = datetime.now()
            
            # 获取所有用户的偏好设置
            preferences = db.query(NotificationPreference).filter(
                NotificationPreference.task_due_web == True
            ).all()
            
            for pref in preferences:
                hours_before = pref.task_due_hours_before or 24
                deadline = now + timedelta(hours=hours_before)
                
                # 查找即将到期的任务
                due_tasks = db.query(Task).filter(
                    Task.user_id == pref.user_id,
                    Task.status != 'completed',
                    Task.due_date <= deadline,
                    Task.due_date > now
                ).all()
                
                # 为每个任务发送通知
                notification_service = NotificationService(db)
                for task in due_tasks:
                    # 检查是否已经发送过通知（24小时内）
                    existing_notification = db.query(Notification).filter(
                        Notification.user_id == pref.user_id,
                        Notification.related_type == 'task',
                        Notification.related_id == task.id,
                        Notification.type == NotificationType.TASK_DUE_SOON.value,
                        Notification.created_at >= now - timedelta(hours=24)
                    ).first()
                    
                    if not existing_notification:
                        notification_service.notify_task_due_soon(task, hours_before)
                        logger.info(f"发送任务到期提醒: user_id={pref.user_id}, task_id={task.id}")
            
            logger.info("即将到期任务检查完成")
            
        except Exception as e:
            logger.error(f"检查即将到期任务失败: {str(e)}")
        finally:
            db.close()
    
    def check_overdue_tasks(self):
        """检查逾期任务"""
        db = SessionLocal()
        try:
            logger.info("开始检查逾期任务...")
            
            now = datetime.now()
            
            # 查找所有已逾期的未完成任务
            overdue_tasks = db.query(Task).filter(
                Task.status != 'completed',
                Task.due_date < now
            ).all()
            
            notification_service = NotificationService(db)
            for task in overdue_tasks:
                # 检查是否已经发送过逾期通知（24小时内）
                existing_notification = db.query(Notification).filter(
                    Notification.user_id == task.user_id,
                    Notification.related_type == 'task',
                    Notification.related_id == task.id,
                    Notification.type == NotificationType.TASK_OVERDUE.value,
                    Notification.created_at >= now - timedelta(hours=24)
                ).first()
                
                if not existing_notification:
                    # 获取用户偏好
                    pref = db.query(NotificationPreference).filter(
                        NotificationPreference.user_id == task.user_id
                    ).first()
                    
                    if pref and pref.task_due_web:
                        notification_service.notify_task_overdue(task)
                        logger.info(f"发送任务逾期提醒: user_id={task.user_id}, task_id={task.id}")
            
            logger.info("逾期任务检查完成")
            
        except Exception as e:
            logger.error(f"检查逾期任务失败: {str(e)}")
        finally:
            db.close()
    
    def check_due_goals(self):
        """检查即将到期的目标"""
        db = SessionLocal()
        try:
            logger.info("开始检查即将到期的目标...")
            
            now = datetime.now()
            days_before = 7  # 提前7天提醒
            deadline = now + timedelta(days=days_before)
            
            # 查找即将到期的目标
            due_goals = db.query(Goal).filter(
                Goal.status != 'completed',
                Goal.target_date <= deadline,
                Goal.target_date > now
            ).all()
            
            notification_service = NotificationService(db)
            for goal in due_goals:
                # 检查是否已经发送过通知
                existing_notification = db.query(Notification).filter(
                    Notification.user_id == goal.user_id,
                    Notification.related_type == 'goal',
                    Notification.related_id == goal.id,
                    Notification.type == NotificationType.GOAL_DUE_SOON.value,
                    Notification.created_at >= now - timedelta(days=7)
                ).first()
                
                if not existing_notification:
                    notification_service.notify_goal_due_soon(goal)
                    logger.info(f"发送目标到期提醒: user_id={goal.user_id}, goal_id={goal.id}")
            
            logger.info("即将到期目标检查完成")
            
        except Exception as e:
            logger.error(f"检查即将到期目标失败: {str(e)}")
        finally:
            db.close()
    
    def send_daily_digests(self):
        """发送每日摘要"""
        db = SessionLocal()
        try:
            logger.info("开始发送每日摘要...")
            
            now = datetime.now()
            today = now.date()
            
            # 获取所有开启了每日摘要的用户
            preferences = db.query(NotificationPreference).filter(
                NotificationPreference.daily_digest == True
            ).all()
            
            for pref in preferences:
                # 检查是否应该发送（根据用户设置的时间）
                user = db.query(User).filter(User.id == pref.user_id).first()
                if not user:
                    continue
                
                # 获取用户的任务统计
                from sqlalchemy import func
                
                # 待办任务
                pending_tasks = db.query(Task).filter(
                    Task.user_id == pref.user_id,
                    Task.status != 'completed'
                ).all()
                
                # 今日截止的任务
                due_today_tasks = [t for t in pending_tasks if t.due_date and t.due_date.date() == today]
                
                # 已逾期的任务
                overdue_tasks = [t for t in pending_tasks if t.due_date and t.due_date.date() < today]
                
                # 准备摘要数据
                digest_data = {
                    "date": today.strftime("%Y年%m月%d日"),
                    "pending_count": len(pending_tasks),
                    "due_today_count": len(due_today_tasks),
                    "overdue_count": len(overdue_tasks),
                    "pending_tasks": [{"title": t.title, "due_date": t.due_date.strftime("%m-%d") if t.due_date else "无"} for t in pending_tasks[:5]],
                    "due_today_tasks": [{"title": t.title} for t in due_today_tasks],
                    "overdue_tasks": [{"title": t.title} for t in overdue_tasks]
                }
                
                # 发送邮件
                if pref.digest_email:
                    email_service.send_daily_digest(user, digest_data)
                
                # 发送站内通知
                if pref.digest_web:
                    notification_service = NotificationService(db)
                    notification_service.send_notification(
                        user=user,
                        notification_type=NotificationType.DAILY_DIGEST,
                        template_data=digest_data
                    )
                
                logger.info(f"发送每日摘要: user_id={pref.user_id}")
            
            logger.info("每日摘要发送完成")
            
        except Exception as e:
            logger.error(f"发送每日摘要失败: {str(e)}")
        finally:
            db.close()


# 全局调度器实例
notification_scheduler = NotificationScheduler()
