from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import UserCreate, UserResponse
from app.utils.dependencies import get_current_user
from app.models import User
from app.utils.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    request: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    current_user.full_name = request.full_name or current_user.full_name
    current_user.email = request.email or current_user.email
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
