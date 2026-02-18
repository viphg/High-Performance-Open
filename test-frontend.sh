#!/bin/bash

# 创建临时静态服务器容器
docker run -d \
  --name hp-frontend-simple \
  -p 5176:80 \
  -v "D:/OPENPROJECT/High-Performance-Open/frontend:/usr/share/nginx/html:ro" \
  nginx:alpine \
  sh -c "cd /usr/share/nginx/html && npm run build && cp -r dist/* /usr/share/nginx/html/ && nginx -g 'daemon off;'"