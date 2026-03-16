"""
邮件发送工具
用于将生成的brief发送到用户指定的邮箱
"""

import json
import smtplib
import ssl
import time
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr, formatdate, make_msgid
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context

try:
    from coze_workload_identity import Client
    from cozeloop.decorator import observe
    IDENTITY_AVAILABLE = True
except ImportError:
    IDENTITY_AVAILABLE = False


def get_email_config():
    """获取邮件配置信息"""
    if not IDENTITY_AVAILABLE:
        raise Exception("邮件服务未配置，请先配置email集成")
    
    client = Client()
    email_credential = client.get_integration_credential("integration-email-imap-smtp")
    return json.loads(email_credential)


@tool
def send_brief_to_email(brief_content: str, to_email: str, client_name: str = None, runtime: ToolRuntime = None) -> str:
    """
    将生成的brief发送到指定邮箱
    
    Args:
        brief_content: brief的文本内容
        to_email: 收件人邮箱地址
        client_name: 客户名称（可选），用于邮件主题
        
    Returns:
        发送结果描述
    """
    try:
        # 检查邮件服务是否可用
        if not IDENTITY_AVAILABLE:
            return "❌ 邮件服务未配置，无法发送邮件。请联系管理员配置email集成。"
        
        # 获取邮件配置
        config = get_email_config()
        
        # 构建HTML格式邮件内容
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4a90e2; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin-top: 20px; }}
                .footer {{ text-align: center; color: #666; margin-top: 20px; font-size: 12px; }}
                pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                .client-name {{ color: #4a90e2; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📋 客户Brief已生成</h2>
                </div>
                <div class="content">
                    <p>您好，</p>
                    <p>您的客户Brief已经整理完成，以下是详细内容：</p>
                    <pre>{brief_content}</pre>
                    <p>如有任何问题或需要修改，请直接回复或联系项目经理。</p>
                </div>
                <div class="footer">
                    <p>此邮件由广告项目经理Agent自动发送</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 构建邮件主题
        client_prefix = f"[{client_name}] " if client_name else ""
        subject = f"{client_prefix}客户Brief已生成"
        
        # 创建邮件对象
        msg = MIMEText(html_content, "html", "utf-8")
        msg["From"] = formataddr(("广告项目经理Agent", config["account"]))
        msg["To"] = to_email
        msg["Subject"] = Header(subject, "utf-8")
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid()
        
        # 发送邮件
        ctx = ssl.create_default_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        
        attempts = 3
        last_err = None
        
        for i in range(attempts):
            try:
                with smtplib.SMTP_SSL(
                    config["smtp_server"],
                    config["smtp_port"],
                    context=ctx,
                    timeout=30
                ) as server:
                    server.ehlo()
                    server.login(config["account"], config["auth_code"])
                    server.sendmail(config["account"], [to_email], msg.as_string())
                    server.quit()
                
                return f"✅ Brief已成功发送到邮箱：{to_email}"
                
            except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError,
                    smtplib.SMTPDataError, smtplib.SMTPHeloError, ssl.SSLError, OSError) as e:
                last_err = e
                time.sleep(1 * (i + 1))
        
        if last_err:
            return f"❌ 发送邮件失败：{str(last_err)}"
        
        return "❌ 发送邮件失败：未知错误"
        
    except Exception as e:
        return f"❌ 发送邮件时发生错误：{str(e)}"
