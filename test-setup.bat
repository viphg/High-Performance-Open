@echo off
REM Windows 批处理文件 - 项目初始化测试脚本

echo.
echo 🚀 High-Performance 项目初始化测试
echo ========================================
echo.

REM 检查 Docker
echo 1️⃣  检查 Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    exit /b 1
)
echo ✅ Docker 已安装

echo.
echo 2️⃣  启动 Docker 容器...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Docker Compose 启动失败
    exit /b 1
)
echo ✅ 容器启动完成

echo.
echo 3️⃣  等待服务初始化... (30秒)
timeout /t 30 /nobreak

echo.
echo 4️⃣  测试后端健康检查...
curl -s http://localhost:8000/health | findstr "healthy" >nul
if errorlevel 1 (
    echo ❌ 后端健康检查失败
    docker-compose logs backend
    exit /b 1
)
echo ✅ 后端健康检查通过

echo.
echo 5️⃣  测试注册 API...
curl -s -X POST http://localhost:8000/api/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"testuser\", \"email\": \"test@example.com\", \"password\": \"password123\", \"full_name\": \"Test User\"}" | findstr "testuser" >nul
if errorlevel 1 (
    echo ❌ 注册 API 测试失败
    exit /b 1
)
echo ✅ 注册 API 测试通过

echo.
echo 6️⃣  测试登录 API...
curl -s -X POST http://localhost:8000/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"testuser\", \"password\": \"password123\"}" | findstr "access_token" >nul
if errorlevel 1 (
    echo ❌ 登录 API 测试失败
    exit /b 1
)
echo ✅ 登录 API 测试通过

echo.
echo ========================================
echo ✅ 所有测试通过！项目已准备好进行开发
echo.
echo 📍 访问地址：
echo    前端: http://localhost:5173
echo    后端 API: http://localhost:8000
echo    API 文档: http://localhost:8000/docs
echo.
echo 📚 查看更多信息：
echo    - 开发指南: DEVELOPMENT.md
echo    - API 文档: docs/04-api-design.md
echo    - 初始化清单: INITIALIZATION_CHECKLIST.md
echo.
