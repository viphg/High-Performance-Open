import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from string import Template
from typing import Dict, Optional
from app.config import settings
from app.models import User

logger = logging.getLogger(__name__)


class EmailService:
    """邮件服务"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = "High-Performance 个人成长平台"
        
    def _create_smtp_connection(self):
        """创建SMTP连接"""
        try:
            if self.smtp_port == 465:
                # SSL连接
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                # STARTTLS连接
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            
            server.login(self.smtp_user, self.smtp_password)
            return server
        except Exception as e:
            logger.error(f"SMTP连接失败: {str(e)}")
            raise
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """发送邮件"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = formataddr((self.from_name, self.from_email))
            msg['To'] = to_email
            
            # 添加纯文本版本
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(part1)
            
            # 添加HTML版本
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part2)
            
            # 发送邮件
            with self._create_smtp_connection() as server:
                server.sendmail(
                    self.from_email,
                    to_email,
                    msg.as_string()
                )
            
            logger.info(f"邮件已发送至: {to_email}, 主题: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            return False
    
    def send_notification_email(
        self,
        user: User,
        subject: str,
        html_template: str,
        template_data: Dict,
        text_template: Optional[str] = None
    ) -> bool:
        """发送通知邮件"""
        try:
            # 使用模板渲染内容
            html_content = Template(html_template).safe_substitute(**template_data)
            
            text_content = None
            if text_template:
                text_content = Template(text_template).safe_substitute(**template_data)
            
            return self.send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
        except Exception as e:
            logger.error(f"渲染邮件模板失败: {str(e)}")
            return False
    
    def send_welcome_email(self, user: User) -> bool:
        """发送欢迎邮件"""
        subject = "👋 欢迎加入 High-Performance！"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .feature {{ margin: 15px 0; padding: 15px; background: white; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 欢迎来到 High-Performance！</h1>
                </div>
                <div class="content">
                    <p>亲爱的 <strong>{user.username}</strong>，</p>
                    <p>感谢您加入我们的个人成长管理平台！我们很高兴能帮助您实现目标。</p>
                    
                    <div class="feature">
                        <h3>🎯 设定目标</h3>
                        <p>将您的梦想分解为清晰可执行的目标</p>
                    </div>
                    
                    <div class="feature">
                        <h3>✅ 管理任务</h3>
                        <p>把目标拆解为每日可执行的任务</p>
                    </div>
                    
                    <div class="feature">
                        <h3>📊 追踪进度</h3>
                        <p>实时查看目标完成情况，保持动力</p>
                    </div>
                    
                    <div class="feature">
                        <h3>🏆 获得成就</h3>
                        <p>完成目标解锁成就，获得持续动力</p>
                    </div>
                    
                    <center>
                        <a href="http://localhost:5176/dashboard" class="button">开始您的旅程</a>
                    </center>
                    
                    <p style="margin-top: 30px; font-size: 12px; color: #666;">
                        如果您有任何问题，请随时联系我们。<br>
                        祝您使用愉快！
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )
    
    def send_daily_digest(self, user: User, digest_data: Dict) -> bool:
        """发送每日摘要邮件"""
        subject = f"📊 您的每日摘要 - {digest_data.get('date', '')}"
        
        tasks_html = ""
        for task in digest_data.get('pending_tasks', []):
            tasks_html += f"<li>{task['title']} - 截止: {task.get('due_date', '无')}</li>"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #667eea; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .stat-box {{ display: inline-block; margin: 10px; padding: 15px; background: white; border-radius: 8px; text-align: center; min-width: 120px; }}
                .stat-number {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .task-list {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 今日任务摘要</h1>
                    <p>{digest_data.get('date', '')}</p>
                </div>
                <div class="content">
                    <div style="text-align: center;">
                        <div class="stat-box">
                            <div class="stat-number">{digest_data.get('pending_count', 0)}</div>
                            <div>待办任务</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number">{digest_data.get('due_today_count', 0)}</div>
                            <div>今日截止</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number">{digest_data.get('overdue_count', 0)}</div>
                            <div>已逾期</div>
                        </div>
                    </div>
                    
                    {f'''<div class="task-list">
                        <h3>⚠️ 今日截止任务</h3>
                        <ul>{tasks_html}</ul>
                    </div>''' if tasks_html else ''}
                    
                    <center>
                        <a href="http://localhost:5176/tasks" class="button">查看所有任务</a>
                    </center>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )


# 全局邮件服务实例
email_service = EmailService()
