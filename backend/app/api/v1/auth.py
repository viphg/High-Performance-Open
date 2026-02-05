from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, LoginResponse, UserCreate, UserResponse
from app.services.auth import AuthService
from app.utils.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """用户登录"""
    access_token, expires_in, user = AuthService.login(db, request.username, request.password)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in * 60,  # 转换为秒
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_admin": user.is_admin
        }
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserCreate,
    db: Session = Depends(get_db)
):
    """用户注册"""
    user = AuthService.register(db, request.username, request.email, request.password, request.full_name)
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return current_user


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """用户登出"""
    return {"message": "登出成功"}


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    request: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    current_user.full_name = request.full_name
    current_user.email = request.email
    if hasattr(request, 'password') and request.password:
        from app.utils.security import hash_password
        current_user.password_hash = hash_password(request.password)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
