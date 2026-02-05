# 🛡️ 版本基线保护设置指南

## 📋 当前状态检查清单

在执行以下步骤前，请确认：

- [ ] 当前工作目录: `D:/OPENPROJECT/High-Performance-Open`
- [ ] Git已安装: 运行 `git --version` 检查
- [ ] Python环境正常: 运行 `python --version` 检查
- [ ] 项目文件完整: 检查 `ls -la` 确认关键文件存在
- [ ] 当前服务可安全停止: 检查 `docker ps` 查看运行状态

---

## 🚀 版本基线保护执行步骤

### 步骤1: Git仓库初始化

```bash
# 进入项目目录
cd "D:/OPENPROJECT/High-Performance-Open"

# 初始化Git仓库
git init

# 配置Git用户信息（如果未配置）
git config user.name "High-Performance Developer"
git config user.email "developer@highperformance.com"

# 验证配置
git config --list
```

**验证点**: 看到 `.git` 目录创建成功，用户信息配置正确

### 步骤2: 创建初始提交

```bash
# 添加所有文件到Git
git add .

# 检查添加状态
git status

# 创建初始提交
git commit -m "feat: v1.0.0 baseline - 完整的任务管理平台"

# 验证提交
git log --oneline -1
```

**验证点**: 看到提交信息，HEAD指向新提交

### 步骤3: 创建基线标签

```bash
# 创建v1.0.0标签
git tag -a v1.0.0 -m "Production baseline - 完整的任务管理平台"

# 验证标签创建
git tag -l

# 查看标签详情
git show v1.0.0
```

**验证点**: 看到v1.0.0标签在列表中

### 步骤4: 创建分支结构

```bash
# 创建并切换到develop分支
git checkout -b develop

# 从develop分支创建功能分支
git checkout -b feature/intelligent-recommendations

# 验证分支结构
git branch -a
```

**验证点**: 看到main、develop、feature/intelligent-recommendations分支

---

## 📦 完整备份执行

### 步骤5: 运行备份系统

```bash
# 创建v1.0.0版本备份
python scripts/backup_system.py --create-backup --version v1.0.0

# 验证备份文件
ls -la backups/
```

**预期输出**:
```
🔄 开始创建备份: high-performance_v1.0.0_20240205_143022
📦 打包项目文件...
✅ 代码备份完成
💾 备份数据库...
✅ 数据库备份完成
🐳 备份Docker卷数据...
✅ 备份恢复成功!

🎉 备份创建成功!
📁 备份位置: ./backups/high-performance_v1.0.0_20240205_143022.zip
📊 备份信息: ./backups/high-performance_v1.0.0_20240205_143022_info.json
```

---

## 🔧 环境准备

### 步骤6: 创建开发环境配置

```bash
# 创建开发环境配置文件
cp .env.example .env.dev

# 编辑开发配置（重要：不要覆盖生产配置）
notepad .env.dev
```

**.env.dev 配置内容**:
```env
# 开发环境配置
DEBUG=True
ENVIRONMENT=development
DATABASE_URL=postgresql://user:password@localhost:5433/high_performance_open_dev
REDIS_URL=redis://localhost:6380/0
CORS_ORIGINS=["http://localhost:5173","http://localhost:5174","http://localhost:5175","http://localhost:3000"]
SECRET_KEY=dev-secret-key-for-intelligent-recommendations-only-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60

# 邮件配置（开发环境可用测试邮箱）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-test-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=dev@highperformance.com
```

---

## 📊 版本基线保护验证

### 验证清单

✅ **Git仓库状态**
```bash
git status
git log --oneline -3
git tag -l
git branch -a
```

✅ **备份文件验证**
```bash
ls -la backups/
unzip -l backups/high-performance_v1.0.0_*.zip | head -10
```

✅ **环境配置验证**
```bash
ls -la .env*
cat .env.dev
```

✅ **分支结构验证**
```bash
git branch --show-current
```

---

## 🔄 回滚机制（如果需要）

### 快速回滚到基线

```bash
# 方法1: 使用Git标签回滚
git checkout v1.0.0

# 方法2: 使用备份文件恢复
python scripts/backup_system.py --restore-backup high-performance_v1.0.0_20240205_143022

# 方法3: 硬重置到基线提交
git reset --hard v1.0.0

# 恢复服务
docker-compose down
docker-compose up -d
```

### 验证回滚成功

```bash
# 检查当前分支
git branch --show-current

# 验证文件状态
git status

# 验证服务状态
curl http://localhost:8000/health
```

---

## 🎯 完成确认

当以下所有条件都满足时，版本基线保护设置完成：

- [x] Git仓库已初始化
- [x] v1.0.0基线标签已创建
- [x] develop和feature分支已创建
- [x] 完整备份已生成（代码+数据库+配置）
- [x] 开发环境配置已创建
- [x] 回滚机制已验证

---

## 📝 后续开发流程

### 标准开发流程

1. **功能开发**: 在feature分支进行开发
2. **代码提交**: 定期提交代码到feature分支
3. **测试验证**: 在开发环境测试功能
4. **合并到develop**: 功能完成后合并到develop分支
5. **创建发布分支**: 从develop创建release分支
6. **测试发布**: 在测试环境验证发布分支
7. **合并到main**: 测试通过后合并到main分支
8. **创建新标签**: 为新版本创建标签

### 分支命名规范

- `main`: 生产稳定版本
- `develop`: 开发集成版本
- `feature/*`: 功能开发分支
- `release/*`: 发布候选版本
- `hotfix/*`: 紧急修复分支

---

## ⚠️ 注意事项

1. **数据安全**: 在执行备份前确保数据库中没有未保存的重要更改
2. **服务状态**: 建议在服务停止状态下执行版本初始化
3. **权限确认**: 确保有足够的文件系统权限
4. **网络连接**: 备份过程中需要稳定的网络连接
5. **时间安排**: 整个过程预计需要30-60分钟

---

## 🚀 立即开始

现在您可以按照上述步骤手动执行版本基线保护设置！

**推荐执行顺序**:
1. 先执行Git初始化和标签创建
2. 再运行完整备份系统
3. 最后创建开发环境配置

完成后，您将拥有一个完整的版本基线保护机制，可以安全地开始智能推荐功能的开发工作！