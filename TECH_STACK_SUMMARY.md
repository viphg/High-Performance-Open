# High-Performance 技术栈速查表

## 核心技术选择

### 📊 技术栈矩阵
```
┌────────────────────────────────────────────────────────────┐
│                    HIGH-PERFORMANCE 技术栈                  │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  后端层                          前端层                      │
│  ────────────────────────────────────────────              │
│  ✓ FastAPI (Python 3.11+)        ✓ React 18 + TypeScript   │
│  ✓ PostgreSQL + SQLAlchemy        ✓ Zustand (状态管理)      │
│  ✓ Celery + Redis                 ✓ TanStack Query (数据)   │
│  ✓ JWT 认证                       ✓ shadcn/ui + Tailwind    │
│  ✓ Pydantic 验证                  ✓ Recharts (图表)         │
│  ✓ APScheduler (定时任务)         ✓ Vite (构建工具)         │
│                                   ✓ React Router v6         │
│  消息队列 & 缓存                   部署                      │
│  ────────────────────────────────────────────              │
│  ✓ Redis (缓存 & 队列)            ✓ Vercel (前端)          │
│  ✓ Celery Beat (定时)            ✓ Railway/Render (后端)   │
│                                   ✓ GitHub Actions (CI/CD)  │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

## 快速对比：为什么选择这套技术？

| 需求 | 我们的选择 | 优势 | 替代方案 |
|------|---------|------|---------|
| 后端框架 | **FastAPI** | 异步、自动文档、类型安全 | Django, Flask |
| 前端框架 | **React** | 组件化、生态大、学习资源多 | Vue 3, Svelte |
| 数据库 | **PostgreSQL** | 功能完整、可靠性高、扩展丰富 | MySQL, MongoDB |
| 状态管理 | **Zustand** | 轻量、API 简洁、无 Redux 复杂性 | Redux, Recoil |
| UI 库 | **shadcn/ui** | 完全可定制、无强绑定 | Material-UI, Ant Design |
| 样式 | **Tailwind CSS** | 原子化、开发快速、文件小 | CSS-in-JS, SASS |
| 部署 | **Docker** | 容器化、一致性、可扩展 | 虚拟机, 手动部署 |

---

## 系统架构层次

```
┌─────────────────────────────────────────────────────────────┐
│                    表现层 (Presentation)                     │
│  React SPA + TypeScript | 响应式设计 | Vercel 托管          │
├─────────────────────────────────────────────────────────────┤
│                    API 网关层 (Gateway)                      │
│  FastAPI 中间件 | 请求验证 | 速率限制 | CORS                │
├─────────────────────────────────────────────────────────────┤
│                    业务逻辑层 (Application)                  │
│  Service 层 | 权限检查 | 事件触发 | 数据转换                │
├─────────────────────────────────────────────────────────────┤
│                    数据访问层 (Data Access)                  │
│  SQLAlchemy ORM | 缓存策略 | 查询优化                       │
├─────────────────────────────────────────────────────────────┤
│                    基础设施层 (Infrastructure)              │
│  PostgreSQL | Redis | Celery | SendGrid API                │
└─────────────────────────────────────────────────────────────┘
```

---

## 核心功能与技术映射

### 目标管理
```
UI: React 组件 (Goals/GoalList.tsx)
  ↓
State: Zustand store (goalStore)
  ↓
API: GET/POST /api/v1/goals (FastAPI)
  ↓
Service: GoalService (SQLAlchemy 查询)
  ↓
DB: goals 表 (PostgreSQL)
```

### 邮件提醒
```
触发: APScheduler 定时检查
  ↓
Service: EmailService (Celery 异步任务)
  ↓
Queue: Redis (任务队列)
  ↓
Worker: Celery Worker (邮件发送)
  ↓
Provider: SendGrid API / SMTP
```

### 成就系统
```
事件: Task 完成 → 触发事件
  ↓
Service: AchievementService (检查条件)
  ↓
Action: 解锁徽章 → 更新数据库
  ↓
Notify: 发送邮件通知用户
```

---

## 开发环境设置速查

### 本地运行（Docker Compose）
```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

### 后端服务
- **API**: http://localhost:8000
- **文档**: http://localhost:8000/docs
- **重定向文档**: http://localhost:8000/redoc

### 前端服务
- **开发服务器**: http://localhost:5173
- **构建**: `npm run build`

### 数据库访问
- **PostgreSQL**: `postgresql://user:password@localhost:5432/highperformance`
- **Redis**: `redis://localhost:6379`

