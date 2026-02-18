#!/bin/bash
# 阿里云自动部署脚本

set -e

# 配置变量
SERVER_IP="8.152.199.108"
DOMAIN="highperformance.152.199.108"
PROJECT_DIR="/opt/high-performance"
SSH_USER="root"

echo "=========================================="
echo "🚀 开始阿里云部署"
echo "=========================================="

# 检查SSH连接
echo "1. 检查SSH连接..."
if ! ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "echo 'SSH连接成功'" 2>/dev/null; then
    echo "❌ SSH连接失败"
    echo "请检查:"
    echo "1. 服务器IP是否正确: $SERVER_IP"
    echo "2. SSH密钥是否配置正确"
    echo "3. 服务器是否允许SSH连接"
    exit 1
fi
echo "✅ SSH连接正常"

# 创建服务器目录结构
echo "2. 创建服务器目录结构..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP << 'EOF'
# 创建项目目录
mkdir -p $PROJECT_DIR/{backups,logs,nginx/ssl,ml_models}
mkdir -p $PROJECT_DIR/backups/{postgres,redis,config}
mkdir -p $PROJECT_DIR/logs/{nginx,app}

# 设置权限
chmod -R 755 $PROJECT_DIR
EOF
echo "✅ 服务器目录结构创建完成"

# 上传配置文件
echo "3. 上传配置文件..."
scp -o StrictHostKeyChecking=no docker-compose-aliyun.yml $SSH_USER@$SERVER_IP:$PROJECT_DIR/
scp -o StrictHostKeyChecking=no .env.aliyun $SSH_USER@$SERVER_IP:$PROJECT_DIR/
scp -o StrictHostKeyChecking=no nginx/nginx.conf $SSH_USER@$SERVER_IP:$PROJECT_DIR/nginx/
echo "✅ 配置文件上传完成"

# 停止现有服务
echo "4. 停止现有服务..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP << 'EOF'
cd $PROJECT_DIR
docker-compose -f docker-compose-aliyun.yml down 2>/dev/null || true
docker system prune -f 2>/dev/null || true
EOF

# 拉取最新代码
echo "5. 拉取最新代码..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP << 'EOF'
cd $PROJECT_DIR
if [ -d ".git" ]; then
    cd $PROJECT_DIR
    git pull origin main
