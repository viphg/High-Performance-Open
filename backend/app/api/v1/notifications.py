from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.utils.dependencies import get_current_user
from app.models import User, Notification, NotificationPreference
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    NotificationCountResponse
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    unread_only: bool = Query(False, description="只显示未读"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的通知列表"""
    service = NotificationService(db)
    notifications = service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset
    )
    
    total = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).count()
    
    unread_count = service.get_unread_count(current_user.id)
    
    return NotificationListResponse(
        total=total,
        unread_count=unread_count,
        notifications=notifications
    )


@router.get("/count", response_model=NotificationCountResponse)
async def get_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取未读通知数量"""
    service = NotificationService(db)
    unread_count = service.get_unread_count(current_user.id)
    
    return NotificationCountResponse(unread_count=unread_count)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记通知为已读"""
    service = NotificationService(db)
    success = service.mark_as_read(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    return notification


@router.post("/read-all")
async def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记所有通知为已读"""
    service = NotificationService(db)
    count = service.mark_all_as_read(current_user.id)
    
    return {"message": f"已标记 {count} 条通知为已读"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除通知"""
    service = NotificationService(db)
    success = service.delete_notification(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    return {"message": "通知已删除"}


@router.get("/preferences", response_model=NotificationPreferenceResponse)
async def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取通知偏好设置"""
    preference = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()
    
    if not preference:
        # 创建默认偏好
        preference = NotificationPreference(user_id=current_user.id)
        db.add(preference)
        db.commit()
        db.refresh(preference)
    
    return preference


@router.put("/preferences", response_model=NotificationPreferenceResponse)
async def update_preferences(
    data: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新通知偏好设置"""
    preference = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()
    
    if not preference:
        preference = NotificationPreference(user_id=current_user.id)
        db.add(preference)
    
    # 更新字段
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preference, field, value)
    
    db.commit()
    db.refresh(preference)
    
    return preference