---

## 代码规范

### 后端 (FastAPI + Python)
```python
# 强制使用类型提示
def get_user_goals(
    user_id: int,
    skip: int = 0,
    limit: int = 10
) -> list[GoalResponse]:
    """
    获取用户目标列表
    
    Args:
        user_id: 用户 ID
        skip: 分页偏移
        limit: 分页大小
    
    Returns:
        目标对象列表
    """
    pass
```

### 前端 (React + TypeScript)
```typescript
// 使用 interface 定义类型
interface Goal {
  id: number;
  title: string;
  status: 'active' | 'paused' | 'completed' | 'failed';
  targetDate: Date;
  progressPercentage: number;
}

// React Hook 组件
function GoalCard({ goal }: { goal: Goal }) {
  return <div>{goal.title}</div>;
}
```

---

## 测试策略

### 后端测试
```
单元测试: pytest (models, schemas)
集成测试: pytest (API endpoints)
覆盖率目标: > 80%
```

### 前端测试
```
单元测试: Jest + React Testing Library
集成测试: Cypress/Playwright (E2E)
覆盖率目标: > 70%
```

---

## 监控与日志

### 后端日志
```
工具: Python logging + structlog
格式: JSON (便于分析)
级别: DEBUG | INFO | WARNING | ERROR | CRITICAL
```

### 前端监控
```
错误跟踪: Sentry
分析: Google Analytics 或 Mixpanel
性能: Lighthouse, WebVitals
```

---

## 安全最佳实践

✅ **认证**
- JWT Token（有效期短期 15min + 长期 7 天）
- 密码使用 bcrypt 哈希
- OAuth 集成（可选）

✅ **授权**
- 基于角色的访问控制 (RBAC)
- 行级别权限检查

✅ **数据保护**
- 所有端点使用 HTTPS
- 敏感信息加密存储
- 定期备份
- GDPR 合规

✅ **输入验证**
- Pydantic 前端验证 (FastAPI)
- React Hook Form 前端验证

---

## 性能优化清单

### 后端优化
- [ ] 数据库查询优化（索引、JOIN 优化）
- [ ] Redis 缓存策略（热数据 TTL）
- [ ] 批量操作优化
- [ ] 异步处理（Celery）
- [ ] 连接池优化

### 前端优化
- [ ] Code splitting (React.lazy)
- [ ] 图片优化 (Next.js Image 或 TanStack Query)
- [ ] 虚拟列表（大列表）
- [ ] 防抖/节流
- [ ] Bundle 分析与减少

---

## 常见问题解答 (FAQ)

### Q: 为什么用 FastAPI 而不是 Django？
**A**: FastAPI 更轻、更快，异步支持原生。适合现代 API 开发。Django 重，适合大型项目。

### Q: 前端可以用 Vue 吗？
**A**: 可以！Vue 3 + TypeScript 也很不错，但本规划用 React 因其生态更丰富。

### Q: 如何处理实时数据更新？
**A**: 使用 WebSocket 或 Server-Sent Events (SSE)。可选集成 FastAPI WebSocket + Redis Pub/Sub。

### Q: 邮件如果失败了怎么办？
**A**: Celery 自动重试（指数退避）。失败日志存入数据库，支持人工重新发送。

### Q: 如何扩展到多个微服务？
**A**: 当单体应用达到性能瓶颈时，将 Service 分离为独立服务，通过 API 网关编排。目前 MVP 阶段单体足够。

---

## 推荐资源

### 学习文档
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [React 官方文档](https://react.dev/)
- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [Celery 官方文档](https://docs.celeryproject.io/)

### 工具与扩展
- [Bruno](https://www.usebruno.com/) - API 客户端（开源，支持本地版本控制）
- [DBeaver](https://dbeaver.io/) - 数据库管理工具
- [Vercel CLI](https://vercel.com/docs/cli) - 本地预览部署

---

## 项目里程碑

| 阶段 | 时间 | 交付物 |
|------|------|--------|
| **MVP** | Week 1-2 | 用户认证 + 目标/任务基础 CRUD |
| **核心功能** | Week 3-4 | 成就系统 + 邮件提醒 |
| **优化** | Week 5-6 | 性能优化 + 测试覆盖 |
| **上线** | Week 7-8 | 安全审计 + 部署验证 |

---

**编写时间**: 2026年2月2日  
**下一步**: 开始初始化项目仓库和本地开发环境
