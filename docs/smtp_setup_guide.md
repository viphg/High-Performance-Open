# SMTP邮件服务器配置指南

## 方案一：阿里云邮件推送（推荐用于生产环境）

### 步骤1：开通阿里云邮件推送服务
1. 登录阿里云控制台：https://www.aliyun.com
2. 搜索"邮件推送"或进入：产品 > 应用服务 > 邮件推送
3. 点击"立即开通"（按量付费，每月前200封免费）

### 步骤2：配置发信域名
1. 进入邮件推送控制台
2. 点击"发信域名" > "新建域名"
3. 输入你的域名（如：notice.yourdomain.com）
4. 按照提示添加DNS解析记录（TXT、MX记录）
5. 等待域名验证通过（通常几分钟到几小时）

### 步骤3：创建发信地址
1. 点击"发信地址" > "新建发信地址"
2. 选择刚刚验证的域名
3. 设置账号（如：noreply）
4. 设置发信地址：noreply@notice.yourdomain.com
5. 点击"验证回信地址"

### 步骤4：获取SMTP凭证
1. 点击"发信地址"列表中的地址
2. 点击"设置SMTP密码"
3. 设置并保存密码（只会显示一次，务必保存）

### 步骤5：配置信息
```
SMTP服务器：smtpdm.aliyun.com
SMTP端口：465（SSL）或 25（STARTTLS）
SMTP用户名：完整的邮箱地址，如 noreply@notice.yourdomain.com
SMTP密码：你在上一步设置的密码
发件人邮箱：noreply@notice.yourdomain.com
```

---

## 方案二：QQ邮箱（适合个人测试）

### 步骤1：开启SMTP服务
1. 登录QQ邮箱网页版
2. 点击"设置" > "账户"
3. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启"SMTP服务"
5. 验证手机号，获取授权码（16位字符）

### 配置信息
```
SMTP服务器：smtp.qq.com
SMTP端口：465（SSL）或 587（STARTTLS）
SMTP用户名：你的QQ邮箱地址，如 123456@qq.com
SMTP密码：授权码（不是QQ密码）
发件人邮箱：123456@qq.com
```

---

## 方案三：163邮箱（适合个人测试）

### 步骤1：开启SMTP服务
1. 登录163邮箱
2. 点击"设置" > "POP3/SMTP/IMAP"
3. 开启"SMTP服务"
4. 验证手机号，获取授权码

### 配置信息
```
SMTP服务器：smtp.163.com
SMTP端口：465（SSL）
SMTP用户名：你的163邮箱地址
SMTP密码：授权码
发件人邮箱：你的163邮箱地址
```

---

## 方案四：Gmail（适合海外用户）

### 步骤1：开启两步验证
1. 登录Google账户
2. 进入"安全性" > "两步验证"
3. 开启两步验证

### 步骤2：创建应用专用密码
1. 进入"安全性" > "应用专用密码"
2. 选择应用：邮件
3. 选择设备：其他（自定义名称）
4. 生成16位密码

### 配置信息
```
SMTP服务器：smtp.gmail.com
SMTP端口：465（SSL）或 587（STARTTLS）
SMTP用户名：你的Gmail地址
SMTP密码：应用专用密码
发件人邮箱：你的Gmail地址
```

---

## 方案五：SendGrid（国际服务，免费额度高）

### 步骤1：注册SendGrid账号
1. 访问：https://sendgrid.com
2. 注册免费账号（每天免费100封邮件）

### 步骤2：获取API Key
1. 登录后进入 Settings > API Keys
2. 点击"Create API Key"
3. 选择"Restricted Access"
4. 开启"Mail Send"权限
5. 复制生成的API Key

### 配置信息
```
SMTP服务器：smtp.sendgrid.net
SMTP端口：587
SMTP用户名：apikey
SMTP密码：你的API Key
发件人邮箱：你的发件邮箱（需在SendGrid验证）
```

---

## 配置方法

### 1. 修改环境变量文件

