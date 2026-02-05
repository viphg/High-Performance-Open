from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "High-Performance"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@postgres:5432/high_performance_open"
    SQLALCHEMY_ECHO: bool = True
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis 配置
    REDIS_URL: str = "redis://redis:6379/0"
    
    # 邮件配置
    SMTP_SERVER: str = "smtp.sendgrid.net"
    SMTP_PORT: int = 587
    SMTP_USER: str = "apikey"
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@highperformance.com"
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5175", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
