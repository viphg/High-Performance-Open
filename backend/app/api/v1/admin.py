from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app.schemas.auth import UserResponse
from app.utils.dependencies import get_current_admin_user
from app.models import User
from app.utils.security import hash_password
from pydantic import BaseModel
from email_validator import validate_email, EmailNotValidError

router = APIRouter(prefix="/admin", tags=["admin"])


class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int
    users: List[UserResponse]
    
    class Config:
        orm_mode = True


class UserUpdateAdmin(BaseModel):
    """管理员更新用户"""
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    full_name: Optional[str] = None
    email: Optional[str] = None


class PasswordResetRequest(BaseModel):
    """密码重置请求"""
    new_password: str
    confirm_password: str
    
    class Config:
        min_anystr_length = 6


class AdminStats(BaseModel):
    """管理员统计信息"""
    total_users: int
    active_users: int
    inactive_users: int
    admin_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int


@router.get("/users", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    is_active: Optional[bool] = Query(None, description="筛选活跃用户"),
    is_admin: Optional[bool] = Query(None, description="筛选管理员用户"),
    search: Optional[str] = Query(None, description="搜索用户名或邮箱"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取用户列表（管理员权限）"""
    query = db.query(User)
    
    # 应用筛选条件
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.username.ilike(search_term)) | 
            (User.email.ilike(search_term))
        )
    
    # 获取总数
    total = query.count()
    
    # 获取分页数据
    users = query.offset(skip).limit(limit).all()
    
    return UserListResponse(total=total, users=users)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取用户详情（管理员权限）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    update_data: UserUpdateAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新用户信息（管理员权限）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能修改自己的管理员权限
    if user.id == current_user.id and update_data.is_admin is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的管理员权限"
        )
    
    # 更新字段
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
    if update_data.is_admin is not None:
        user.is_admin = update_data.is_admin
    if update_data.full_name is not None:
        user.full_name = update_data.full_name
    if update_data.email is not None:
        # 验证邮箱格式
        try:
            validate_email(update_data.email)
        except EmailNotValidError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱格式无效"
            )
        # 检查邮箱是否已被其他用户使用
        existing_user = db.query(User).filter(
            User.email == update_data.email,
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被其他用户使用"
            )
        user.email = update_data.email
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除用户（管理员权限）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )
    
    # 删除用户（软删除：将is_active设为False）
    user.is_active = False
    db.commit()
    
    return None


@router.post("/users/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """激活用户（管理员权限）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user.is_active = True
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/users/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """禁用用户（管理员权限）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能禁用自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用自己"
        )
    
    user.is_active = False
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/users/{user_id}/set-admin", response_model=UserResponse)
async def set_user_admin(
    user_id: int,
    is_admin: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """设置/取消用户管理员权限"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能修改自己的权限
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的管理员权限"
        )
    
    user.is_admin = is_admin
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/users/{user_id}/reset-password", response_model=UserResponse)
async def reset_user_password(
    user_id: int,
    password_data: PasswordResetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """重置用户密码（管理员权限）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 验证两次密码是否一致
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="两次输入的密码不一致"
        )
    
    # 验证密码长度
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少为6位"
        )
    
    # 更新密码
    user.hashed_password = hash_password(password_data.new_password)
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取管理员统计信息"""
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    inactive_users = db.query(User).filter(User.is_active == False).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    
    new_users_today = db.query(User).filter(
        func.date(User.created_at) == today
    ).count()
    
    new_users_this_week = db.query(User).filter(
        func.date(User.created_at) >= week_ago
    ).count()
    
    new_users_this_month = db.query(User).filter(
        func.date(User.created_at) >= month_ago
    ).count()
    
    return AdminStats(
        total_users=total_users,
        active_users=active_users,
        inactive_users=inactive_users,
        admin_users=admin_users,
        new_users_today=new_users_today,
        new_users_this_week=new_users_this_week,
        new_users_this_month=new_users_this_month
    )
