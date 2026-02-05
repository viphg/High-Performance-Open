# REST API 设计规范

## 概述

本文档定义了 High-Performance 平台的 REST API 设计规范，包括命名约定、请求/响应格式、错误处理、认证和授权机制。

---

## 1. 基础约定

### 1.1 API 基础 URL
```
生产环境: https://api.highperformance.com/api/v1
开发环境: http://localhost:8000/api/v1
```

### 1.2 API 版本控制
- 使用 URL 前缀方式进行版本控制：`/api/v1`, `/api/v2`
- 新增功能优先在最新版本中实现
- 废弃 API 会提前 3 个月通知

### 1.3 请求/响应格式
- 所有请求和响应都使用 **JSON** 格式
- 请求头必须包含：`Content-Type: application/json`
- 字符编码统一为 **UTF-8**

---

## 2. 标准响应格式

### 2.1 成功响应 (2xx)

#### 单个资源响应 (GET, POST, PUT, DELETE)
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": 1,
    "name": "Example",
    ...
  },
  "timestamp": "2026-02-02T10:30:00Z"
}
```

#### 列表响应 (GET with pagination)
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      { "id": 1, "name": "Item 1" },
      { "id": 2, "name": "Item 2" }
    ],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "total_pages": 10
  },
  "timestamp": "2026-02-02T10:30:00Z"
}
```

### 2.2 错误响应 (4xx, 5xx)

```json
{
  "code": 400,
  "message": "请求参数错误",
  "errors": [
    {
      "field": "email",
      "message": "邮箱格式不正确"
    }
  ],
  "timestamp": "2026-02-02T10:30:00Z"
}
```

### 2.3 HTTP 状态码

| 状态码 | 说明 | 场景 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 删除成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证或令牌过期 |
| 403 | Forbidden | 没有权限访问 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突（如用户已存在） |
| 422 | Unprocessable Entity | 数据验证失败 |
| 500 | Internal Server Error | 服务器错误 |

---

## 3. 认证与授权

### 3.1 认证方式
- 使用 **JWT (JSON Web Token)** 进行身份验证
- Token 类型：Bearer Token
- 过期时间：30 分钟

### 3.2 获取 Token

**请求**
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

