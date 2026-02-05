# High-Performance 快速入门指南

## 项目概览

High-Performance 是一个个人成长管理平台，帮助用户制定目标、创建任务、追踪进度并解锁成就。

## 系统要求

- Docker 20.10+
- Docker Compose 1.29+
- Windows 10+ 或 Linux/macOS

## 快速启动 (60秒)

### 1. 启动应用
```bash
cd d:\OPENPROJECT\High-Performance
docker-compose up -d
```

### 2. 访问应用
- **前端**: http://localhost:5173
- **API文档**: http://localhost:8000/docs

### 3. 登录
使用测试账户:
- **用户名**: testuser
- **密码**: test123

## 功能导览

### 仪表盘 (Dashboard)
- 查看关键指标 (KPI)
- 目标和任务完成率
- 快速创建目标/任务

### 目标 (Goals)
- 创建新目标，设置优先级
- 追踪目标进度 (0-100%)
- 编辑或删除目标
- 为每个目标设置截止日期

### 任务 (Tasks)
- 创建任务并关联目标
- 记录预计和实际工时
- 修改任务状态 (未开始/进行中/已完成/已取消)
- 按优先级和截止日期管理

### 成就 (Achievements)
- 查看已解锁的成就
- 查看总积分
- 查看成就进度

### 分析 (Analytics)
- 目标完成率统计
- 任务完成率统计
- 进度分布可视化
- 最近任务概览
- 状态分布统计

## 核心工作流

### 1. 制定目标
```
仪表盘 → 创建新目标 → 填写目标信息 → 保存
```

### 2. 创建任务
```
任务页面 → 创建新任务 → 选择关联目标 → 保存
```

### 3. 追踪进度
```
分析页面 → 查看完成率 → 编辑任务状态 → 实时更新
```

### 4. 管理目标/任务
```
目标/任务列表 → 点击编辑 → 修改信息 → 保存更改
```

## API使用示例

### 登录
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

### 创建目标
```bash
curl -X POST http://localhost:8000/api/v1/goals \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "学习Python",
    "description": "完成Python基础课程",
    "priority": 3,
    "target_date": "2024-03-31"
  }'
```

### 创建任务
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "完成第1章节练习",
    "goal_id": 1,
    "priority": 2,
    "estimated_hours": 4
  }'
```

## 常见问题

### Q: 忘记密码怎么办?
A: 目前没有密码重置功能。可以通过后端重置用户密码:
```bash
docker-compose exec backend python -c "
from app.database import SessionLocal
from app.models import User
from app.utils.security import hash_password

db = SessionLocal()
user = db.query(User).filter(User.username == 'testuser').first()
user.hashed_password = hash_password('new_password')
db.commit()
"
```

### Q: 如何创建新用户?
A: 在注册页面填写信息即可自动创建账户。

### Q: 数据会被保存吗?
A: 是的！所有数据保存在PostgreSQL数据库中，持久化存储。

### Q: 如何停止应用?
A: ```bash
docker-compose down
```

### Q: 如何查看API文档?
A: 访问 http://localhost:8000/docs (Swagger UI) 或 http://localhost:8000/redoc (ReDoc)

## 开发环境设置

### 后端修改实时生效
后端使用 `uvicorn --reload`，修改Python文件后自动重启。

### 前端修改实时生效
前端使用 Vite HMR，修改React/TypeScript后自动刷新浏览器。

### 查看日志
```bash
# 后端日志
docker-compose logs backend -f

# 前端日志
docker-compose logs frontend -f

# 数据库日志
docker-compose logs postgres -f
```

## 项目文件结构

```
High-Performance/
├── backend/                  # FastAPI后端
│   ├── app/
│   │   ├── api/v1/          # API端点
│   │   ├── models/          # 数据库模型
│   │   ├── schemas/         # 验证模式
│   │   ├── services/        # 业务逻辑
│   │   └── utils/           # 工具函数
│   └── requirements.txt
│
├── frontend/                 # React前端
│   ├── src/
│   │   ├── pages/           # 页面组件
│   │   ├── api/             # API客户端
│   │   ├── stores/          # 状态管理
│   │   └── types/           # TypeScript类型
│   ├── vite.config.ts
│   └── package.json
│
└── docker-compose.yml        # 容器编排配置
```

## 扩展应用

### 添加新页面
1. 在 `frontend/src/pages/` 创建新文件
2. 在 `App.tsx` 中添加路由
3. 更新导航菜单

### 添加新API端点
1. 在 `backend/app/api/v1/` 创建新文件
2. 定义Pydantic schema
3. 在 `__init__.py` 中注册路由

### 连接数据库
```bash
# 进入后端容器
docker-compose exec backend bash

# 使用psql连接
psql -h postgres -U user -d high_performance
```

## 生产部署建议

1. **环境变量**: 使用 `.env` 文件管理敏感信息
2. **HTTPS**: 在Nginx反向代理后使用SSL证书
3. **数据库备份**: 定期备份PostgreSQL数据
4. **日志聚集**: 使用ELK或Prometheus监控
5. **负载均衡**: 使用Kubernetes或Docker Swarm扩展

## 支持和贡献

- 报告bug: 在项目README中描述问题
- 建议功能: 创建GitHub Issue
- 代码贡献: Fork -> 修改 -> Pull Request

## 许可证

MIT License

## 更新日志

### v1.0.0 (2024-02-03)
- ✅ 完整的认证系统
- ✅ 目标和任务CRUD
- ✅ 成就系统
- ✅ 数据分析仪表盘
- ✅ 响应式UI设计

---

**项目链接**: https://github.com/your-username/high-performance
**问题反馈**: contact@example.com
**最后更新**: 2024年2月3日
