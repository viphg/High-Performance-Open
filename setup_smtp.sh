#!/bin/bash
# 阿里云邮件推送快速配置脚本

echo "====================================="
echo "阿里云邮件推送配置向导"
echo "====================================="
echo ""
echo "请按提示输入你的阿里云邮件推送配置信息"
echo ""

# 提示用户输入
read -p "请输入SMTP服务器地址 [默认: smtpdm.aliyun.com]: " SMTP_SERVER
SMTP_SERVER=${SMTP_SERVER:-smtpdm.aliyun.com}

read -p "请输入SMTP端口 [默认: 465]: " SMTP_PORT
SMTP_PORT=${SMTP_PORT:-465}

read -p "请输入SMTP用户名 (完整的邮箱地址): " SMTP_USER

read -s -p "请输入SMTP密码: " SMTP_PASSWORD
echo ""

read -p "请输入发件人邮箱地址 [$SMTP_USER]: " FROM_EMAIL
FROM_EMAIL=${FROM_EMAIL:-$SMTP_USER}

# 创建备份
cp backend/.env backend/.env.backup.$(date +%Y%m%d_%H%M%S)

# 更新配置文件
cat > /tmp/smtp_config.txt << EOF

# 阿里云邮件推送配置
SMTP_SERVER=$SMTP_SERVER
SMTP_PORT=$SMTP_PORT
SMTP_USER=$SMTP_USER
SMTP_PASSWORD=$SMTP_PASSWORD
FROM_EMAIL=$FROM_EMAIL
EOF

# 替换原有的邮件配置
sed -i '/# Email Configuration/,/FROM_EMAIL=.*/d' backend/.env
cat /tmp/smtp_config.txt >> backend/.env

echo ""
echo "====================================="
echo "配置已更新！"
echo "====================================="
echo ""
echo "配置信息："
echo "SMTP服务器: $SMTP_SERVER"
echo "SMTP端口: $SMTP_PORT"
echo "SMTP用户: $SMTP_USER"
echo "发件人: $FROM_EMAIL"
echo ""
echo "下一步操作："
echo "1. 重启后端服务: docker restart hp-backend-open"
echo "2. 测试邮件发送"
echo "3. 查看日志: docker logs hp-backend-open --tail 50"
echo ""
echo "如需恢复配置，请运行："
echo "cp backend/.env.backup.* backend/.env"
