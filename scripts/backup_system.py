#!/usr/bin/env python3
"""
High-Performance 项目版本备份管理系统
提供完整的代码、数据库、配置备份功能
"""

import os
import shutil
import json
import sys
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

class VersionBackupManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = self.project_root / "backups"
        self.docker_backup_dir = self.project_root / "docker-backups"
        
        # 确保备份目录存在
        self.backup_dir.mkdir(exist_ok=True)
        self.docker_backup_dir.mkdir(exist_ok=True)
        
        print(f"📁 项目根目录: {self.project_root}")
        print(f"📁 备份目录: {self.backup_dir}")
        print(f"📁 Docker备份目录: {self.docker_backup_dir}")
    
    def create_full_backup(self, version_tag):
        """创建完整代码备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"high-performance_v{version_tag}_{timestamp}"
        
        print(f"\n🔄 开始创建备份: {backup_name}")
        
        # 备份路径
        backup_path = self.backup_dir / f"{backup_name}.zip"
        
        # 需要排除的目录和文件
        exclude_patterns = [
            "node_modules",
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".venv",
            "venv",
            ".git",
            "*.log",
            "backups",
            "docker-backups",
            ".DS_Store",
            "Thumbs.db"
        ]
        
        try:
            # 创建ZIP备份文件
            print("📦 打包项目文件...")
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                for root, dirs, files in os.walk(self.project_root):
                    # 计算相对路径
                    rel_path = os.path.relpath(root, self.project_root)
                    
                    # 跳过排除的目录
                    dirs[:] = [d for d in dirs if not self._should_exclude(d, exclude_patterns)]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_file_path = os.path.relpath(file_path, self.project_root)
                        
                        # 跳过排除的文件
                        if self._should_exclude_file(file, exclude_patterns):
                            continue
                            
                        # 添加到ZIP
                        try:
                            zipf.write(file_path, rel_file_path)
                            print(f"  ✓ {rel_file_path}")
                        except Exception as e:
                            print(f"  ❌ 跳过文件 {file}: {e}")
                            continue
            
            print(f"✅ 代码备份完成: {backup_path}")
            print(f"📊 备份大小: {self._format_size(backup_path.stat().st_size)}")
            
            # 创建备份信息文件
            backup_info = self._create_backup_info(backup_name, version_tag, backup_path)
            
            # 备份数据库
            db_backup_result = self._backup_database(backup_name)
            
            # 备份Docker卷
            docker_backup_result = self._backup_docker_volumes(backup_name)
            
            # 更新备份信息
            backup_info.update({
                "database_backup": db_backup_result,
                "docker_backup": docker_backup_result,
                "total_size": self._calculate_total_size(backup_info)
            })
            
            # 保存备份信息
            info_path = self.backup_dir / f"{backup_name}_info.json"
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"✅ 备份信息文件: {info_path}")
            
            # 创建最新备份链接
            latest_link = self.backup_dir / "latest_backup"
            if latest_link.exists():
                latest_link.unlink()
            
            try:
                latest_link.symlink_to(backup_path)
                print(f"✅ 创建最新备份链接: {latest_link}")
            except OSError:
                # Windows可能需要管理员权限
                print("⚠️ 无法创建符号链接（Windows限制）")
            
            return backup_name
            
        except Exception as e:
            print(f"❌ 备份创建失败: {e}")
            return None
    
    def _should_exclude(self, dirname, exclude_patterns):
        """检查目录是否应该排除"""
        return dirname in exclude_patterns
    
    def _should_exclude_file(self, filename, exclude_patterns):
        """检查文件是否应该排除"""
        for pattern in exclude_patterns:
            if pattern.startswith('*'):
                if filename.endswith(pattern[1:]):
                    return True
            elif filename == pattern:
                return True
        return False
    
    def _create_backup_info(self, backup_name, version_tag, backup_path):
        """创建备份信息"""
        file_count = 0
        total_size = 0
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                file_count = len(zipf.namelist())
                total_size = sum(info.file_size for info in zipf.filelist())
        except Exception as e:
            print(f"⚠️ 无法读取备份文件信息: {e}")
        
        backup_info = {
            "backup_name": backup_name,
            "version": version_tag,
            "timestamp": datetime.now().isoformat(),
            "backup_path": str(backup_path),
            "file_count": file_count,
            "total_size": total_size,
            "formatted_size": self._format_size(total_size),
            "project_root": str(self.project_root),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "backup_type": "full_project_backup"
        }
        
        return backup_info
    
    def _backup_database(self, backup_name):
        """备份数据库"""
        print("\n💾 备份数据库...")
        
        try:
            # 检查PostgreSQL容器是否运行
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=hp-postgres-open", "--format", "{{.Status}}"],
                capture_output=True, text=True, shell=False
            )
            
            if "Up" not in result.stdout:
                print("⚠️ PostgreSQL容器未运行，跳过数据库备份")
                return {"status": "skipped", "reason": "container_not_running"}
            
            # 创建数据库备份
            backup_sql_path = self.backup_dir / f"{backup_name}_database.sql"
            
            cmd = [
                "docker", "exec", "hp-postgres-open",
                "pg_dump", "-U", "user", "-d", "high_performance_open"
            ]
            
            print("📊 执行数据库备份命令...")
            result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
            
            if result.returncode == 0:
                with open(backup_sql_path, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                
                file_size = backup_sql_path.stat().st_size
                print(f"✅ 数据库备份完成: {backup_sql_path}")
                print(f"📊 备份大小: {self._format_size(file_size)}")
                
                return {
                    "status": "success",
                    "backup_path": str(backup_sql_path),
                    "file_size": file_size,
                    "formatted_size": self._format_size(file_size)
                }
            else:
                print(f"❌ 数据库备份失败: {result.stderr}")
                return {"status": "failed", "error": result.stderr}
                
        except Exception as e:
            print(f"❌ 数据库备份异常: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _backup_docker_volumes(self, backup_name):
        """备份Docker卷数据"""
        print("\n🐳 备份Docker卷数据...")
        
        docker_volumes = [
            ("postgres_data_open", "hp-postgres-open"),
            ("redis_data_open", "hp-redis-open"),
            ("frontend_node_modules_open", None)
        ]
        
        backup_results = {}
        
        for volume_name, container_name in docker_volumes:
            try:
                print(f"📦 备份卷: {volume_name}")
                
                if container_name:
                    # 检查容器是否运行
                    result = subprocess.run(
                        ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Status}}"],
                        capture_output=True, text=True, shell=False
                    )
                    
                    if "Up" not in result.stdout:
                        print(f"  ⚠️ 容器 {container_name} 未运行，跳过")
                        backup_results[volume_name] = {"status": "skipped", "reason": "container_not_running"}
                        continue
                
                # 创建卷备份目录
                volume_backup_dir = self.docker_backup_dir / f"{backup_name}_{volume_name}"
                volume_backup_dir.mkdir(exist_ok=True)
                
                if container_name:
                    # 备份容器中的数据
                    cmd = [
                        "docker", "cp", 
                        f"{container_name}:/data" if volume_name == "postgres_data_open" else f"{container_name}:/data",
                        str(volume_backup_dir)
                    ]
                else:
                    # 跳过node_modules备份（太大）
                    backup_results[volume_name] = {"status": "skipped", "reason": "too_large"}
                    continue
                
                result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
                
                if result.returncode == 0:
                    # 打包备份
                    backup_zip_path = self.docker_backup_dir / f"{backup_name}_{volume_name}.zip"
                    
                    with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, dirs, files in os.walk(volume_backup_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                rel_path = os.path.relpath(file_path, volume_backup_dir)
                                zipf.write(file_path, rel_path)
                    
                    # 清理临时目录
                    shutil.rmtree(volume_backup_dir)
                    
                    file_size = backup_zip_path.stat().st_size
                    backup_results[volume_name] = {
                        "status": "success",
                        "backup_path": str(backup_zip_path),
                        "file_size": file_size,
                        "formatted_size": self._format_size(file_size)
                    }
                    
                    print(f"  ✅ {volume_name} 备份完成")
                else:
                    print(f"  ❌ {volume_name} 备份失败: {result.stderr}")
                    backup_results[volume_name] = {"status": "failed", "error": result.stderr}
                    
            except Exception as e:
                print(f"  ❌ {volume_name} 备份异常: {e}")
                backup_results[volume_name] = {"status": "failed", "error": str(e)}
        
        return backup_results
    
    def _format_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def _calculate_total_size(self, backup_info):
        """计算总备份大小"""
        total_size = backup_info.get("total_size", 0)
        
        # 添加数据库大小
        if backup_info.get("database_backup", {}).get("status") == "success":
            total_size += backup_info["database_backup"]["file_size"]
        
        # 添加Docker卷大小
        docker_backup = backup_info.get("docker_backup", {})
        for volume_data in docker_backup.values():
            if volume_data.get("status") == "success":
                total_size += volume_data["file_size"]
        
        return {
            "total_bytes": total_size,
            "formatted_size": self._format_size(total_size)
        }
    
    def list_backups(self):
        """列出所有备份"""
        print("\n📋 现有备份列表:")
        
        if not self.backup_dir.exists():
            print("  📁 备份目录不存在")
            return
        
        backup_files = list(self.backup_dir.glob("high-performance_v*"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not backup_files:
            print("  📭 未找到备份文件")
            return
        
        for i, backup_file in enumerate(backup_files[:10], 1):  # 只显示最近10个
            backup_name = backup_file.stem
            size_str = self._format_size(backup_file.stat().st_size)
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            print(f"  {i:2d}. {backup_name}")
            print(f"      📊 大小: {size_str}")
            print(f"      📅 时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
    
    def restore_backup(self, backup_name):
        """恢复到指定备份"""
        print(f"\n🔄 开始恢复备份: {backup_name}")
        
        # 查找备份文件
        backup_file = None
        for file in self.backup_dir.glob(f"{backup_name}.zip"):
            backup_file = file
            break
        
        if not backup_file:
            print(f"❌ 备份文件不存在: {backup_name}")
            return False
        
        try:
            print(f"📦 解压备份文件: {backup_file}")
            
            # 创建临时目录
            temp_dir = self.project_root / "temp_restore"
            temp_dir.mkdir(exist_ok=True)
            
            # 解压到临时目录
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # 备份当前文件（以防恢复失败）
            current_backup = self.project_root / "current_backup_before_restore"
            if current_backup.exists():
                shutil.rmtree(current_backup)
            
            print("📋 创建当前状态备份...")
            shutil.copytree(self.project_root, current_backup, ignore=shutil.ignore_patterns('temp_restore', 'backups', 'docker-backups'))
            
            # 移除当前文件（保留备份目录）
            print("🗑️ 清理当前文件...")
            for item in self.project_root.iterdir():
                if item.name not in ['backups', 'docker-backups', 'temp_restore']:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
            
            # 复制恢复文件
            print("📋 恢复文件...")
            for item in temp_dir.iterdir():
                if item.name != 'backups':  # 不覆盖备份目录
                    dest = self.project_root / item.name
                    if item.is_file():
                        shutil.copy2(item, dest)
                    elif item.is_dir():
                        shutil.copytree(item, dest)
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
            
            print("✅ 备份恢复完成!")
            print(f"📁 原文件已备份到: {current_backup}")
            return True
            
        except Exception as e:
            print(f"❌ 恢复失败: {e}")
            return False


def main():
    """主函数"""
    manager = VersionBackupManager()
    
    if len(sys.argv) < 2:
        print("🔧 High-Performance 备份管理系统")
        print("\n用法:")
        print("  python scripts/backup_system.py --create-backup [--version VERSION]")
        print("  python scripts/backup_system.py --list-backups")
        print("  python scripts/backup_system.py --restore-backup BACKUP_NAME")
        print("\n示例:")
        print("  python scripts/backup_system.py --create-backup --version v1.0.0")
        print("  python scripts/backup_system.py --list-backups")
        print("  python scripts/backup_system.py --restore-backup high-performance_v1.0.0_20240205_143022")
        return
    
    command = sys.argv[1]
    
    if command == "--create-backup":
        version = "v1.0.0"  # 默认版本
        if len(sys.argv) > 2 and sys.argv[2] == "--version":
            version = sys.argv[3]
        
        print(f"🚀 创建版本备份: {version}")
        backup_name = manager.create_full_backup(version)
        
        if backup_name:
            print(f"\n🎉 备份创建成功!")
            print(f"📁 备份位置: {manager.backup_dir / f'{backup_name}.zip'}")
            print(f"📊 备份信息: {manager.backup_dir / f'{backup_name}_info.json'}")
        else:
            print(f"\n❌ 备份创建失败!")
    
    elif command == "--list-backups":
        manager.list_backups()
    
    elif command == "--restore-backup":
        if len(sys.argv) < 3:
            print("❌ 请指定备份名称")
            return
        
        backup_name = sys.argv[2]
        success = manager.restore_backup(backup_name)
        
        if success:
            print(f"\n🎉 备份恢复成功!")
        else:
            print(f"\n❌ 备份恢复失败!")
    
    else:
        print(f"❌ 未知命令: {command}")


if __name__ == "__main__":
    main()