#!/usr/bin/env python3
"""
配置文件验证脚本
"""

import os
from pathlib import Path

def check_config_files():
    """检查配置文件是否存在"""
    project_root = Path("D:/OPENPROJECT/High-Performance-Open")
    
    print("🔍 验证配置文件...")
    
    # 检查后端配置
    backend_env = project_root / "backend" / ".env.dev"
    if backend_env.exists():
        print("✅ 后端开发配置文件存在: backend/.env.dev")
        with open(backend_env, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"   📊 配置行数: {len(lines)}")
            
            # 检查关键配置
            content = f.read()
            if "ENABLE_INTELLIGENT_RECOMMENDATIONS=True" in content:
                print("   ✅ 智能推荐功能已启用")
            if "ML_MODEL_PATH" in content:
                print("   ✅ 机器学习配置已添加")
            if "high_performance_open_dev" in content:
                print("   ✅ 开发数据库已配置")
    else:
        print("❌ 后端开发配置文件不存在")
    
    # 检查前端配置
    frontend_env = project_root / "frontend" / ".env.dev"
    if frontend_env.exists():
        print("✅ 前端开发配置文件存在: frontend/.env.dev")
        with open(frontend_env, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"   📊 配置行数: {len(lines)}")
            
            # 检查关键配置
            content = f.read()
            if "VITE_ENABLE_INTELLIGENT_RECOMMENDATIONS=true" in content:
                print("   ✅ 前端智能推荐功能已启用")
            if "VITE_RECOMMENDATION_API_BASE_URL" in content:
                print("   ✅ 推荐API地址已配置")
            if "VITE_API_URL=http://localhost:8001/api" in content:
                print("   ✅ API地址已更新")
    else:
        print("❌ 前端开发配置文件不存在")
    
    print("\n📋 配置验证完成!")

if __name__ == "__main__":
    check_config_files()