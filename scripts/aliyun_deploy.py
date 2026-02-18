#!/usr/bin/env python3
"""
阿里云部署脚本 - 自动化部署到阿里云服务器
"""

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class AliyunDeployer:
    def __init__(self):
        self.project_root = Path("D:/OPENPROJECT/High-Performance-Open")
        self.ssh_key_path = self.project_root / "aliyun_key.pem"
        
    def create_aliyun_ssh_key(self):
        """创建阿里云SSH密钥配置"""
        print("🔑 创建阿里云SSH配置...")
        
        ssh_config = """
# 阿里云SSH配置
# 使用方法: ssh root@your_server_ip

# 配置说明:
# 1. 将此内容追加到 ~/.ssh/config
# 2. 或者使用: ssh -i ~/.ssh/aliyun_key.pem root@your_server_ip

Host aliyun-server
    HostName YOUR_SERVER_IP  # 替换为您的服务器IP
    User root
    Port 22
    IdentityFile ~/.ssh/aliyun_key.pem
    StrictHostKeyChecking no
    UserKnownHostsFile ~/.ssh/known_hosts
    
    # 也可以使用域名
Host aliyun-domain
    HostName YOUR_DOMAIN     # 替换为您的域名
    User root
    Port 22
    IdentityFile ~/.ssh/aliyun_key.pem
    StrictHostKeyChecking no
"""
        
        config_path = self.project_root / "aliyun_ssh_config.txt"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(ssh_config)
        
        print(f"✅ SSH配置已创建: {config_path}")
        return config_path
    
    def create_docker_compose_aliyun(self):
        """创建阿里云专用的Docker Compose配置"""
        print("🐳 创建阿里云Docker配置...")
        
        aliyun_compose = """
version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    container_name: hp-postgres-aliyun
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-password123!@#}
      POSTGRES_DB: high_performance_aliyun
    volumes:
      - postgres_data_aliyun:/var/lib/postgresql/data
      - ./backups/postgres:/var/lib/postgresql/backups
    ports:
      - "5432:5432"
    networks:
      - aliyun_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d high_performance_aliyun"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: hp-redis-aliyun
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-redis123!@#}
    volumes:
      - redis_data_aliyun:/data
      - ./backups/redis:/var/lib/redis/backups
    ports:
      - "6379:6379"
    networks:
      - aliyun_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # 后端服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: hp-backend-aliyun
    environment:
      DATABASE_URL: postgresql://user:${POSTGRES_PASSWORD:-password123!@#}@postgres:5432/high_performance_aliyun
      REDIS_URL: redis://:${REDIS_PASSWORD:-redis123!@#}@redis:6379/0
      SECRET_KEY: ${SECRET_KEY:-your-production-secret-key-change-this}
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 1440  # 24小时
      DEBUG: "false"
      ENVIRONMENT: production
      SMTP_SERVER: ${SMTP_SERVER:-smtp.aliyun.com}
      SMTP_PORT: ${SMTP_PORT:-465}
      SMTP_USER: ${SMTP_USER}
      SMTP_PASSWORD: ${SMTP_PASSWORD}
      FROM_EMAIL: ${FROM_EMAIL:-noreply@highperformance.com}
      CORS_ORIGINS: '["https://${DOMAIN:-your-domain.com}", "https://www.${DOMAIN:-your-domain.com}"]
      
      # 智能推荐功能配置
      ENABLE_INTELLIGENT_RECOMMENDATIONS: "true"
      ENABLE_ML_FEATURES: "true"
      ENABLE_ADVANCED_ANALYTICS: "true"
    volumes:
      - ./backups:/app/backups
      - ./logs:/app/logs
      - ./ml_models:/app/ml_models
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - aliyun_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 前端服务
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: hp-frontend-aliyun
    environment:
      VITE_API_URL: http://${DOMAIN:-your-domain.com}:8000/api
      VITE_NODE_ENV: production
      VITE_APP_NAME: High-Performance-Aliyun
      VITE_APP_VERSION: 1.1.0-aliyun
    ports:
      - "80:80"  # HTTP
      - "443:443"  # HTTPS (如果有SSL证书)
    depends_on:
      - backend
    networks:
      - aliyun_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx反向代理 (推荐)
  nginx:
    image: nginx:alpine
    container_name: hp-nginx-aliyun
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro  # SSL证书目录
      - ./logs/nginx:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - frontend
    networks:
      - aliyun_network
    restart: unless-stopped

networks:
  aliyun_network:
    driver: bridge

volumes:
  postgres_data_aliyun:
  redis_data_aliyun:
"""
        
        compose_path = self.project_root / "docker-compose-aliyun.yml"
        with open(compose_path, 'w', encoding='utf-8') as f:
            f.write(aliyun_compose)
        
        print(f"✅ 阿里云Docker配置已创建: {compose_path}")
        return compose_path
    
    def create_environment_file(self):
        """创建阿里云环境变量文件"""
        print("📝 创建阿里云环境变量...")
        
        env_content = """
# 阿里云生产环境配置
# 请根据实际情况修改以下配置

# 数据库配置
POSTGRES_PASSWORD=your-secure-postgres-password-123!

# Redis配置
REDIS_PASSWORD=your-secure-redis-password-123!

# JWT配置
SECRET_KEY=your-super-secure-production-secret-key-change-this-456789

# 域名配置
DOMAIN=your-domain.com  # 替换为您的实际域名

# 邮件配置 (阿里云邮件推送服务)
SMTP_SERVER=smtp.aliyun.com
SMTP_PORT=465
SMTP_USER=your-email@your-domain.com
SMTP_PASSWORD=your-aliyun-smtp-password
FROM_EMAIL=noreply@highperformance.com

# SSL证书配置 (如果使用HTTPS)
SSL_CERT_PATH=./nginx/ssl/cert.pem
SSL_KEY_PATH=./nginx/ssl/key.pem

# 监控配置
MONITORING_ENABLED=true
SENTRY_DSN=your-sentry-dsn-here

# 备份配置
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"  # 每天凌晨2点备份
BACKUP_RETENTION_DAYS=30

# 性能配置
WORKER_PROCESSES=4
CACHE_TTL=3600
RATE_LIMIT=1000

# 安全配置
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
SECURE_COOKIES=true
CORS_CREDENTIALS=false
"""
        
        env_path = self.project_root / ".env.aliyun"
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ 阿里云环境变量已创建: {env_path}")
        return env_path
    
    def create_nginx_config(self):
        """创建Nginx配置"""
        print("🌐 创建Nginx反向代理配置...")
        
        nginx_dir = self.project_root / "nginx"
        nginx_dir.mkdir(exist_ok=True)
        
        nginx_config = """
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL配置
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # 日志
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # 限制请求大小
    client_max_body_size 10M;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
    
    # 后端API代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时时间
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket支持 (用于实时功能)
    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 前端静态文件
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 缓存静态资源
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 健康检查
    location /health {
        proxy_pass http://backend:8000/health;
        access_log off;
    }
    
    # 禁止访问敏感文件
    location ~ /\. {
        deny all;
    }
    
    location ~ /admin/ {
        auth_basic "Restricted Area";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
"""
        
        config_path = nginx_dir / "nginx.conf"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(nginx_config)
        
        print(f"✅ Nginx配置已创建: {config_path}")
        return config_path
    
    def create_deploy_script(self):
        """创建部署脚本"""
        print("🚀 创建部署脚本...")
        
        deploy_script = """
#!/bin/bash

# 阿里云部署脚本
# 使用方法: ./deploy_aliyun.sh

set -e

echo "🚀 开始阿里云部署..."

# 配置变量
SERVER_IP="YOUR_SERVER_IP"  # 替换为您的服务器IP
DOMAIN="your-domain.com"     # 替换为您的域名
SSH_KEY="~/.ssh/aliyun_key.pem"

# 检查SSH连接
echo "🔍 检查SSH连接..."
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH密钥文件不存在: $SSH_KEY"
    echo "请确保aliyun_key.pem文件在~/.ssh/目录中"
    exit 1
fi

if ! ssh -i "$SSH_KEY" root@"$SERVER_IP" "echo 'SSH连接成功'" 2>/dev/null; then
    echo "❌ SSH连接失败，请检查:"
    echo "1. 服务器IP是否正确: $SERVER_IP"
    echo "2. SSH密钥是否正确配置"
    echo "3. 服务器是否允许SSH连接"
    echo "4. 网络连接是否正常"
    exit 1
fi

echo "✅ SSH连接正常"

# 创建服务器目录结构
echo "📁 创建服务器目录结构..."
ssh -i "$SSH_KEY" root@"$SERVER_IP" << 'EOF'
mkdir -p /opt/high-performance/{backups,logs,nginx/ssl,ml_models}
mkdir -p /opt/high-performance/backups/{postgres,redis,config}
EOF

# 上传配置文件
echo "📤 上传配置文件..."
scp -i "$SSH_KEY" docker-compose-aliyun.yml root@"$SERVER_IP":/opt/high-performance/
scp -i "$SSH_KEY" .env.aliyun root@"$SERVER_IP":/opt/high-performance/
scp -i "$SSH_KEY" nginx/nginx.conf root@"$SERVER_IP":/opt/high-performance/nginx/

# 创建环境变量文件
echo "⚙️ 创建服务器环境变量..."
ssh -i "$SSH_KEY" root@"$SERVER_IP" << 'EOF'
cat > /opt/high-performance/docker-compose-override.yml << EOL
version: '3.8'
services:
  backend:
    environment:
      - DOMAIN=${DOMAIN}
  frontend:
    environment:
      - VITE_API_URL=http://${DOMAIN}:8000/api
EOL
EOF

# 停止现有服务
echo "🛑 停止现有服务..."
ssh -i "$SSH_KEY" root@"$SERVER_IP" "cd /opt/high-performance && docker-compose -f docker-compose-aliyun.yml down 2>/dev/null || true"

# 拉取最新代码
echo "📥 拉取最新代码..."
ssh -i "$SSH_KEY" root@"$SERVER_IP" << 'EOF'
if [ -d "/opt/high-performance/code" ]; then
    cd /opt/high-performance/code
    git pull origin main
else
    cd /opt
    git clone https://github.com/viphg/High-Performance-Open.git high-performance-code
    mv high-performance/code/* /opt/high-performance/
fi
EOF

# 构建并启动服务
echo "🐳 构建并启动服务..."
ssh -i "$SSH_KEY" root@"$SERVER_IP" << 'EOF'
cd /opt/high-performance
docker-compose -f docker-compose-aliyun.yml --env-file .env.aliyun build
docker-compose -f docker-compose-aliyun.yml --env-file .env.aliyun up -d

echo "等待服务启动..."
sleep 30

# 检查服务状态
docker-compose -f docker-compose-aliyun.yml --env-file .env.aliyun ps
EOF

# 验证部署
echo "✅ 验证部署状态..."
echo "等待服务完全启动..."
sleep 60

echo "🔍 检查服务状态..."
ssh -i "$SSH_KEY" root@"$SERVER_IP" << 'EOF'
cd /opt/high-performance
echo "=== Docker服务状态 ==="
docker-compose -f docker-compose-aliyun.yml --env-file .env.aliyun ps

echo ""
echo "=== 健康检查 ==="
curl -s http://localhost:8000/health || echo "后端健康检查失败"
curl -s http://localhost:80/ || echo "前端访问检查失败"

echo ""
echo "=== 服务日志 ==="
echo "后端服务日志:"
docker logs --tail 50 hp-backend-aliyun
EOF

echo ""
echo "🎉 部署完成!"
echo "=========================================="
echo "📋 访问信息:"
echo "  🌐 前端: https://$DOMAIN"
echo "  🔗 后端API: https://$DOMAIN/api"
echo "  📖 API文档: https://$DOMAIN/docs"
echo "  🏥 健康检查: https://$DOMAIN/health"
echo ""
echo "🔧 管理命令:"
echo "  查看日志: ssh -i aliyun_key.pem root@$SERVER_IP 'cd /opt/high-performance && docker-compose logs'"
echo "  重启服务: ssh -i aliyun_key.pem root@$SERVER_IP 'cd /opt/high-performance && docker-compose restart'"
echo "  更新代码: ssh -i aliyun_key.pem root@$SERVER_IP 'cd /opt/high-performance && git pull && docker-compose build && docker-compose up -d'"
echo "=========================================="
"""
        
        script_path = self.project_root / "deploy_aliyun.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(deploy_script)
        
        # 设置执行权限
        try:
            os.chmod(script_path, 0o755)
        except:
            pass
        
        print(f"✅ 部署脚本已创建: {script_path}")
        return script_path
    
    def create_monitoring_setup(self):
        """创建监控配置"""
        print("📊 创建监控配置...")
        
        monitoring_dir = self.project_root / "monitoring"
        monitoring_dir.mkdir(exist_ok=True)
        
        # 健康检查脚本
        health_check = """#!/bin/bash

# 健康检查脚本
DOMAIN="your-domain.com"

echo "🔍 执行健康检查..."
echo "时间: $(date)"
echo "================================"

# 检查服务状态
if command -v docker-compose >/dev/null 2>&1; then
    echo "📋 Docker服务状态:"
    docker-compose ps
else
    echo "❌ Docker未安装"
fi

echo ""

# 检查Web服务
echo "🌐 Web服务检查:"
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ 后端服务正常"
else
    echo "❌ 后端服务异常"
fi

if curl -s http://localhost:80 >/dev/null; then
    echo "✅ 前端服务正常"
else
    echo "❌ 前端服务异常"
fi

echo ""

# 检查数据库
echo "🗄️ 数据库检查:"
if command -v docker >/dev/null 2>&1; then
    if docker exec hp-postgres-aliyun pg_isready -U user >/dev/null 2>&1; then
        echo "✅ PostgreSQL正常"
    else
        echo "❌ PostgreSQL异常"
    fi
fi

if command -v docker >/dev/null 2>&1; then
    if docker exec hp-redis-aliyun redis-cli ping >/dev/null 2>&1; then
        echo "✅ Redis正常"
    else
        echo "❌ Redis异常"
    fi
fi

echo ""
echo "📈 资源使用情况:"
if command -v free >/dev/null 2>&1; then
    free -h
fi

echo ""
echo "🖥️ 磁盘使用情况:"
if command -v df >/dev/null 2>&1; then
    df -h
fi

echo "================================"
"""
        
        health_path = monitoring_dir / "health_check.sh"
        with open(health_path, 'w', encoding='utf-8') as f:
            f.write(health_check)
        
        os.chmod(health_path, 0o755)
        
        print(f"✅ 健康检查脚本已创建: {health_path}")
        return health_path
    
    def create_backup_automation(self):
        """创建自动备份脚本"""
        print("💾 创建自动备份脚本...")
        
        backup_script = """#!/bin/bash

# 自动备份脚本
BACKUP_DIR="/opt/high-performance/backups"
RETENTION_DAYS=30

# 数据库备份
echo "📊 备份PostgreSQL数据库..."
docker exec hp-postgres-aliyun pg_dump -U user -d high_performance_aliyun > "$BACKUP_DIR/postgres/postgres_backup_$(date +%Y%m%d_%H%M%S).sql"

# Redis备份
echo "📈 备份Redis数据..."
docker exec hp-redis-aliyun redis-cli --rdb /var/lib/redis/dump.rdb
cp /var/lib/redis/dump.rdb "$BACKUP_DIR/redis/redis_backup_$(date +%Y%m%d_%H%M%S).rdb"

# 配置文件备份
echo "⚙️ 备份配置文件..."
tar -czf "$BACKUP_DIR/config/config_backup_$(date +%Y%m%d_%H%M%S).tar.gz" /opt/high-performance/.env.aliyun /opt/high-performance/nginx.conf

# 清理旧备份
echo "🧹 清理旧备份..."
find "$BACKUP_DIR" -name "*.sql" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.rdb" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "✅ 备份完成"
"""
        
        backup_path = self.project_root / "scripts" / "backup_automation.sh"
        backup_path.parent.mkdir(exist_ok=True)
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(backup_script)
        
        os.chmod(backup_path, 0o755)
        
        print(f"✅ 备份脚本已创建: {backup_path}")
        return backup_path

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 阿里云部署配置创建器")
    print("=" * 60)
    print()
    
    deployer = AliyunDeployer()
    
    # 1. 创建SSH配置
    deployer.create_aliyun_ssh_key()
    
    # 2. 创建Docker配置
    deployer.create_docker_compose_aliyun()
    
    # 3. 创建环境变量
    deployer.create_environment_file()
    
    # 4. 创建Nginx配置
    deployer.create_nginx_config()
    
    # 5. 创建部署脚本
    deployer.create_deploy_script()
    
    # 6. 创建监控配置
    deployer.create_monitoring_setup()
    
    # 7. 创建备份自动化
    deployer.create_backup_automation()
    
    print()
    print("✅ 所有配置文件已创建完成!")
    print("📋 创建的文件:")
    print("  🔑 aliyun_ssh_config.txt - SSH连接配置")
    print("  🐳 docker-compose-aliyun.yml - Docker服务配置")
    print("  📝 .env.aliyun - 环境变量配置")
    print("  🌐 nginx/nginx.conf - Nginx反向代理配置")
    print("  🚀 deploy_aliyun.sh - 自动部署脚本")
    print("  📊 monitoring/health_check.sh - 健康检查脚本")
    print("  💾 scripts/backup_automation.sh - 自动备份脚本")
    print()
    print("🎯 下一步操作:")
    print("=" * 60)
    print("1. 📋 查看并修改配置文件")
    print("   - 编辑 .env.aliyun 设置实际的域名和密码")
    print("   - 编辑 deploy_aliyun.sh 设置服务器IP")
    print("   - 编辑 nginx.conf 设置实际域名")
    print()
    print("2. 🔑 准备阿里云服务器SSH密钥")
    print("   - 将阿里云服务器的SSH私钥保存到 ~/.ssh/aliyun_key.pem")
    print("   - 设置正确的权限: chmod 400 ~/.ssh/aliyun_key.pem")
    print()
    print("3. 🚀 执行部署:")
    print("   ./deploy_aliyun.sh")
    print()
    print("4. 🔍 验证部署:")
    print("   访问: https://your-domain.com")
    print("   健康检查: curl https://your-domain.com/health")
    print("   查看日志: ./monitoring/health_check.sh")
    print("=" * 60)

if __name__ == "__main__":
    main()