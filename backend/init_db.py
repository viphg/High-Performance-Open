#!/usr/bin/env python
"""
快速数据库初始化脚本
"""
import sys
sys.path.insert(0, '/app')

from app.database import Base, engine
from app.models import User, Goal, Task, Achievement

def init_db():
    """初始化数据库表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库初始化完成！")

if __name__ == "__main__":
    init_db()
