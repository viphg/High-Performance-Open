# 本地开发指南

## 快速开始

### 方案 1: 使用 Docker Compose (推荐)

最简单和快速的方法，所有服务自动配置。

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

服务访问地址：
- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 数据库: localhost:5432
- Redis: localhost:6379

---

### 方案 2: 手动启动后端和前端

需要预先安装 PostgreSQL 和 Redis。

#### 1. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境配置文件
cp .env.example .env

# 初始化数据库 (首次运行)
# 首先确保 PostgreSQL 已启动并创建了数据库

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
python -m uvicorn app.main:app --reload
```

后端服务运行在 http://localhost:8000

#### 2. 启动前端

在新的终端窗口中：

```bash
cd frontend

# 安装依赖
npm install

# 复制环境配置文件
cp .env.example .env

# 启动开发服务器
npm run dev
```

前端服务运行在 http://localhost:5173

---

## 环境配置

### 后端环境变量 (.env)

关键配置项：

```
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/high_performance

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://localhost:6379/0

# 邮件
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key

# 应用
DEBUG=True
ENVIRONMENT=development
```

### 前端环境变量 (.env)

```
VITE_API_URL=http://localhost:8000/api
```

---

## 数据库初始化

### 使用 Alembic 管理数据库迁移

```bash
cd backend

# 生成新的迁移脚本
alembic revision --autogenerate -m "add new table"

# 应用所有待处理的迁移
alembic upgrade head

# 回滚到上一个版本
alembic downgrade -1

# 查看当前数据库版本
alembic current

# 查看迁移历史
alembic history
```

---

## 常用开发命令

### 后端

```bash
# 运行单元测试
pytest tests/

# 运行特定测试
pytest tests/test_auth.py

# 查看覆盖率
pytest --cov=app tests/

# 代码质量检查
flake8 app/ --max-line-length=120

# 代码格式化
black app/

# 类型检查
mypy app/
```

### 前端

```bash
# 开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 代码检查
npm run lint

# 运行测试
npm test
```

### Docker

```bash
# 查看所有容器
docker-compose ps

# 查看后端日志
docker-compose logs -f backend

# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec postgres psql -U user -d high_performance

# 重新构建镜像
docker-compose build --no-cache

# 清理所有数据并重新开始
docker-compose down -v
docker-compose up -d
```

---

## 测试 API

### 使用 Curl

```bash
# 注册用户
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'

# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'

# 获取当前用户信息 (需要 token)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer {access_token}"
```

### 使用 Postman

1. 导入 API 集合（待创建）
2. 在环境变量中设置 `base_url` 和 `token`
3. 执行请求

### 使用 FastAPI 内置文档

1. 打开 http://localhost:8000/docs (Swagger UI)
2. 或 http://localhost:8000/redoc (ReDoc)
3. 直接在界面上测试 API

---

## 故障排除

### 数据库连接错误

```
Error: could not connect to server: Connection refused
```

**解决方案:**
1. 确保 PostgreSQL 正在运行
2. 检查 DATABASE_URL 是否正确
3. 确认用户名和密码正确
4. 检查数据库是否已创建

### 端口已被占用

```
Address already in use
```

**解决方案:**
```bash
# 查看占用端口的进程
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 杀死进程
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Python 包冲突

```
pip install --upgrade pip
pip cache purge
pip install -r requirements.txt --force-reinstall
```

### Redis 连接错误

确保 Redis 正在运行：
```bash
# 使用 Docker
docker run -d -p 6379:6379 redis:7-alpine

# 或在本地运行
redis-server
```

---

## 开发工作流

1. **创建特性分支**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **编写代码** - 遵循项目代码规范

3. **运行测试** - 确保所有测试通过
   ```bash
   pytest tests/
   npm test
   ```

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/new-feature
   ```

5. **提交 PR** - 等待代码审查

---

## 更多资源

- [项目规划](../PROJECT_PLAN.md)
- [API 设计文档](../docs/04-api-design.md)
- [数据模型设计](../docs/02-data-model.md)
- [前端页面结构](../docs/03-pages.md)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [React 文档](https://react.dev/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)

---

**最后更新**: 2026-02-02