else
    cd /opt
    git clone https://github.com/viphg/High-Performance-Open.git high-performance-code
    mv high-performance-code/* $PROJECT_DIR/
    rm -rf high-performance-code
fi
EOF
echo "✅ 代码拉取完成"

# 构建并启动服务
echo "6. 构建并启动Docker服务..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP << 'EOF'
cd $PROJECT_DIR
docker-compose -f docker-compose-aliyun.yml --env-file .env.aliyun build
EOF

echo "✅ Docker构建完成"

# 启动服务
echo "7. 启动服务..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP << 'EOF'
cd $PROJECT_DIR
docker-compose -f docker-compose-aliyun.yml --env-file .env.aliyun up -d

echo "等待服务启动..."
sleep 30

# 检查服务状态
echo "检查Docker服务状态..."
docker-compose -f docker-compose-aliyun.yml --env-file .env.aliyun ps

echo "等待服务完全启动..."
sleep 30
EOF
echo "✅ 服务启动完成"

# 验证部署
echo "8. 验证部署状态..."
sleep 10

# 检查服务健康状态
echo "检查服务健康状态..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP << 'EOF'
cd $PROJECT_DIR

echo "=== Docker服务状态 ==="
docker-compose -f docker-compose-aliyun.yml --env-file .env.aliyun ps

echo ""
echo "=== 健康检查 ==="

# 检查后端健康
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ 后端服务正常"
else
    echo "❌ 后端服务异常"
fi

# 检查前端
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ 前端服务正常"
else
    echo "❌ 前端服务异常"
fi

# 检查数据库
if docker exec hp-postgres-aliyun pg_isready -U user >/dev/null 2>&1; then
    echo "✅ PostgreSQL数据库正常"
else
    echo "❌ PostgreSQL数据库异常"
fi

# 检查Redis
if docker exec hp-redis-aliyun redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis缓存正常"
else
    echo "❌ Redis缓存异常"
fi

echo ""
echo "=== 资源使用情况 ==="
free -h

echo ""
echo "=== 磁盘使用情况 ==="
df -h

echo ""
echo "=== 服务日志 ==="
echo "后端服务日志 (最近20行):"
docker logs --tail 20 hp-backend-aliyun 2>/dev/null || echo "后端日志获取失败"

echo ""
echo "前端服务日志 (最近20行):"
docker logs --tail 20 hp-frontend-aliyun 2>/dev/null || echo "前端日志获取失败"

echo ""
echo "=== 端口监听状态 ==="
netstat -tlnp | grep -E ':(80|3000|5432|6379|8000)' || echo "端口检查失败"

EOF

# 保存部署信息
echo "9. 生成部署报告..."
DEPLOY_REPORT="$PROJECT_DIR/deploy_report_$(date +%Y%m%d_%H%M%S).txt"

ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP << 'EOF'
cat > $DEPLOY_REPORT << 'EOF
==========================================
阿里云部署报告
==========================================

部署时间: $(date)
服务器IP: $SERVER_IP
域名: $DOMAIN
项目目录: $PROJECT_DIR

服务状态检查:
EOF

# 添加服务状态
docker-compose -f docker-compose-aliyun.yml --env-file .env.aliyun ps >> $DEPLOY_REPORT

echo "" >> $DEPLOY_REPORT
echo "健康检查结果:" >> $DEPLOY_REPORT

# 后端检查
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ 后端API: 正常" >> $DEPLOY_REPORT
else
    echo "❌ 后端API: 异常" >> $DEPLOY_REPORT
fi

# 前端检查
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ 前端页面: 正常" >> $DEPLOY_REPORT
else
    echo "❌ 前端页面: 异常" >> $DEPLOY_REPORT
fi

# 数据库检查
if docker exec hp-postgres-aliyun pg_isready -U user >/dev/null 2>&1; then
    echo "✅ PostgreSQL: 正常" >> $DEPLOY_REPORT
else
    echo "❌ PostgreSQL: 异常" >> $DEPLOY_REPORT
fi

# Redis检查
if docker exec hp-redis-aliyun redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis: 正常" >> $DEPLOY_REPORT
else
    echo "❌ Redis: 异常" >> $DEPLOY_REPORT
fi

echo "" >> $DEPLOY_REPORT
echo "访问信息:" >> $DEPLOY_REPORT
echo "前端地址: http://$DOMAIN" >> $DEPLOY_REPORT
echo "后端API: http://$DOMAIN/api" >> $DEPLOY_REPORT
echo "API文档: http://$DOMAIN/docs" >> $DEPLOY_REPORT
echo "健康检查: http://$DOMAIN/health" >> $DEPLOY_REPORT

echo "" >> $DEPLOY_REPORT
echo "管理命令:" >> $DEPLOY_REPORT
echo "查看日志: docker logs -f [container-name]" >> $DEPLOY_REPORT
echo "重启服务: docker-compose -f docker-compose-aliyun.yml restart" >> $DEPLOY_REPORT
echo "更新代码: git pull && docker-compose build && docker-compose up -d" >> $DEPLOY_REPORT

EOF

echo "部署报告已生成: $DEPLOY_REPORT"
EOF

echo ""
echo "=========================================="
echo "🎉 阿里云部署完成!"
echo "=========================================="
echo ""
echo "📋 访问信息:"
echo "  前端应用: http://$DOMAIN"
echo "  后端API: http://$DOMAIN/api"
echo "  API文档: http://$DOMAIN/docs"
echo "  健康检查: http://$DOMAIN/health"
echo ""
echo "🔧 管理命令 (在服务器上执行):"
echo "  查看服务状态: docker-compose ps"
echo "  查看服务日志: docker logs [container-name]"
echo "  重启服务: docker-compose restart [service-name]"
echo "  停止服务: docker-compose stop [service-name]"
echo "  更新服务: git pull && docker-compose build && docker-compose up -d"
echo ""
echo "📞 下一步建议:"
echo "  1. 配置域名解析到 $SERVER_IP"
echo "  2. 设置SSL证书 (可选)"
echo "  3. 配置监控告警 (推荐)"
echo "  4. 设置自动备份 (推荐)"
echo ""
echo "💾 备份文件位置:"
echo "  数据库备份: /opt/high-performance/backups/postgres"
echo "  配置备份: /opt/high-performance/backups/config"
echo "  部署报告: $DEPLOY_REPORT"
echo ""