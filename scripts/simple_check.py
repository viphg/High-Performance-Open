#!/usr/bin/env python3
"""
配置文件验证脚本 - 简化版本，避免编码问题
"""

import os
from pathlib import Path

def check_config_files():
    """检查配置文件是否存在"""
    project_root = Path("D:/OPENPROJECT/High-Performance-Open")
    
    print("=== 配置文件验证 ===")
    
    # 检查后端配置
    backend_env = project_root / "backend" / ".env.dev"
    if backend_env.exists():
        print("OK: Backend dev config file exists")
        with open(backend_env, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if "ENABLE_INTELLIGENT_RECOMMENDATIONS=True" in content:
                print("OK: Backend intelligent recommendations enabled")
            if "ML_MODEL_PATH" in content:
                print("OK: Machine learning config added")
            if "high_performance_open_dev" in content:
                print("OK: Dev database configured")
    else:
        print("ERROR: Backend dev config file missing")
    
    # 检查前端配置
    frontend_env = project_root / "frontend" / ".env.dev"
    if frontend_env.exists():
        print("OK: Frontend dev config file exists")
        with open(frontend_env, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if "VITE_ENABLE_INTELLIGENT_RECOMMENDATIONS=true" in content:
                print("OK: Frontend intelligent recommendations enabled")
            if "VITE_RECOMMENDATION_API_BASE_URL" in content:
                print("OK: Recommendations API URL configured")
            if "VITE_API_URL=http://localhost:8001/api" in content:
                print("OK: API URL updated")
    else:
        print("ERROR: Frontend dev config file missing")
    
    print("=== 验证完成 ===")

if __name__ == "__main__":
    check_config_files()