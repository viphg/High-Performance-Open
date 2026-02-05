#!/usr/bin/env python
"""
创建测试用户脚本
"""
import sys
sys.path.insert(0, '/app')

from app.database import SessionLocal
from app.services.auth import AuthService

def create_test_user():
    """创建测试用户"""
    db = SessionLocal()
    
    try:
        user = AuthService.register(
            db,
            username="testuser",
            email="test@example.com",
            password="test123",  # 使用更短的密码
            full_name="Test User"
        )
        print(f"✅ 测试用户创建成功！")
        print(f"   用户名: {user.username}")
        print(f"   邮箱: {user.email}")
        print(f"   ID: {user.id}")
    except Exception as e:
        print(f"❌ 创建失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
