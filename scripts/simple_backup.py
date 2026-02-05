#!/usr/bin/env python3
"""
简化版版本备份系统 - 避免编码问题
"""

import os
import sys
import zipfile
import shutil
from datetime import datetime
from pathlib import Path

class SimpleVersionBackup:
    def __init__(self):
        self.project_root = Path("D:/OPENPROJECT/High-Performance-Open")
        self.backup_dir = self.project_root / "backups" / "version_baseline"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, version_tag):
        """创建完整项目备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"high-performance_v{version_tag}_{timestamp}"
        backup_zip_path = self.backup_dir / f"{backup_name}.zip"
        
        print(f"Starting backup: {backup_name}")
        
        try:
            with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                for root, dirs, files in os.walk(self.project_root):
                    # 过滤排除的目录和文件
                    dirs[:] = [d for d in dirs if not self._should_exclude(d)]
                    
                    for file in files:
                        file_path = Path(root) / file
                        if self._should_exclude_file(file):
                            continue
                        
                        rel_path = file_path.relative_to(self.project_root)
                        
                        try:
                            zipf.write(file_path, rel_path)
                            print(f"  Adding: {rel_path}")
                        except Exception as e:
                            print(f"  Skip: {rel_path} - {e}")
                            continue
            
            file_size = backup_zip_path.stat().st_size
            print(f"Backup completed: {backup_zip_path}")
            print(f"Backup size: {self._format_size(file_size)}")
            
            return True
            
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
    
    def _should_exclude(self, dirname):
        """检查目录是否应该排除"""
        exclude_dirs = [
            "node_modules", "__pycache__", "*.pyc", "*.pyo", "*.pyd",
            ".venv", "venv", ".git", "*.log", "backups", 
            "docker-backups", "temp_restore", "__pycache__"
        ]
        return dirname in exclude_dirs
    
    def _should_exclude_file(self, filename):
        """检查文件是否应该排除"""
        exclude_files = [
            "Thumbs.db", "desktop.ini"
        ]
        return any(filename == f for f in exclude_files)
    
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

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python simple_backup.py --create-backup [--version VERSION]")
        return
    
    command = sys.argv[1]
    
    if command == "--create-backup":
        version = "v1.0.0"
        if len(sys.argv) > 2 and sys.argv[2] == "--version":
            version = sys.argv[3]
        
        print(f"Creating backup for version: {version}")
        
        manager = SimpleVersionBackup()
        success = manager.create_backup(version)
        
        if success:
            print("Backup completed successfully!")
        else:
            print("Backup failed!")

if __name__ == "__main__":
    main()