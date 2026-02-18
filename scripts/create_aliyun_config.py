#!/usr/bin/env python3
"""
阿里云部署配置 - 简化版本，避免编码问题
"""

import os
from pathlib import Path

def main():
    print("=== 阿里云部署配置 ===")
    
    project_root = Path("D:/OPENPROJECT/High-Performance-Open")
    
    # 创建配置目录
    nginx_dir = project_root / "nginx"
    nginx_dir.mkdir(exist_ok=True)
    
    # 1. 创建阿里云专用的 docker-compose 文件
    aliyun_compose = """version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: hp-postgres-aliyun
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-Aliyun123!@#}
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

  redis:
    image: redis:7-alpine
    container_name: hp-redis-aliyun
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-Aliyun123!@#}
    volumes:
      - redis_data_aliyun:/data
      - ./backups/redis:/var/lib/redis/backups
    ports:
      - "6379:6379"
    networks:
      - aliyun_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: hp-backend-aliyun
    environment:
      DATABASE_URL: postgresql://user:${POSTGRES_PASSWORD:-Aliyun123!@#}@postgres:5432/high_performance_aliyun
      REDIS_URL: redis://:${REDIS_PASSWORD:-Aliyun123!@#}@redis:6379/0
      SECRET_KEY: ${SECRET_KEY:-your-production-secret-key-change-this-456789}
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 1440
      DEBUG: "false"
      ENVIRONMENT: production
      SMTP_SERVER: ${SMTP_SERVER:-smtp.aliyun.com}
      SMTP_PORT: ${SMTP_PORT:-465}
      SMTP_USER: ${SMTP_USER}
      SMTP_PASSWORD: ${SMTP_PASSWORD}
      FROM_EMAIL: ${FROM_EMAIL:-noreply@highperformance.com}
      CORS_ORIGINS: '["https://${DOMAIN:-highperformance.152.199.108}", "https://www.${DOMAIN:-highperformance.152.199.108}"]
      
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

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: hp-frontend-aliyun
    environment:
      VITE_API_URL: http://${DOMAIN:-highperformance.152.199.108}:8000/api
      VITE_NODE_ENV: production
      VITE_APP_NAME: High-Performance-Aliyun
      VITE_APP_VERSION: 1.1.0-aliyun
    ports:
      - "3000:80"
    depends_on:
      - backend
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
    
    compose_path = project_root / "docker-compose-aliyun.yml"
    with open(compose_path, 'w', encoding='utf-8') as f:
        f.write(aliyun_compose)
    
    print(f"阿里云Docker配置已创建: {compose_path}")
    
    # 2. 创建环境变量文件
    env_content = """# 阿里云生产环境配置
# 请根据实际情况修改以下配置

# 数据库配置
POSTGRES_PASSWORD=Aliyun123!@#

# Redis配置
REDIS_PASSWORD=Aliyun123!@#

# JWT配置
SECRET_KEY=your-super-secure-production-secret-key-change-this-456789

# 域名配置
DOMAIN=highperformance.152.199.108

# 邮件配置 (阿里云邮件推送服务)
SMTP_SERVER=smtp.aliyun.com
SMTP_PORT=465
SMTP_USER=your-email@example.com
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
ALLOWED_ORIGINS=https://highperformance.152.199.108,https://www.highperformance.152.199.108
SECURE_COOKIES=true
CORS_CREDENTIALS=false
"""
    
    env_path = project_root / ".env.aliyun"
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"环境变量文件已创建: {env_path}")
    
    # 3. 创建Nginx配置
    nginx_config = """server {
    listen 80;
    server_name highperformance.152.199.108 www.highperformance.152.199.108;
    
    # 重定向到HTTPS (如果配置了SSL)
    # return 301 https://$server_name$request_uri;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    add_header X-Forwarded-For $proxy_add_x_forwarded_for;
    add_header X-Forwarded-Proto $scheme;
    
    # 日志
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # 限制请求大小
    client_max_body_size 10M;
    
    # 后端API代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # WebSocket支持
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
    
    # 安全配置
    location ~ /\. {
        deny all;
    }
    
    location /admin {
        auth_basic "Restricted Area";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}

# HTTPS配置 (可选)
# server {
#     listen 443 ssl http2;
#     server_name highperformance.152.199.108 www.highperformance.152.199.108;
#     
#     ssl_certificate /etc/nginx/ssl/cert.pem;
#     ssl_certificate_key /etc/nginx/ssl/key.pem;
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256-DHE-RSA-AES128-GCM-SHA256;
#     ssl_prefer_server_ciphers off;
#     
#     # ... 其他HTTPS配置与上面相同
# }
"""
    
    nginx_config_path = nginx_dir / "nginx.conf"
    with open(nginx_config_path, 'w', encoding='utf-8') as f:
        f.write(nginx_config)
    
    print(f"Nginx配置已创建: {nginx_config_path}")
    
    print("")
    print("=== 部署配置已创建完成 ===")
    print("创建的文件:")
    print(f"1. docker-compose-aliyun.yml - Docker服务配置")
    print(f"2. .env.aliyun - 环境变量配置")
    print(f"3. nginx/nginx.conf - Nginx代理配置")
    print("")
    print("下一步手动操作:")
    print("1. 将配置文件上传到阿里云服务器")
    print("2. 配置服务器环境")
    print("3. 启动服务并验证")
    print("4. 配置域名解析")
    
    return True

if __name__ == "__main__":
    main()