编辑 `backend/.env` 文件：

```bash
# 根据你选择的方案，修改以下配置

# 阿里云示例
SMTP_SERVER=smtpdm.aliyun.com
SMTP_PORT=465
SMTP_USER=noreply@notice.yourdomain.com
SMTP_PASSWORD=你的SMTP密码
FROM_EMAIL=noreply@notice.yourdomain.com

# QQ邮箱示例
# SMTP_SERVER=smtp.qq.com
# SMTP_PORT=465
# SMTP_USER=123456@qq.com
# SMTP_PASSWORD=你的授权码
# FROM_EMAIL=123456@qq.com
```

### 2. 重启后端服务

```bash
docker restart hp-backend-open
```

### 3. 测试邮件发送

#### 方法1：使用API测试
登录系统后，访问通知设置页面，修改设置后保存，会触发邮件发送。

#### 方法2：使用curl测试
```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username":"testuser",
    "email":"你的测试邮箱@example.com",
    "password":"password123"
  }'
```

#### 方法3：查看Docker日志
```bash
docker logs hp-backend-open --tail 50 | grep -i email
```

---

## 常见问题

### 1. 邮件发送失败
**可能原因：**
- SMTP密码错误（注意是授权码，不是邮箱密码）
- 端口被防火墙拦截
- 邮箱SMTP服务未开启
- 发件人地址和认证地址不一致

**解决方法：**
- 检查密码/授权码是否正确
- 尝试更换端口（465/587/25）
- 检查邮箱设置中SMTP是否开启
- 确保FROM_EMAIL和SMTP_USER一致

### 2. 邮件进入垃圾箱
**可能原因：**
- 发件域名没有SPF、DKIM记录
- 邮件内容被识别为垃圾邮件
- 发件域名信誉度低

**解决方法：**
- 配置SPF、DKIM、DMARC记录
- 优化邮件内容，避免敏感词
- 使用专业的邮件推送服务（如阿里云）

### 3. 发送频率限制
**常见限制：**
- QQ邮箱：每天最多200封
- 163邮箱：每天最多200封
- Gmail：每天最多100封
- 阿里云：根据套餐，免费版每天200封

**解决方法：**
- 使用专业的邮件推送服务
- 实现邮件队列，控制发送频率
- 购买商业邮件服务

---

## 生产环境建议

### 1. 使用阿里云邮件推送
- 国内发送速度快
- 到达率高
- 价格实惠（0.09元/1000封）
- 有详细的发送统计

### 2. 配置邮件模板
在 `backend/app/services/email_service.py` 中自定义邮件模板，加入：
- 公司Logo
- 品牌色彩
- 退订链接
- 联系方式

### 3. 监控邮件发送
- 配置日志记录
- 监控发送成功率
- 处理退信和投诉

### 4. 安全措施
- 不要在代码中硬编码密码
- 使用环境变量
- 定期更换授权码
- 启用IP白名单

---

## 快速配置命令

如果你使用阿里云，可以直接执行：

```bash
# 1. 备份原配置
cp backend/.env backend/.env.backup

# 2. 编辑配置（将以下信息替换为你的实际配置）
cat >> backend/.env << 'EOF'

# 阿里云邮件推送配置
SMTP_SERVER=smtpdm.aliyun.com
SMTP_PORT=465
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=your-smtp-password
FROM_EMAIL=noreply@yourdomain.com
EOF

# 3. 重启服务
docker restart hp-backend-open

# 4. 检查日志
docker logs hp-backend-open --tail 20
```

---

## 测试邮件发送

配置完成后，可以通过以下方式测试：

1. **注册新用户** - 会发送欢迎邮件
2. **修改通知设置** - 会发送测试邮件
3. **查看日志** - 确认邮件发送状态

测试成功标志：
- 后端日志显示 "邮件已发送至: xxx"
- 测试邮箱收到邮件
- 邮件内容格式正确

---

祝你配置顺利！如有问题随时询问。
