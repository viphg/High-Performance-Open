from datetime import timedelta
from sqlalchemy.orm import Session
from app.models import User
from app.utils.security import hash_password, verify_password, create_access_token
from app.config import settings
from fastapi import HTTPException, status


class UserService:
    """用户服务"""
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        """通过用户名获取用户"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """通过邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User | None:
        """通过 ID 获取用户"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str, full_name: str = None) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        if UserService.get_user_by_username(db, username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        if UserService.get_user_by_email(db, email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="邮箱已被注册"
            )
        
        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


class AuthService:
    """认证服务"""
    
    @staticmethod
    def login(db: Session, username: str, password: str) -> tuple[str, int, User]:
        """用户登录"""
        user = UserService.get_user_by_username(db, username)
        
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户已禁用"
            )
        
        # 创建 Token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES, user
    
    @staticmethod
    def register(db: Session, username: str, email: str, password: str, full_name: str = None) -> User:
        """用户注册"""
        return UserService.create_user(db, username, email, password, full_name)
