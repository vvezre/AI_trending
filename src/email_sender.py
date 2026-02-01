"""
邮件推送模块
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import Optional
import os


class EmailSender:
    """邮件发送器"""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str
    ):
        """
        初始化邮件发送器

        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP端口
            sender_email: 发件人邮箱
            sender_password: 发件人密码（或应用专用密码）
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_text_email(
        self,
        receiver_email: str,
        subject: str,
        content: str
    ) -> bool:
        """
        发送纯文本邮件

        Args:
            receiver_email: 收件人邮箱
            subject: 邮件主题
            content: 邮件内容

        Returns:
            是否发送成功
        """
        try:
            # 创建邮件对象
            message = MIMEText(content, 'plain', 'utf-8')
            message['From'] = self.sender_email
            message['To'] = receiver_email
            message['Subject'] = Header(subject, 'utf-8')

            # 连接SMTP服务器并发送
            print(f"正在连接SMTP服务器: {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # 启用TLS加密
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, receiver_email, message.as_string())

            print(f"[OK] 邮件发送成功: {receiver_email}")
            return True

        except smtplib.SMTPException as e:
            print(f"[ERROR] SMTP错误: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] 邮件发送失败: {e}")
            return False

    def send_html_email(
        self,
        receiver_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        发送HTML邮件

        Args:
            receiver_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML格式内容
            text_content: 纯文本内容（可选，作为HTML的备用）

        Returns:
            是否发送成功
        """
        try:
            # 创建多部分邮件
            message = MIMEMultipart('alternative')
            message['From'] = Header(f"GitHub Trending 助手 <{self.sender_email}>", 'utf-8')
            message['To'] = Header(receiver_email, 'utf-8')
            message['Subject'] = Header(subject, 'utf-8')

            # 添加纯文本部分（备用）
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                message.attach(part1)

            # 添加HTML部分
            part2 = MIMEText(html_content, 'html', 'utf-8')
            message.attach(part2)

            # 连接SMTP服务器并发送
            print(f"正在连接SMTP服务器: {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, receiver_email, message.as_string())

            print(f"[OK] HTML邮件发送成功: {receiver_email}")
            return True

        except smtplib.SMTPException as e:
            print(f"[ERROR] SMTP错误: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] 邮件发送失败: {e}")
            return False

    def send_trending_report(
        self,
        receiver_email: str,
        report_content: str,
        date: Optional[str] = None
    ) -> bool:
        """
        发送GitHub Trending分析报告

        Args:
            receiver_email: 收件人邮箱
            report_content: 报告内容（markdown格式）
            date: 日期（可选）

        Returns:
            是否发送成功
        """
        from datetime import datetime

        if date is None:
            date = datetime.now().strftime("%Y年%m月%d日")

        subject = f"GitHub Trending 今日观察 - {date}"

        # MVP阶段使用纯文本邮件
        # 后续可以将markdown转换为HTML格式
        return self.send_text_email(receiver_email, subject, report_content)


def markdown_to_simple_html(markdown_text: str) -> str:
    """
    将Markdown简单转换为HTML（基础版本）
    后续可以使用markdown库进行更完善的转换

    Args:
        markdown_text: Markdown文本

    Returns:
        HTML文本
    """
    import re

    html = markdown_text

    # 标题转换
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # 粗体和斜体
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)

    # 链接
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)

    # 列表
    html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # 段落
    html = html.replace('\n\n', '</p><p>')

    # 包装
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #24292e;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f6f8fa;
        }}
        h1, h2, h3 {{ color: #0366d6; }}
        a {{ color: #0366d6; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        li {{ margin: 5px 0; }}
        code {{ background-color: #f6f8fa; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    <p>{html}</p>
</body>
</html>
"""
    return html


def test_email_sender():
    """测试邮件发送功能"""
    # 从环境变量读取配置
    sender = EmailSender(
        smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        sender_email=os.getenv("EMAIL_SENDER", ""),
        sender_password=os.getenv("EMAIL_PASSWORD", "")
    )

    test_content = """
# GitHub Trending 今日观察

## 测试报告

这是一封测试邮件，用于验证邮件发送功能是否正常。

### 功能清单
- 数据抓取 [OK]
- AI分析 [OK]
- 邮件推送 [OK]

感谢使用 GitHub Trending AI 总结助手！
"""

    receiver = os.getenv("EMAIL_RECEIVER", "")

    if not sender.sender_email or not receiver:
        print("请设置环境变量: EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER")
        return

    success = sender.send_trending_report(receiver, test_content)

    if success:
        print("测试邮件发送成功！")
    else:
        print("测试邮件发送失败！")


if __name__ == "__main__":
    test_email_sender()
