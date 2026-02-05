#!/usr/bin/env python3
"""
Windows环境下版本基线保护设置脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """在Windows环境下安全地执行命令"""
    original_cwd = None
    try:
        if cwd:
            original_cwd = os.getcwd()
            os.chdir(cwd)
        
        print(f"执行命令: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if original_cwd:
            os.chdir(original_cwd)
        
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        if original_cwd:
            try:
                os.chdir(original_cwd)
            except:
                pass
        print(f"命令执行失败: {e}")
        return False, "", str(e)

def main():
    """主函数"""
    print("==========================================")
    print("High-Performance 版本基线保护设置")
    print("==========================================")
    print()
    
    # 项目路径
    project_path = Path("D:/OPENPROJECT/High-Performance-Open")
    
    if not project_path.exists():
        print(f"❌ 项目目录不存在: {project_path}")
        return False
    
    print(f"✅ 项目目录: {project_path}")
    
    # 切换到项目目录
    os.chdir(project_path)
    
    # 步骤1: 检查Git
    print("[1/8] 检查Git环境...")
    success, stdout, stderr = run_command("git --version")
    if not success:
        print("❌ Git未安装，请先安装Git: https://git-scm.com/")
        return False
    print("✅ Git已安装")
    
    # 步骤2: 初始化Git仓库
    print("[2/8] 初始化Git仓库...")
    if not Path(".git").exists():
        success, stdout, stderr = run_command("git init")
        if not success:
            print(f"❌ Git初始化失败: {stderr}")
            return False
        print("✅ Git仓库初始化成功")
    else:
        print("⚠️ Git仓库已存在，跳过初始化")
    
    # 步骤3: 配置Git用户信息
    print("[3/8] 配置Git用户信息...")
    run_command('git config user.name "High-Performance Developer"')
    run_command('git config user.email "developer@highperformance.com"')
    print("✅ Git用户配置完成")
    
    # 步骤4: 添加所有文件
    print("[4/8] 添加文件到Git...")
    success, stdout, stderr = run_command("git add .")
    if not success:
        print(f"❌ 添加文件失败: {stderr}")
        return False
    print("✅ 文件添加成功")
    
    # 步骤5: 创建初始提交
    print("[5/8] 创建初始提交...")
    success, stdout, stderr = run_command('git commit -m "feat: v1.0.0 baseline - 完整的任务管理平台"')
    if not success:
        print(f"❌ 提交创建失败: {stderr}")
        return False
    print("✅ 初始提交创建成功")
    
    # 步骤6: 创建基线标签
    print("[6/8] 创建v1.0.0基线标签...")
    success, stdout, stderr = run_command('git tag -a v1.0.0 -m "Production baseline - 完整的任务管理平台"')
    if not success:
        print(f"❌ 标签创建失败: {stderr}")
        return False
    print("✅ v1.0.0基线标签创建成功")
    
    # 步骤7: 创建分支结构
    print("[7/8] 创建分支结构...")
    success, stdout, stderr = run_command("git checkout -b develop")
    success, stdout, stderr = run_command("git checkout -b feature/intelligent-recommendations")
    if not success:
        print(f"❌ 分支创建失败: {stderr}")
        return False
    print("✅ 分支结构创建成功")
    
    # 步骤8: 创建备份目录
    print("[8/8] 创建备份目录...")
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    print(f"✅ 备份目录已创建: {backup_dir}")
    
    # 显示最终状态
    print()
    print("==========================================")
    print("🎉 版本基线保护设置完成！")
    print("==========================================")
    print()
    
    # 显示Git状态
    print("📊 Git状态信息:")
    success, stdout, stderr = run_command("git branch -a")
    if success:
        print(stdout)
    
    print()
    print("📋 最近提交:")
    success, stdout, stderr = run_command("git log --oneline -3")
    if success:
        print(stdout)
    
    print()
    print("🏷️ 标签列表:")
    success, stdout, stderr = run_command("git tag -l")
    if success:
        print(stdout)
    
    print()
    print("🔄 下一步操作:")
    print("1. 运行备份系统: python scripts/backup_system.py --create-backup --version v1.0.0")
    print("2. 创建开发环境配置: copy .env.example .env.dev")
    print("3. 开始智能推荐功能开发")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            input("按任意键继续...")
        else:
            input("设置失败，按任意键退出...")
    except KeyboardInterrupt:
        print("\n用户取消操作")
    except Exception as e:
        print(f"发生异常: {e}")
        input("按任意键退出...")