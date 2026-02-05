#!/usr/bin/env python3
"""
直接版本基线保护设置 - 不依赖外部命令
"""

import os
import json
import zipfile
import shutil
from datetime import datetime
from pathlib import Path

class DirectVersionSetup:
    def __init__(self):
        self.project_path = Path("D:/OPENPROJECT/High-Performance-Open")
        self.backup_path = self.project_path / "backups" / "version_baseline"
        self.backup_path.mkdir(parents=True, exist_ok=True)
    
    def create_git_manifest(self):
        """创建Git清单文件"""
        print("📋 创建Git清单文件...")
        
        manifest = {
            "version": "v1.0.0",
            "baseline_date": datetime.now().isoformat(),
            "project_root": str(self.project_path),
            "description": "Production baseline - 完整的任务管理平台",
            "file_structure": self._scan_project_structure(),
            "important_files": self._get_important_files()
        }
        
        manifest_path = self.backup_path / "git_manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Git清单已创建: {manifest_path}")
        return manifest
    
    def _scan_project_structure(self):
        """扫描项目结构"""
        structure = {}
        
        for root, dirs, files in os.walk(self.project_path):
            root_path = Path(root)
            relative_path = root_path.relative_to(self.project_path)
            
            if str(relative_path) == '.':
                continue
            
            structure_key = str(relative_path).replace('\\', '/')
            structure[structure_key] = {
                "directories": dirs,
                "files": files,
                "file_count": len(files)
            }
        
        return structure
    
    def _get_important_files(self):
        """获取重要文件列表"""
        important_files = []
        
        # 关键配置文件
        config_files = [
            "docker-compose.yml",
            ".env.example",
            "requirements.txt",
            "package.json",
            "README.md"
        ]
        
        for file in config_files:
            file_path = self.project_path / file
            if file_path.exists():
                important_files.append({
                    "name": file,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        return important_files
    
    def create_full_backup(self):
        """创建完整项目备份"""
        print("📦 创建完整项目备份...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"high-performance_v1.0.0_baseline_{timestamp}"
        backup_zip_path = self.backup_path / f"{backup_name}.zip"
        
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
            "temp_restore"
        ]
        
        def should_exclude(path):
            """检查是否应该排除文件"""
            path_name = path.name
            for pattern in exclude_patterns:
                if pattern.startswith('*'):
                    if path_name.endswith(pattern[1:]):
                        return True
                elif path_name == pattern:
                    return True
            return False
        
        try:
            with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                for root, dirs, files in os.walk(self.project_path):
                    # 过滤目录
                    dirs[:] = [d for d in dirs if not should_exclude(Path(d))]
                    
                    for file in files:
                        file_path = Path(root) / file
                        if should_exclude(file_path):
                            continue
                        
                        # 计算相对路径
                        rel_path = file_path.relative_to(self.project_path)
                        
                        try:
                            zipf.write(file_path, rel_path)
                            print(f"  ✓ {rel_path}")
                        except Exception as e:
                            print(f"  ❌ 跳过文件 {rel_path}: {e}")
                            continue
            
            print(f"✅ 备份完成: {backup_zip_path}")
            print(f"📊 备份大小: {self._format_size(backup_zip_path.stat().st_size)}")
            
            return backup_zip_path
            
        except Exception as e:
            print(f"❌ 备份创建失败: {e}")
            return None
    
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
    
    def create_development_config(self):
        """创建开发环境配置"""
        print("🔧 创建开发环境配置...")
        
        # 复制.env.example到.env.dev
        env_example = self.project_path / ".env.example"
        env_dev = self.project_path / ".env.dev"
        
        if env_example.exists():
            shutil.copy2(env_example, env_dev)
            
            # 修改开发配置
            with open(env_dev, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换关键配置为开发环境
            dev_content = content.replace('DEBUG=False', 'DEBUG=True')
            dev_content = dev_content.replace('ENVIRONMENT=production', 'ENVIRONMENT=development')
            dev_content = dev_content.replace('your-secret-key-change-in-production', 'dev-secret-key-for-intelligent-recommendations-only-change-in-production')
            
            with open(env_dev, 'w', encoding='utf-8') as f:
                f.write(dev_content)
            
            print(f"✅ 开发配置已创建: {env_dev}")
        else:
            print("⚠️ .env.example文件不存在，跳过配置创建")
    
    def create_git_instructions(self):
        """创建Git操作说明文件"""
        print("📝 创建Git操作说明...")
        
        instructions = """# Git 版本基线保护操作说明

## 🎯 当前状态
- 项目位置: {project_path}
- 版本: v1.0.0 (基线版本)
- 备份位置: {backup_path}

## 📋 手动操作步骤

### 1. 初始化Git仓库
```bash
cd "{project_path}"
git init
git config user.name "High-Performance Developer"
git config user.email "developer@highperformance.com"
```

### 2. 添加文件并创建提交
```bash
git add .
git commit -m "feat: v1.0.0 baseline - 完整的任务管理平台"
```

### 3. 创建基线标签
```bash
git tag -a v1.0.0 -m "Production baseline - 完整的任务管理平台"
```

### 4. 创建分支结构
```bash
git checkout -b develop
git checkout -b feature/intelligent-recommendations
```

### 5. 验证设置
```bash
git branch -a
git log --oneline -3
git tag -l
```

## 🔄 回滚机制

### 回滚到基线版本
```bash
git checkout v1.0.0
# 或
git reset --hard v1.0.0
```

### 使用备份恢复
```bash
# 解压备份文件
unzip {backup_name}.zip -d ./restore
# 复制文件覆盖当前项目
```

## ✅ 验证清单

- [ ] Git仓库已初始化
- [ ] v1.0.0基线标签已创建
- [ ] develop和feature分支已创建
- [ ] 完整备份已生成
- [ ] 开发环境配置已创建
- [ ] 回滚机制已验证

## 🚀 下一步开发

1. 在feature/intelligent-recommendations分支开发智能推荐功能
2. 定期提交代码并推送到develop分支
3. 功能完成后创建release分支进行测试
4. 测试通过后合并到main分支并创建新标签

""".format(
            project_path=self.project_path,
            backup_path=self.backup_path
        )
        
        instructions_path = self.backup_path / "git_instructions.md"
        with open(instructions_path, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print(f"✅ Git操作说明已创建: {instructions_path}")
    
    def run_complete_setup(self):
        """运行完整设置"""
        print("=" * 60)
        print("High-Performance 版本基线保护设置")
        print("=" * 60)
        print()
        
        # 1. 创建Git清单
        manifest = self.create_git_manifest()
        
        # 2. 创建完整备份
        backup_path = self.create_full_backup()
        
        # 3. 创建开发配置
        self.create_development_config()
        
        # 4. 创建Git操作说明
        self.create_git_instructions()
        
        # 5. 创建设置总结
        self.create_setup_summary(manifest, backup_path)
        
        print("=" * 60)
        print("🎉 版本基线保护设置完成!")
        print("=" * 60)
        
        return True
    
    def create_setup_summary(self, manifest, backup_path):
        """创建设置总结"""
        summary = {
            "setup_date": datetime.now().isoformat(),
            "version": "v1.0.0",
            "status": "baseline_protected",
            "components": {
                "git_manifest": "已创建",
                "full_backup": "已创建" if backup_path else "失败",
                "dev_config": "已创建",
                "git_instructions": "已创建"
            },
            "next_steps": [
                "1. 按照git_instructions.md中的步骤手动执行Git操作",
                "2. 在feature/intelligent-recommendations分支开始开发",
                "3. 定期提交代码并进行测试"
            ],
            "rollback_options": [
                "使用Git标签回滚: git checkout v1.0.0",
                "使用备份恢复: 解压备份文件覆盖项目",
                "使用Git硬重置: git reset --hard v1.0.0"
            ]
        }
        
        summary_path = self.backup_path / "setup_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ 设置总结已创建: {summary_path}")
        
        # 显示关键信息
        print("\n📋 设置总结:")
        print(f"  🎯 版本: v1.0.0")
        print(f"  📁 备份: {backup_path.name if backup_path else '失败'}")
        print(f"  📝 说明: git_instructions.md")
        print(f"  🔧 配置: .env.dev")
        print("\n🚀 立即执行:")
        print(f"  打开 {summary_path}")
        print(f"  查看 git_instructions.md 文件")
        print(f"  按照1-4步手动执行Git操作")


def main():
    """主函数"""
    try:
        setup = DirectVersionSetup()
        success = setup.run_complete_setup()
        
        if success:
            input("\n✅ 设置完成! 按任意键继续...")
        else:
            input("\n❌ 设置失败! 按任意键退出...")
            
    except KeyboardInterrupt:
        print("\n用户取消操作")
    except Exception as e:
        print(f"发生异常: {e}")
        input("按任意键退出...")


if __name__ == "__main__":
    main()