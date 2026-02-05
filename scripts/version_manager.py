#!/usr/bin/env python3
"""
High-Performance 项目版本管理脚本
提供Git仓库初始化、标签创建、分支管理等功能
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class VersionManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        os.chdir(self.project_root)
        
        print(f"📁 项目根目录: {self.project_root}")
    
    def run_command(self, cmd, capture_output=True, check=True):
        """安全地执行命令"""
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=capture_output, 
                text=True, 
                cwd=self.project_root
            )
            
            if capture_output:
                return result.returncode, result.stdout, result.stderr
            return result.returncode, "", ""
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 命令执行失败: {e}")
            return e.returncode, "", str(e)
    
    def check_git_availability(self):
        """检查Git是否可用"""
        print("🔍 检查Git可用性...")
        
        code, stdout, stderr = self.run_command("git --version")
        
        if code == 0:
            print(f"✅ Git可用: {stdout.strip()}")
            return True
        else:
            print("❌ Git不可用，请先安装Git")
            return False
    
    def init_git_repo(self):
        """初始化Git仓库"""
        print("\n🚀 初始化Git仓库...")
        
        # 检查是否已经是Git仓库
        if Path(".git").exists():
            print("⚠️ 已经是Git仓库，跳过初始化")
            return True
        
        # 初始化仓库
        code, stdout, stderr = self.run_command("git init")
        
        if code == 0:
            print("✅ Git仓库初始化成功")
            return True
        else:
            print(f"❌ Git仓库初始化失败: {stderr}")
            return False
    
    def configure_git_user(self, name=None, email=None):
        """配置Git用户信息"""
        print("\n👤 配置Git用户信息...")
        
        if not name:
            name = "High-Performance Developer"
        
        if not email:
            email = "developer@highperformance.com"
        
        # 配置用户名
        code, stdout, stderr = self.run_command(f"git config user.name \"{name}\"")
        if code != 0:
            print(f"⚠️ 配置用户名失败: {stderr}")
        
        # 配置邮箱
        code, stdout, stderr = self.run_command(f"git config user.email \"{email}\"")
        if code != 0:
            print(f"⚠️ 配置邮箱失败: {stderr}")
        
        print(f"✅ Git用户配置: {name} <{email}>")
    
    def add_all_files(self):
        """添加所有文件到Git"""
        print("\n📦 添加文件到Git...")
        
        code, stdout, stderr = self.run_command("git add .")
        
        if code == 0:
            print("✅ 文件添加成功")
            return True
        else:
            print(f"❌ 文件添加失败: {stderr}")
            return False
    
    def create_initial_commit(self, message="feat: v1.0.0 baseline - 完整的任务管理平台"):
        """创建初始提交"""
        print(f"\n💾 创建初始提交: {message}")
        
        # 提交
        code, stdout, stderr = self.run_command(f'git commit -m "{message}"')
        
        if code == 0:
            print("✅ 初始提交创建成功")
            return True
        else:
            print(f"❌ 初始提交创建失败: {stderr}")
            return False
    
    def create_tag(self, tag_name="v1.0.0", tag_message="Production baseline - 完整的任务管理平台"):
        """创建Git标签"""
        print(f"\n🏷️ 创建标签: {tag_name}")
        
        # 创建标签
        code, stdout, stderr = self.run_command(f'git tag -a {tag_name} -m "{tag_message}"')
        
        if code == 0:
            print(f"✅ 标签创建成功: {tag_name}")
            return True
        else:
            print(f"❌ 标签创建失败: {stderr}")
            return False
    
    def create_develop_branch(self):
        """创建develop分支"""
        print("\n🌿 创建develop分支...")
        
        # 检查develop分支是否已存在
        code, stdout, stderr = self.run_command("git branch --list develop")
        
        if "develop" in stdout:
            print("⚠️ develop分支已存在，切换到develop分支")
            code, stdout, stderr = self.run_command("git checkout develop")
        else:
            # 创建develop分支
            code, stdout, stderr = self.run_command("git checkout -b develop")
        
        if code == 0:
            print("✅ develop分支创建/切换成功")
            return True
        else:
            print(f"❌ develop分支操作失败: {stderr}")
            return False
    
    def create_feature_branch(self, feature_name="intelligent-recommendations"):
        """创建功能分支"""
        branch_name = f"feature/{feature_name}"
        print(f"\n🌿 创建功能分支: {branch_name}")
        
        # 创建功能分支
        code, stdout, stderr = self.run_command(f"git checkout -b {branch_name}")
        
        if code == 0:
            print(f"✅ 功能分支创建成功: {branch_name}")
            return True
        else:
            print(f"❌ 功能分支创建失败: {stderr}")
            return False
    
    def show_status(self):
        """显示Git状态"""
        print("\n📊 Git状态信息:")
        
        # 分支信息
        code, stdout, stderr = self.run_command("git branch -a")
        if code == 0:
            print("🌿 分支:")
            for line in stdout.split('\n'):
                print(f"  {line}")
        
        # 状态信息
        code, stdout, stderr = self.run_command("git status")
        if code == 0:
            print("\n📝 状态:")
            print(stdout)
        
        # 提交历史
        code, stdout, stderr = self.run_command("git log --oneline -5")
        if code == 0:
            print("\n📜 最近提交:")
            print(stdout)
        
        # 标签信息
        code, stdout, stderr = self.run_command("git tag -l")
        if code == 0:
            print("\n🏷️ 标签:")
            if stdout.strip():
                for line in stdout.split('\n'):
                    print(f"  {line}")
            else:
                print("  暂无标签")
    
    def complete_baseline_setup(self):
        """完成基线设置"""
        print("🚀 开始版本基线保护设置...")
        print("=" * 60)
        
        # 1. 检查Git可用性
        if not self.check_git_availability():
            return False
        
        # 2. 初始化Git仓库
        if not self.init_git_repo():
            return False
        
        # 3. 配置Git用户
        self.configure_git_user()
        
        # 4. 添加所有文件
        if not self.add_all_files():
            return False
        
        # 5. 创建初始提交
        if not self.create_initial_commit():
            return False
        
        # 6. 创建基线标签
        if not self.create_tag():
            return False
        
        # 7. 创建develop分支
        if not self.create_develop_branch():
            return False
        
        # 8. 创建功能分支
        if not self.create_feature_branch():
            return False
        
        # 9. 显示状态
        self.show_status()
        
        print("\n" + "=" * 60)
        print("🎉 版本基线保护设置完成!")
        print("📋 完成项目:")
        print("  ✅ Git仓库初始化")
        print("  ✅ v1.0.0 基线标签创建")
        print("  ✅ develop 分支创建")
        print("  ✅ feature/intelligent-recommendations 分支创建")
        print("\n🔧 下一步:")
        print("  1. 运行备份系统: python scripts/backup_system.py --create-backup --version v1.0.0")
        print("  2. 创建开发环境配置")
        print("  3. 开始智能推荐功能开发")
        
        return True


def main():
    """主函数"""
    manager = VersionManager()
    
    if len(sys.argv) < 2:
        print("🔧 High-Performance 版本管理工具")
        print("\n用法:")
        print("  python scripts/version_manager.py --baseline-setup")
        print("  python scripts/version_manager.py --init")
        print("  python scripts/version_manager.py --add")
        print("  python scripts/version_manager.py --commit [message]")
        print("  python scripts/version_manager.py --tag [tag_name]")
        print("  python scripts/version_manager.py --checkout-branch [branch_name]")
        print("  python scripts/version_manager.py --create-branch [branch_name]")
        print("  python scripts/version_manager.py --status")
        print("\n示例:")
        print("  python scripts/version_manager.py --baseline-setup")
        print("  python scripts/version_manager.py --commit 'feat: 添加智能推荐功能'")
        print("  python scripts/version_manager.py --tag v1.1.0")
        return
    
    command = sys.argv[1]
    
    if command == "--baseline-setup":
        manager.complete_baseline_setup()
    
    elif command == "--init":
        manager.init_git_repo()
        manager.configure_git_user()
    
    elif command == "--add":
        manager.add_all_files()
    
    elif command == "--commit":
        message = "Auto commit"
        if len(sys.argv) > 2:
            message = sys.argv[2]
        manager.create_initial_commit(message)
    
    elif command == "--tag":
        tag_name = "v1.0.0"
        if len(sys.argv) > 2:
            tag_name = sys.argv[2]
        manager.create_tag(tag_name)
    
    elif command == "--checkout-branch":
        if len(sys.argv) < 3:
            print("❌ 请指定分支名称")
            return
        
        branch_name = sys.argv[2]
        manager.run_command(f"git checkout {branch_name}")
    
    elif command == "--create-branch":
        if len(sys.argv) < 3:
            print("❌ 请指定分支名称")
            return
        
        branch_name = sys.argv[2]
        manager.create_feature_branch(branch_name)
    
    elif command == "--status":
        manager.show_status()
    
    else:
        print(f"❌ 未知命令: {command}")


if __name__ == "__main__":
    main()