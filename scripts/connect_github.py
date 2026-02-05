#!/usr/bin/env python3
"""
GitHub仓库连接脚本
"""

import subprocess
import webbrowser
from pathlib import Path

def connect_to_github():
    """连接本地仓库到GitHub"""
    print("🔗 GitHub仓库连接向导")
    print("=" * 50)
    
    # 检查当前状态
    print("1. 检查当前Git状态...")
    
    # 添加所有未跟踪文件
    print("2. 添加所有文件...")
    result = subprocess.run(
        'git -C "D:/OPENPROJECT/High-Performance-Open" add .',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ 添加文件失败: {result.stderr}")
        return False
    
    print("✅ 文件添加成功")
    
    # 创建提交
    print("3. 创建开发环境配置提交...")
    result = subprocess.run(
        'git -C "D:/OPENPROJECT/High-Performance-Open" commit -m "feat: 添加开发环境配置和版本基线保护 [develop-config]"',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ 提交失败: {result.stderr}")
        return False
    
    print("✅ 提交创建成功")
    
    print("\n" + "=" * 50)
    print("📋 下一步手动操作:")
    print("=" * 50)
    
    print("\n4. 在GitHub上创建新仓库:")
    print("   🌐 访问: https://github.com/new")
    print("   📁 仓库名: High-Performance-Open")
    print("   📝 描述: 个人成长管理平台 - 智能任务推荐系统")
    print("   🔒 可见性: Public 或 Private")
    print("   ❌ 不要勾选: 'Initialize with README'")
    
    print("\n5. 连接远程仓库 (替换YOUR_USERNAME):")
    print("   ```bash")
    print("   cd \"D:\\OPENPROJECT\\High-Performance-Open\"")
    print("   git remote add origin https://github.com/YOUR_USERNAME/High-Performance-Open.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    print("   git push -u origin develop")
    print("   git push -u origin feature/intelligent-recommendations")
    print("   ```")
    
    print("\n6. 推送所有分支和标签:")
    print("   ```bash")
    print("   git push --all")
    print("   git push --tags")
    print("   ```")
    
    print("\n7. 验证GitHub仓库:")
    print("   🌐 访问: https://github.com/YOUR_USERNAME/High-Performance-Open")
    print("   👀 检查文件是否同步")
    print("   🏷️ 检查v1.0.0标签是否存在")
    
    print("\n" + "=" * 50)
    print("🎉 准备就绪！请按照上述步骤操作")
    print("=" * 50)
    
    # 提供GitHub链接
    try:
        webbrowser.open("https://github.com/new")
        print("🌐 已自动打开GitHub创建页面")
    except:
        print("📋 请手动访问: https://github.com/new")
    
    return True

if __name__ == "__main__":
    connect_to_github()