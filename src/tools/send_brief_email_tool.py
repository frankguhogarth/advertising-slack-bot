"""
邮件发送工具
用于将生成的brief以md文件附件形式发送到指定邮箱
"""

import json
import smtplib
import ssl
import time
import os
import base64
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
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
    将生成的brief以md文件附件形式发送到指定邮箱
    
    Args:
        brief_content: brief的文本内容
        to_email: 收件人邮箱地址
        client_name: 客户名称（可选），用于邮件主题和文件名
        
    Returns:
        发送结果描述
    """
    try:
        # 检查邮件服务是否可用
        if not IDENTITY_AVAILABLE:
            return "❌ 邮件服务未配置，无法发送邮件。请联系管理员配置email集成。"
        
        # 获取邮件配置
        config = get_email_config()
        
        # 生成文件名（符合命名规范）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client_prefix = client_name.replace(" ", "_").replace("/", "_") if client_name else "brief"
        client_prefix = "".join(c for c in client_prefix if c.isalnum() or c in "_-")
        filename = f"brief_{client_prefix}_{timestamp}.md"
        
        # 将brief内容保存到临时文件
        temp_file_path = f"/tmp/{filename}"
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.write(brief_content)
        
        # 构建HTML格式邮件正文
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4a90e2; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin-top: 20px; }}
                .footer {{ text-align: center; color: #666; margin-top: 20px; font-size: 12px; }}
                .highlight {{ background-color: #e3f2fd; padding: 10px; border-left: 4px solid #4a90e2; margin: 15px 0; }}
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
                    <p>您的客户Brief已经整理完成，详细内容请查看附件中的 <strong>{filename}</strong> 文件。</p>
                    <div class="highlight">
                        <p><strong>附件说明：</strong></p>
                        <ul>
                            <li>文件格式：Markdown (.md)</li>
                            <li>客户名称：{client_name if client_name else '未指定'}</li>
                            <li>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                        </ul>
                    </div>
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
        
        # 创建multipart邮件对象
        msg = MIMEMultipart()
        msg["From"] = formataddr(("广告项目经理Agent", config["account"]))
        msg["To"] = to_email
        msg["Subject"] = Header(subject, "utf-8")
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid()
        
        # 添加HTML正文
        msg.attach(MIMEText(html_content, "html", "utf-8"))
        
        # 添加md文件附件
        with open(temp_file_path, 'rb') as f:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            
            # 设置附件文件名（包含文件名编码）
            encoded_filename = Header(filename, 'utf-8').encode()
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename="{encoded_filename}"'
            )
            msg.attach(attachment)
        
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
                
                # 清理临时文件
                try:
                    os.remove(temp_file_path)
                except:
                    pass
                
                return f"✅ Brief已成功发送到邮箱：{to_email}（附件：{filename}）"
                
            except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError,
                    smtplib.SMTPDataError, smtplib.SMTPHeloError, ssl.SSLError, OSError) as e:
                last_err = e
                time.sleep(1 * (i + 1))
        
        # 清理临时文件（发送失败时）
        try:
            os.remove(temp_file_path)
        except:
            pass
        
        if last_err:
            return f"❌ 发送邮件失败：{str(last_err)}"
        
        return "❌ 发送邮件失败：未知错误"
        
    except Exception as e:
        # 清理临时文件（发生异常时）
        try:
            if 'temp_file_path' in locals():
                os.remove(temp_file_path)
        except:
            pass
        return f"❌ 发送邮件时发生错误：{str(e)}"
