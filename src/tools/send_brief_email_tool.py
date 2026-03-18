"""
邮件发送工具
用于将生成的brief以PDF文件附件形式发送到指定邮箱
"""

import json
import smtplib
import ssl
import time
import os
import re
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from email.utils import formataddr, formatdate, make_msgid
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context
from coze_coding_dev_sdk import DocumentGenerationClient, PDFConfig, DOCXConfig

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


def extract_images_from_brief(brief_content: str) -> list:
    """从brief内容中提取图片URL
    
    Args:
        brief_content: brief的文本内容
        
    Returns:
        图片信息列表，格式：[{"index": 1, "url": "https://...", "filename": "image_1.jpg"}]
    """
    images = []
    # 匹配格式：[图片X: URL]
    pattern = r'\[图片(\d+):\s*(https?://[^\]]+)\]'
    matches = re.findall(pattern, brief_content)
    
    for index, url in matches:
        # 确定文件扩展名
        ext = ".jpg"
        if ".png" in url.lower():
            ext = ".png"
        elif ".gif" in url.lower():
            ext = ".gif"
        elif ".webp" in url.lower():
            ext = ".webp"
        
        filename = f"image_{index}{ext}"
        images.append({
            "index": int(index),
            "url": url,
            "filename": filename
        })
    
    return images


