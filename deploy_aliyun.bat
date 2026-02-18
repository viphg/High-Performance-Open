@echo off
setlocal enabledelayedexpansion

echo ========================================
echo 🚀 阿里云部署脚本 - Windows版本
echo ========================================
echo.

echo 1. 设置配置变量
set SERVER_IP=8.152.199.108
set DOMAIN=highperformance.152.199.108
set SSH_USER=root
set PROJECT_DIR=/opt/high-performance
set SSH_KEY=aliyun_key.pem

echo 当前配置:
echo   服务器IP: %SERVER_IP%
echo   域名: %DOMAIN%
echo   项目目录: %PROJECT_DIR%
echo.

echo 2. 检查必要文件
if not exist "docker-compose-aliyun.yml" (
    echo ❌ Docker配置文件不存在
    echo 请先运行: python scripts/create_aliyun_config.py
    pause
    exit /b 1
)

if not exist ".env.aliyun" (
    echo ❌ 环境变量文件不存在
    echo 请先运行: python scripts/create_aliyun_config.py
    pause
    exit /b 1
)

echo ✅ 配置文件检查通过
echo.

echo 3. 测试SSH连接
echo 🔍 检查SSH连接到 %SERVER_IP%...
ssh -o StrictHostKeyChecking=no %SSH_KEY%@SSH_USER%@SERVER_IP% "echo 'SSH连接测试成功'" 2>nul

if errorlevel 1 (
    echo ❌ SSH连接失败
    echo 请检查:
    echo 1. 服务器IP是否正确: %SERVER_IP%
    echo 2. SSH密钥是否在正确位置
    echo 3. 服务器SSH服务是否开启
    echo 4. 网络连接是否正常
    pause
    exit /b 1
)
echo ✅ SSH连接正常
echo.

echo 4. 上传配置文件到服务器
echo 📤 上传Docker配置...
scp -o StrictHostKeyChecking=no docker-compose-aliyun.yml %SSH_USER%@SERVER_IP%:%PROJECT_DIR%/
if errorlevel 1 (
    echo ❌ Docker配置上传失败
    pause
    exit /b 1
)
echo ✅ Docker配置上传完成

echo 📤 上传环境变量...
scp -o StrictHostKeyChecking=no .env.aliyun %SSH_USER%@SERVER_IP%:%PROJECT_DIR%/
if errorlevel 1 (
    echo ❌ 环境变量上传失败
    pause
    exit /b 1
)
echo ✅ 环境变量上传完成

echo.

echo 5. 服务器端操作
echo 🖥 在服务器上执行初始化...
ssh -o StrictHostKeyChecking=no %SSH_USER%@SERVER_IP% ^
    "cd %PROJECT_DIR% && mkdir -p backups/{postgres,redis,config} logs/{nginx,app} nginx/ssl ml_models"
if errorlevel 1 (
    echo ❌ 服务器目录创建失败
    pause
    exit /b 1
)
echo ✅ 服务器目录创建完成

echo.

echo 6. 停止现有服务
echo 🛑 停止现有Docker服务...
ssh -o StrictHostKeyChecking=no %SSH_USER%@SERVER_IP% ^
    "cd %PROJECT_DIR% && docker-compose -f docker-compose-aliyun.yml down 2>nul || echo '无现有服务需要停止'"
if errorlevel 1 (
    echo ⚠️ 服务器操作失败，继续执行...
)

echo.

echo 7. 拉取最新代码
echo 📥 拉取最新代码...
ssh -o StrictHostKeyChecking=no %SSH_USER%@SERVER_IP% ^
    "cd %PROJECT_DIR% && if [ -d code ]; then cd code && git pull origin main; else cd /opt && git clone https://github.com/viphg/High-Performance-Open.git high-performance-code; mv high-performance-code/* %PROJECT_DIR/ && rm -rf high-performance-code; fi"
if errorlevel 1 (
    echo ❌ 代码拉取失败
    pause
    exit /b 1
)
echo ✅ 代码拉取完成

echo.

echo 8. 构建并启动服务
echo 🐳 构建Docker镜像...
ssh -o StrictHostKeyChecking=no %SSH_USER%@SERVER_IP% ^
    "cd %PROJECT_DIR% && docker-compose -f docker-compose-aliyun.yml --env-file .env.aliyun build"
if errorlevel 1 (
    echo ❌ Docker构建失败
    pause
    exit /b 1
)
echo ✅ Docker构建完成

echo 🚀 启动Docker服务...
ssh -o StrictHostKeyChecking=no %SSH_USER%@SERVER_IP% ^
    "cd %PROJECT_DIR% && docker-compose -f docker-compose-aliyun.yml --env-file .env.aliyun up -d"
if errorlevel 1 (
    echo ❌ Docker服务启动失败
    pause
    exit /b 1
)
echo ✅ Docker服务启动完成

echo.

echo 9. 等待服务完全启动
echo ⏳ 等待服务完全启动...
timeout /t 60 ssh -o StrictHostKeyChecking=no %SSH_USER%@SERVER_IP% "echo '等待30秒...' && sleep 30"

echo 🔍 检查服务状态...
ssh -o StrictHostKeyChecking=no %SSH_USER%@SERVER_IP% ^
    "cd %PROJECT_DIR% && docker-compose -f docker-compose-aliyun.yml --env-file .env.aliyun ps"

echo.

echo 10. 验证部署
echo 🔍 验证部署状态...
echo 检查后端API...
ssh -o StrictHostKeyChecking=no %SSH_USER%@SERVER_IP% ^
    "cd %PROJECT_DIR% && timeout 10 curl -s http://localhost:8000/health"
if errorlevel 1 (
    echo ❌ 后端API未响应
) else (
    echo ✅ 后端API正常
)

echo 检查前端应用...
ssh -o StrictHostKeyChecking=no %SSH_USER%@SERVER_IP% ^
    "cd %PROJECT_DIR% && timeout 10 curl -s http://localhost:3000"
if errorlevel 1 (
    echo ❌ 前端应用未响应
) else (
    echo ✅ 前端应用正常
)

echo.
echo ========================================
echo 🎉 阿里云部署完成!
echo ========================================
echo.
echo 📋 访问信息:
echo    前端应用: http://%DOMAIN%
echo    后端API: http://%DOMAIN%/api
echo    API文档: http://%DOMAIN%/docs
echo    健康检查: http://%DOMAIN%/health
echo.
echo 🔧 管理命令 (在服务器上执行):
echo    查看服务状态: cd %PROJECT_DIR% && docker-compose ps
echo    查看服务日志: cd %PROJECT_DIR% && docker logs [service-name]
echo    重启服务: cd %PROJECT_DIR% && docker-compose restart [service-name]
echo    停止服务: cd %PROJECT_DIR% && docker-compose stop [service-name]
echo.
echo 📊 监控页面 (后续建议):
echo    1. 配置阿里云监控告警
echo    2. 设置域名解析到服务器IP
echo    3. 配置SSL证书启用HTTPS
echo    4. 设置防火墙规则
echo.

pause