**成功响应 (200)**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": 1,
      "username": "user@example.com",
      "email": "user@example.com",
      "full_name": "John Doe",
      "is_active": true
    }
  },
  "timestamp": "2026-02-02T10:30:00Z"
}
```

### 3.3 使用 Token

在请求头中添加 Authorization 字段：

```
Authorization: Bearer {access_token}
```

### 3.4 刷新 Token

**请求**
```
POST /api/v1/auth/refresh
Authorization: Bearer {access_token}
```

**成功响应 (200)**
```json
{
  "code": 200,
  "message": "Token 刷新成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

## 4. 命名约定

### 4.1 URL 路径

- 资源名使用**小写复数**形式：`/users`, `/goals`, `/tasks`
- 使用 RESTful 风格：
  - `GET /users` - 获取用户列表
  - `POST /users` - 创建用户
  - `GET /users/:id` - 获取单个用户
  - `PUT /users/:id` - 更新用户
  - `DELETE /users/:id` - 删除用户
- 嵌套资源：`GET /goals/:goal_id/tasks` - 获取某个目标下的所有任务

### 4.2 查询参数

- 分页：`page=1&page_size=10`
- 排序：`sort_by=created_at&sort_order=desc`
- 搜索：`search=keyword`
- 过滤：`status=active&priority=high`

### 4.3 字段名称

- 使用 **snake_case** 命名：`created_at`, `full_name`, `is_active`
- 日期时间字段使用 ISO 8601 格式：`2026-02-02T10:30:00Z`
- Boolean 字段以 `is_` 或 `has_` 开头：`is_active`, `has_completed`

---

## 5. 分页规范

### 5.1 分页参数

```
GET /api/v1/users?page=1&page_size=20
```

### 5.2 分页响应

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

---

## 6. 错误处理

### 6.1 错误响应格式

```json
{
  "code": 400,
  "message": "请求失败",
  "errors": [
    {
      "field": "email",
      "message": "邮箱已被使用"
    }
  ],
  "timestamp": "2026-02-02T10:30:00Z"
}
```

### 6.2 常见错误码

| 错误码 | HTTP 状态 | 说明 |
|--------|-----------|------|
| 400 | 400 | 请求参数错误 |
| 401 | 401 | 未认证或 Token 过期 |
| 403 | 403 | 权限不足 |
| 404 | 404 | 资源不存在 |
| 409 | 409 | 资源冲突 |
| 422 | 422 | 数据验证失败 |
| 500 | 500 | 服务器内部错误 |

---

## 7. 核心 API 端点

### 7.1 用户认证

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/auth/register` | 用户注册 |
| POST | `/auth/login` | 用户登录 |
| POST | `/auth/logout` | 用户登出 |
| POST | `/auth/refresh` | 刷新 Token |
| GET | `/auth/me` | 获取当前用户信息 |

### 7.2 用户管理

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/users` | 获取用户列表 |
| GET | `/users/:id` | 获取单个用户 |
| PUT | `/users/:id` | 更新用户信息 |
| DELETE | `/users/:id` | 删除用户 |

### 7.3 目标管理

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/goals` | 获取目标列表 |
| POST | `/goals` | 创建新目标 |
| GET | `/goals/:id` | 获取单个目标详情 |
| PUT | `/goals/:id` | 更新目标 |
| DELETE | `/goals/:id` | 删除目标 |
| POST | `/goals/:id/complete` | 标记目标完成 |

### 7.4 任务管理

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/tasks` | 获取任务列表 |
| POST | `/tasks` | 创建新任务 |
| GET | `/tasks/:id` | 获取单个任务详情 |
| PUT | `/tasks/:id` | 更新任务 |
| DELETE | `/tasks/:id` | 删除任务 |
| POST | `/tasks/:id/complete` | 标记任务完成 |

### 7.5 成就系统

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/achievements` | 获取成就列表 |
| GET | `/achievements/user/:id` | 获取用户成就 |
| POST | `/achievements/:id/unlock` | 解锁成就 |

---

## 8. 请求示例

### 8.1 创建目标

**请求**
```bash
curl -X POST http://localhost:8000/api/v1/goals \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "学习 Python",
    "description": "掌握 Python 基础",
    "start_date": "2026-02-02",
    "end_date": "2026-05-02",
    "priority": "high"
  }'
```

**响应**
```json
{
  "code": 201,
  "message": "目标创建成功",
  "data": {
    "id": 1,
    "title": "学习 Python",
    "description": "掌握 Python 基础",
    "start_date": "2026-02-02",
    "end_date": "2026-05-02",
    "priority": "high",
    "status": "in_progress",
    "created_at": "2026-02-02T10:30:00Z",
    "updated_at": "2026-02-02T10:30:00Z"
  }
}
```

### 8.2 获取任务列表

**请求**
```bash
curl -X GET "http://localhost:8000/api/v1/tasks?page=1&page_size=10&status=pending" \
  -H "Authorization: Bearer {access_token}"
```

**响应**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "学习第一章",
        "goal_id": 1,
        "status": "pending",
        "priority": "high",
        "created_at": "2026-02-02T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 5,
      "total_pages": 1
    }
  }
}
```

---

## 9. 速率限制

### 9.1 限制策略

- 未认证用户：100 请求/小时
- 认证用户：1000 请求/小时
- 超过限制返回 429 Too Many Requests

### 9.2 响应头

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

---

## 10. 版本更新日志

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-02-02 | 初始版本 |

---

## 11. 最佳实践

1. **总是返回结构化响应** - 即使是空数据也要保持格式一致
2. **使用合适的 HTTP 状态码** - 不要过度使用 200
3. **提供清晰的错误信息** - 帮助客户端快速定位问题
4. **使用 Token 进行认证** - 不要在 URL 中传递敏感信息
5. **实施速率限制** - 防止滥用
6. **记录所有 API 访问** - 便于故障排查和监控
7. **版本控制** - 保证向后兼容性

---

**最后更新**: 2026-02-02  
**作者**: High-Performance Team