def download_image(url: str, save_path: str) -> bool:
    """下载图片文件
    
    Args:
        url: 图片URL
        save_path: 保存路径
        
    Returns:
        下载是否成功
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"下载图片失败 {url}: {str(e)}")
        return False


def markdown_to_html(brief_content: str) -> str:
    """将Markdown内容转换为HTML，以保持正确的格式
    
    Args:
        brief_content: Markdown格式的内容
        
    Returns:
        HTML格式的内容
    """
    html_lines = []
    html_lines.append('<!DOCTYPE html>')
    html_lines.append('<html lang="zh-CN">')
    html_lines.append('<head>')
    html_lines.append('<meta charset="UTF-8">')
    html_lines.append('<style>')
    html_lines.append('body {')
    html_lines.append('  font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif;')
    html_lines.append('  font-size: 12px;')
    html_lines.append('  line-height: 1.8;')
    html_lines.append('  color: #333;')
    html_lines.append('  margin: 40px;')
    html_lines.append('}')
    html_lines.append('h1 {')
    html_lines.append('  font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif;')
    html_lines.append('  font-size: 18px;')
    html_lines.append('  font-weight: bold;')
    html_lines.append('  color: #000;')
    html_lines.append('  margin-top: 20px;')
    html_lines.append('  margin-bottom: 10px;')
    html_lines.append('  border-bottom: 2px solid #000;')
    html_lines.append('  padding-bottom: 5px;')
    html_lines.append('}')
    html_lines.append('ul, ol {')
    html_lines.append('  margin: 5px 0;')
    html_lines.append('  padding-left: 20px;')
    html_lines.append('}')
    html_lines.append('li {')
    html_lines.append('  margin: 5px 0;')
    html_lines.append('  line-height: 1.8;')
    html_lines.append('}')
    html_lines.append('p {')
    html_lines.append('  margin: 10px 0;')
    html_lines.append('  line-height: 1.8;')
    html_lines.append('  text-align: justify;')
    html_lines.append('}')
    html_lines.append('.nested-list {')
    html_lines.append('  margin-left: 20px;')
    html_lines.append('}')
    html_lines.append('</style>')
    html_lines.append('</head>')
    html_lines.append('<body>')
    
    # 解析Markdown内容
    lines = brief_content.split('\n')
    current_title = None
    in_ol = False
    in_nested_ol = False
    
    for i, line in enumerate(lines):
        # 处理标题（######）
        if line.startswith('######'):
            # 关闭之前的列表
            if in_nested_ol:
                html_lines.append('</ol>')
                in_nested_ol = False
            if in_ol:
                html_lines.append('</ol>')
                in_ol = False
            
            text = line[6:].strip()
            html_lines.append(f'<h1>{text}</h1>')
        # 处理缩进的列表项（\t1. 或 \t-）
        elif line.startswith('\t'):
            text = line.lstrip('\t').strip()
            if text.startswith('-'):
                if not in_nested_ol:
                    html_lines.append('<ul class="nested-list">')
                    in_nested_ol = True
                text = text[1:].strip()
                html_lines.append(f'<li>{text}</li>')
            elif text and text[0].isdigit() and ('. ' in text or '.\t' in text):
                if not in_nested_ol:
                    html_lines.append('<ol class="nested-list">')
                    in_nested_ol = True
                # 提取数字后的文本
                if '. ' in text:
                    text = text.split('. ', 1)[1] if '. ' in text else text
                elif '.\t' in text:
                    text = text.split('.\t', 1)[1] if '.\t' in text else text
                html_lines.append(f'<li>{text}</li>')
            else:
                # 缩进的普通文本
                if in_nested_ol:
                    html_lines.append('</ol>')
                    in_nested_ol = False
                if in_ol:
                    html_lines.append('</ol>')
                    in_ol = False
                html_lines.append(f'<p style="margin-left: 20px;">{text}</p>')
        # 处理列表项（- 或 数字.）
        elif line.strip().startswith('-'):
            # 关闭嵌套列表
            if in_nested_ol:
                html_lines.append('</ol>')
                in_nested_ol = False
            if not in_ol:
                html_lines.append('<ul>')
                in_ol = True
            text = line.lstrip('-').strip()
            html_lines.append(f'<li>{text}</li>')
        elif line.strip() and line.strip()[0].isdigit() and ('. ' in line.strip() or '.\t' in line.strip()):
            # 关闭嵌套列表
            if in_nested_ol:
                html_lines.append('</ol>')
                in_nested_ol = False
            if not in_ol:
                html_lines.append('<ol>')
                in_ol = True
            text = line.strip()
            # 提取数字后的文本
            if '. ' in text:
                text = text.split('. ', 1)[1] if '. ' in text else text
            elif '.\t' in text:
                text = text.split('.\t', 1)[1] if '.\t' in text else text
            html_lines.append(f'<li>{text}</li>')
        # 处理空行
        elif not line.strip():
            if in_nested_ol:
                html_lines.append('</ol>')
                in_nested_ol = False
            if in_ol:
                html_lines.append('</ol>')
                in_ol = False
        # 处理普通文本
        elif line.strip():
            if in_nested_ol:
                html_lines.append('</ol>')
                in_nested_ol = False
            if in_ol:
                html_lines.append('</ol>')
                in_ol = False
            text = line.strip()
            html_lines.append(f'<p>{text}</p>')
    
    # 关闭未关闭的列表
    if in_nested_ol:
        html_lines.append('</ol>')
    if in_ol:
        html_lines.append('</ol>')
    
    html_lines.append('</body>')
    html_lines.append('</html>')
    
    return '\n'.join(html_lines)


@tool
def send_brief_to_email(brief_content: str, to_email: str, client_name: str = None, runtime: ToolRuntime = None) -> str:
    """
    将生成的brief以Word文档（DOCX）文件附件形式发送到指定邮箱
    
    Args:
        brief_content: brief的文本内容（Markdown格式）
        to_email: 收件人邮箱地址
        client_name: 客户名称（可选），用于邮件主题和文件名
        
    Returns:
        发送结果描述
    """
    ctx = runtime.context if runtime else new_context(method="send_brief_to_email")
    
    pdf_url = None
    temp_file_path = None
    temp_files_to_cleanup = []
    
    try:
        # 检查邮件服务是否可用
        if not IDENTITY_AVAILABLE:
            return "❌ 邮件服务未配置，无法发送邮件。请联系管理员配置email集成。"
        
        # 获取邮件配置
        config = get_email_config()
        
        # 提取brief中的图片
        images = extract_images_from_brief(brief_content)
        
        # 从brief内容中移除图片链接，改为占位符
        clean_brief = brief_content
        for image in images:
            # 将 [图片X: URL] 替换为 [图片X - 请查看邮件附件]
            old_pattern = f'[图片{image["index"]}:[^\\]]+]'
            clean_brief = re.sub(old_pattern, f'[图片{image["index"]} - 请查看邮件附件]', clean_brief)
        
        # 生成PDF文件
        # title参数必须是英文，使用client_name的拼音或拼音首字母
        client_prefix = client_name.replace(" ", "_").replace("/", "_") if client_name else "brief"
        # 移除非字母数字和下划线、短横线的字符
        client_prefix = "".join(c for c in client_prefix if c.isalnum() or c in "_-")
        # 使用英文名作为PDF文件名
        pdf_title = f"brief_{client_prefix}"
        
        try:
            # 配置DOCX生成参数（支持中文）
            docx_config = DOCXConfig(
                font_name="Microsoft YaHei",  # 使用微软雅黑字体
                font_size=12,
                top_margin=1.0,
                bottom_margin=1.0,
                left_margin=1.0,
                right_margin=1.0
            )
            docx_client = DocumentGenerationClient(docx_config=docx_config)
            
            # 将Markdown转换为HTML，以保持正确的格式
            html_content = markdown_to_html(clean_brief)
            
            # 使用HTML内容生成DOCX
            docx_url = docx_client.create_docx_from_html(html_content, pdf_title)
            
        except Exception as e:
            return f"❌ 生成文档失败：{str(e)}"
        
        # 从S3下载DOCX文件到本地
        try:
            # 生成临时文件名（使用.docx格式）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"brief_{client_prefix}_{timestamp}.docx"
            temp_file_path = f"/tmp/{filename}"
            temp_files_to_cleanup.append(temp_file_path)
            
            # 下载DOCX文件
            response = requests.get(docx_url, timeout=30)
            response.raise_for_status()
            
            with open(temp_file_path, 'wb') as f:
                f.write(response.content)
                
        except Exception as e:
            return f"❌ 下载文档失败：{str(e)}"
        
        # 下载图片文件
        downloaded_images = []
        for image in images:
            image_path = f"/tmp/{image['filename']}"
            if download_image(image["url"], image_path):
                downloaded_images.append({
                    "path": image_path,
                    "filename": image["filename"]
                })
                temp_files_to_cleanup.append(image_path)
        
        # 构建HTML格式邮件正文
        attachment_list_html = "<ul>"
        attachment_list_html += f"<li>文件格式：Word文档（{filename}）</li>"
        if downloaded_images:
            attachment_list_html += "<li>参考图片："
            attachment_list_html += "<ul>"
            for img in downloaded_images:
                attachment_list_html += f"<li>{img['filename']}</li>"
            attachment_list_html += "</ul></li>"
        attachment_list_html += "</ul>"
        
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
                    <p>您的客户Brief已经整理完成，详细内容请查看附件。</p>
                    <div class="highlight">
                        <p><strong>附件说明：</strong></p>
                        {attachment_list_html}
                        <li>客户名称：<span class="client-name">{client_name if client_name else '未指定'}</span></li>
                        <li>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                        </ul>
                    </div>
                    <p>Word文档可以在Microsoft Word、WPS等软件中打开，支持中文和英文完美显示。</p>
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
        
        # 添加DOCX文件附件
        with open(temp_file_path, 'rb') as f:
            attachment = MIMEBase('application', 'vnd.openxmlformats-officedocument.wordprocessingml.document')
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            
            # 设置附件文件名（包含文件名编码）
            encoded_filename = Header(filename, 'utf-8').encode()
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename="{encoded_filename}"'
            )
            msg.attach(attachment)
        
        # 添加图片附件
        for img in downloaded_images:
            with open(img["path"], 'rb') as f:
                # 根据文件扩展名确定MIME类型
                mime_type = 'image/jpeg'
                if img["filename"].endswith('.png'):
                    mime_type = 'image/png'
                elif img["filename"].endswith('.gif'):
                    mime_type = 'image/gif'
                elif img["filename"].endswith('.webp'):
                    mime_type = 'image/webp'
                
                img_attachment = MIMEBase('image', img["filename"].split('.')[-1])
                img_attachment.set_payload(f.read())
                encoders.encode_base64(img_attachment)
                
                # 设置附件文件名
                encoded_img_filename = Header(img["filename"], 'utf-8').encode()
                img_attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{encoded_img_filename}"'
                )
                msg.attach(img_attachment)
        
        # 发送邮件
        ctx_ssl = ssl.create_default_context()
        ctx_ssl.minimum_version = ssl.TLSVersion.TLSv1_2
        
        attempts = 3
        last_err = None
        
        for i in range(attempts):
            try:
                with smtplib.SMTP_SSL(
                    config["smtp_server"],
                    config["smtp_port"],
                    context=ctx_ssl,
                    timeout=30
                ) as server:
                    server.ehlo()
                    server.login(config["account"], config["auth_code"])
                    server.sendmail(config["account"], [to_email], msg.as_string())
                    server.quit()
                
                # 清理所有临时文件
                for file_path in temp_files_to_cleanup:
                    try:
                        os.remove(file_path)
                    except:
                        pass
                
                image_info = ""
                if downloaded_images:
                    image_info = f"，图片附件：{len(downloaded_images)}个"
                
                return f"✅ Brief已成功发送到邮箱：{to_email}（附件：{filename}{image_info}）"
                
            except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError,
                    smtplib.SMTPDataError, smtplib.SMTPHeloError, ssl.SSLError, OSError) as e:
                last_err = e
                time.sleep(1 * (i + 1))
        
        # 清理所有临时文件（发送失败时）
        for file_path in temp_files_to_cleanup:
            try:
                os.remove(file_path)
            except:
                pass
        
        if last_err:
            return f"❌ 发送邮件失败：{str(last_err)}"
        
        return "❌ 发送邮件失败：未知错误"
        
    except Exception as e:
        # 清理所有临时文件（发生异常时）
        for file_path in temp_files_to_cleanup:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
        return f"❌ 发送邮件时发生错误：{str(e)}"
