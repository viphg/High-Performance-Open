from datetime import timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional


# 用户相关 Schema
class UserBase(BaseModel):
    """用户基础信息"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """创建用户"""
    password: str


class UserUpdate(BaseModel):
    """更新用户"""
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """用户响应"""
    id: int
    is_active: bool
    is_admin: bool
    
    class Config:
        orm_mode = True


# 认证相关 Schema
class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
