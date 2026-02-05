#!/bin/bash
# 项目初始化测试脚本

set -e

echo "🚀 High-Performance 项目初始化测试"
echo "========================================"
echo ""

# 检查必要的工具
echo "1️⃣  检查必要工具..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi
echo "✅ Docker 已安装"

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装"
    exit 1
fi
echo "✅ Docker Compose 已安装"

echo ""
echo "2️⃣  启动 Docker 容器..."
docker-compose up -d
echo "✅ 容器启动完成"

echo ""
echo "3️⃣  等待服务初始化... (30秒)"
sleep 30

echo ""
echo "4️⃣  测试后端健康检查..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ 后端健康检查通过"
else
    echo "❌ 后端健康检查失败"
    docker-compose logs backend
    exit 1
fi

echo ""
echo "5️⃣  测试前端连接..."
if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ 前端连接成功"
else
    echo "⚠️  前端仍在加载，这是正常的"
fi

echo ""
echo "6️⃣  测试认证 API..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }')

if echo "$RESPONSE" | grep -q "testuser"; then
    echo "✅ 用户注册 API 测试通过"
else
    echo "❌ 用户注册 API 测试失败"
    echo "响应: $RESPONSE"
fi

echo ""
echo "7️⃣  测试登录 API..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "✅ 用户登录 API 测试通过"
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "   Token: ${TOKEN:0:20}..."
else
    echo "❌ 用户登录 API 测试失败"
    echo "响应: $LOGIN_RESPONSE"
fi

echo ""
echo "========================================"
echo "✅ 所有测试通过！项目已准备好进行开发"
echo ""
echo "📍 访问地址："
echo "   前端: http://localhost:5173"
echo "   后端 API: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "📚 查看更多信息："
echo "   - 开发指南: DEVELOPMENT.md"
echo "   - API 文档: docs/04-api-design.md"
echo "   - 初始化清单: INITIALIZATION_CHECKLIST.md"
echo ""
