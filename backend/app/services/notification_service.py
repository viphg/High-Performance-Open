from typing import Optional, Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from app.models import User, Notification, NotificationPreference
from app.models.task import Task
from app.models.goal import Goal
from app.services.email_service import email_service
from app.services.notification_types import (
    NotificationType, 
    NotificationChannel,
    NOTIFICATION_TEMPLATES
)

logger = logging.getLogger(__name__)


class NotificationService:
    """通知服务 - 核心业务逻辑"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _get_user_preference(self, user_id: int) -> Optional[NotificationPreference]:
        """获取用户通知偏好"""
        preference = self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        
        if not preference:
            # 创建默认偏好
            preference = NotificationPreference(user_id=user_id)
            self.db.add(preference)
            self.db.commit()
            self.db.refresh(preference)
        
        return preference
    
    def _should_send_channel(
        self, 
        preference: NotificationPreference, 
        notification_type: NotificationType,
        channel: NotificationChannel
    ) -> bool:
        """检查是否应该通过指定渠道发送"""
        if channel == NotificationChannel.WEB:
            # 站内信默认都发送
            return True
        
        if channel == NotificationChannel.EMAIL:
            # 根据通知类型和用户偏好决定是否发送邮件
            if notification_type in [NotificationType.TASK_DUE_SOON, NotificationType.TASK_OVERDUE]:
                return preference.task_due_email
            elif notification_type in [NotificationType.GOAL_PROGRESS, NotificationType.GOAL_COMPLETED]:
                return preference.goal_progress_email
            elif notification_type == NotificationType.ACHIEVEMENT_UNLOCKED:
                return preference.achievement_email
            elif notification_type == NotificationType.DAILY_DIGEST:
                return preference.daily_digest and preference.digest_email
            elif notification_type == NotificationType.SYSTEM_ANNOUNCEMENT:
                return preference.system_announcement_email
            elif notification_type == NotificationType.WELCOME:
                return True  # 欢迎邮件总是发送
        
        return False
    
    def create_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        content: str,
        related_type: Optional[str] = None,
        related_id: Optional[int] = None,
        channels: Optional[List[NotificationChannel]] = None
    ) -> Optional[Notification]:
        """创建通知"""
        try:
            # 获取用户偏好
            preference = self._get_user_preference(user_id)
            
            # 如果没有指定渠道，使用默认渠道
            if not channels:
                channels = [NotificationChannel.WEB]
            
            # 创建站内通知记录
            notification = Notification(
                user_id=user_id,
                type=notification_type.value,
                title=title,
                content=content,
                related_type=related_type,
                related_id=related_id,
                channel=",".join([c.value for c in channels]),
                is_read=False
            )
            
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            
            logger.info(f"创建通知成功: user_id={user_id}, type={notification_type.value}")
            return notification
            
        except Exception as e:
            logger.error(f"创建通知失败: {str(e)}")
            self.db.rollback()
            return None
    
    def send_notification(
        self,
        user: User,
        notification_type: NotificationType,
        template_data: Dict,
        related_type: Optional[str] = None,
        related_id: Optional[int] = None
    ) -> bool:
        """发送通知（站内信 + 邮件）"""
        try:
            # 获取通知模板
            template = NOTIFICATION_TEMPLATES.get(notification_type)
            if not template:
                logger.error(f"未找到通知模板: {notification_type}")
                return False
            
            # 渲染标题和内容
            title = template["title"].format(**template_data)
            content = template["content"].format(**template_data)
            
            # 获取用户偏好
            preference = self._get_user_preference(user.id)
            
            # 创建站内通知
            notification = self.create_notification(
                user_id=user.id,
                notification_type=notification_type,
                title=title,
                content=content,
                related_type=related_type,
                related_id=related_id
            )
            
            if not notification:
                return False
            
            # 发送邮件（如果需要）
            if self._should_send_channel(preference, notification_type, NotificationChannel.EMAIL):
                email_subject = template.get("email_subject", title).format(**template_data)
                email_body = template.get("email_body", content).format(**template_data)
                
                email_sent = email_service.send_email(
                    to_email=user.email,
                    subject=email_subject,
                    html_content=email_body
                )
                
                if email_sent:
                    notification.email_sent = True
                    self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}")
            return False
    
    # ========== 特定类型的通知方法 ==========
    
    def notify_task_due_soon(self, task: Task, hours_before: int = 24):
        """任务即将到期通知"""
        user = self.db.query(User).filter(User.id == task.user_id).first()
        if not user:
            return
        
        self.send_notification(
            user=user,
            notification_type=NotificationType.TASK_DUE_SOON,
            template_data={
                "task_title": task.title,
                "task_description": task.description or "无描述",
                "hours": hours_before,
                "task_link": f"http://localhost:5176/tasks/{task.id}"
            },
            related_type="task",
            related_id=task.id
        )
    
    def notify_task_overdue(self, task: Task):
        """任务逾期通知"""
        user = self.db.query(User).filter(User.id == task.user_id).first()
        if not user:
            return
        
        # 计算逾期天数
        days_overdue = (datetime.now() - task.due_date).days if task.due_date else 0
        
        self.send_notification(
            user=user,
            notification_type=NotificationType.TASK_OVERDUE,
            template_data={
                "task_title": task.title,
                "days": max(1, days_overdue),
                "task_link": f"http://localhost:5176/tasks/{task.id}"
            },
            related_type="task",
            related_id=task.id
        )
    
    def notify_task_completed(self, task: Task):
        """任务完成通知"""
        user = self.db.query(User).filter(User.id == task.user_id).first()
        if not user:
            return
        
        self.send_notification(
            user=user,
            notification_type=NotificationType.TASK_COMPLETED,
            template_data={
                "task_title": task.title
            },
            related_type="task",
            related_id=task.id
        )
    
    def notify_goal_progress(self, goal: Goal):
        """目标进度更新通知"""
        user = self.db.query(User).filter(User.id == goal.user_id).first()
        if not user:
            return
        
        self.send_notification(
            user=user,
            notification_type=NotificationType.GOAL_PROGRESS,
            template_data={
                "goal_title": goal.title,
                "progress": int(goal.progress)
            },
            related_type="goal",
            related_id=goal.id
        )
    
    def notify_goal_completed(self, goal: Goal):
        """目标完成通知"""
        user = self.db.query(User).filter(User.id == goal.user_id).first()
        if not user:
            return
        
        self.send_notification(
            user=user,
            notification_type=NotificationType.GOAL_COMPLETED,
            template_data={
                "goal_title": goal.title
            },
            related_type="goal",
            related_id=goal.id
        )
    
    def notify_welcome(self, user: User):
        """欢迎新用户通知"""
        # 发送站内通知
        self.send_notification(
            user=user,
            notification_type=NotificationType.WELCOME,
            template_data={
                "username": user.username,
                "dashboard_link": "http://localhost:5176/dashboard"
            }
        )
        
        # 同时发送欢迎邮件
        email_service.send_welcome_email(user)
    
    def notify_achievement_unlocked(self, user: User, achievement_title: str, description: str, points: int):
        """成就解锁通知"""
        self.send_notification(
            user=user,
            notification_type=NotificationType.ACHIEVEMENT_UNLOCKED,
            template_data={
                "achievement_title": achievement_title,
                "achievement_description": description,
                "points": points
            },
            related_type="achievement"
        )
    
    # ========== 查询方法 ==========
    
    def get_user_notifications(
        self, 
        user_id: int, 
        unread_only: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> List[Notification]:
        """获取用户通知列表"""
        query = self.db.query(Notification).filter(
            Notification.user_id == user_id
        )
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    def get_unread_count(self, user_id: int) -> int:
        """获取未读通知数量"""
        return self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).count()
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """标记通知为已读"""
        try:
            notification = self.db.query(Notification).filter(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            ).first()
            
            if notification:
                notification.is_read = True
                notification.read_at = datetime.now()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"标记已读失败: {str(e)}")
            return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """标记所有通知为已读"""
        try:
            count = self.db.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            ).update({
                "is_read": True,
                "read_at": datetime.now()
            })
            self.db.commit()
            return count
        except Exception as e:
            logger.error(f"标记全部已读失败: {str(e)}")
            return 0
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """删除通知"""
        try:
            notification = self.db.query(Notification).filter(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            ).first()
            
            if notification:
                self.db.delete(notification)
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"删除通知失败: {str(e)}")
            return False
