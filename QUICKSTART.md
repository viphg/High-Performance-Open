# 项目快速导航

## 🎯 我应该从哪里开始？

### 1. **首次启动项目？**
👉 [快速启动指南](#快速启动)

### 2. **想了解项目？**
👉 [项目概述](#项目概述) → [README.md](README.md)

### 3. **开始开发？**
👉 [DEVELOPMENT.md](DEVELOPMENT.md)

### 4. **查看 API 文档？**
👉 [docs/04-api-design.md](docs/04-api-design.md) 或 http://localhost:8000/docs

### 5. **下一步做什么？**
👉 [INITIALIZATION_CHECKLIST.md](INITIALIZATION_CHECKLIST.md#-下一步任务)

---

## 🚀 快速启动

### 最简单的方式 (Docker)

```bash
docker-compose up -d
```

然后打开：
- **前端**: http://localhost:5173
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 测试认证系统

```bash
# 1. 注册用户
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# 2. 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'

# 3. 使用 token 获取当前用户信息
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer {access_token}"
```

---

## 📚 项目概述

**High-Performance** 是一个个人成长管理平台，帮助用户：
- 🎯 科学地设定目标
- ✅ 高效地执行任务
- 🏆 解锁成就获得动力
- 📊 数据驱动的反思

### 核心特性
- 用户认证系统 ✅ (已完成)
- 目标和任务管理 📋 (Phase 2)
- 成就和徽章系统 📋 (Phase 2)
- 邮件提醒功能 📋 (Phase 2)
- 数据统计分析 📋 (Phase 3)

---

## 📁 项目结构

```
High-Performance/
├── backend/          # FastAPI 后端
├── frontend/         # React 前端
├── docs/             # 项目文档
├── docker-compose.yml  # 开发环境配置
├── README.md         # 项目简介
├── DEVELOPMENT.md    # 开发指南 ⭐
├── INITIALIZATION_CHECKLIST.md  # 完成清单
└── PROJECT_LAUNCH_REPORT.md     # 启动报告
```

---

## 🔑 关键文件

| 文件 | 用途 | 优先级 |
|------|------|--------|
| [DEVELOPMENT.md](DEVELOPMENT.md) | 本地开发完整指南 | ⭐⭐⭐ |
| [docs/04-api-design.md](docs/04-api-design.md) | REST API 设计规范 | ⭐⭐⭐ |
| [README.md](README.md) | 项目总体介绍 | ⭐⭐ |
| [PROJECT_PLAN.md](PROJECT_PLAN.md) | 完整项目规划 | ⭐⭐ |
| [docs/02-data-model.md](docs/02-data-model.md) | 数据库设计 | ⭐⭐ |

---

## 🛠️ 常用命令

### Docker
```bash
docker-compose up -d           # 启动
docker-compose down            # 停止
docker-compose logs -f         # 查看日志
docker-compose exec backend sh # 进入容器
```

### 后端
```bash
python -m uvicorn app.main:app --reload  # 开发服务器
pytest tests/                            # 运行测试
alembic upgrade head                     # 数据库迁移
```

### 前端
```bash
npm run dev      # 开发服务器
npm run build    # 构建生产版本
npm run lint     # 代码检查
```

---

## 📊 项目进度

```
████████████████████░░░░░░░░░░░░░░░░░░░░░░░ ~45%

Phase 1: 初始化 ✅ (完成)
- 框架搭建
- 认证系统
- 开发环境

Phase 2: 核心功能 📋 (待做)
- 目标管理
- 任务管理
- 成就系统

Phase 3: 优化 📋 (待做)
Phase 4: 上线 📋 (待做)
```

---

## 🆘 遇到问题？

1. **检查 [DEVELOPMENT.md](DEVELOPMENT.md) 的故障排除部分**
2. **查看 Docker 日志**: `docker-compose logs backend`
3. **重新初始化**: `docker-compose down -v && docker-compose up -d`
4. **查看 API 文档**: http://localhost:8000/docs

---

## 📞 快速链接

### 文档
- [项目主文档](README.md)
- [API 设计文档](docs/04-api-design.md)
- [数据模型设计](docs/02-data-model.md)
- [开发指南](DEVELOPMENT.md)
- [项目规划](PROJECT_PLAN.md)

### 运行中的服务
- [前端](http://localhost:5173) - React 应用
- [后端 API](http://localhost:8000) - FastAPI
- [Swagger 文档](http://localhost:8000/docs) - 交互式 API 文档
- [ReDoc](http://localhost:8000/redoc) - API 参考文档

### 本地服务
- 数据库: `localhost:5432` (PostgreSQL)
- 缓存: `localhost:6379` (Redis)

---

## ✨ 下一步

### 立即可做
1. ✅ 启动项目: `docker-compose up -d`
2. ✅ 测试认证: 访问 http://localhost:8000/docs
3. ✅ 创建测试用户

### 接下来 (Phase 2)
1. 📋 实现目标管理 API
2. 📋 实现任务管理 API
3. 📋 实现前端页面
4. 📋 集成邮件服务

---

## 🎓 学习资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [React 官方文档](https://react.dev/)
- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [Docker 官方文档](https://docs.docker.com/)

---

<div align="center">

### 🚀 项目已准备好！开始编码吧！

**有问题？** 查看 [DEVELOPMENT.md](DEVELOPMENT.md)

</div>
