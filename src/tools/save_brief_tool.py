"""
Brief保存工具
用于将生成的brief保存为文件并上传到对象存储，提供下载链接
"""

from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk.s3 import S3SyncStorage
from coze_coding_utils.runtime_ctx.context import new_context
import os
import time
from datetime import datetime


@tool
def save_brief_to_file(brief_content: str, client_name: str = None, runtime: ToolRuntime = None) -> str:
    """
    将生成的brief保存为文件并上传到对象存储，返回下载链接
    
    Args:
        brief_content: brief的文本内容
        client_name: 客户名称（可选），用于生成文件名
        
    Returns:
        下载链接URL
    """
    try:
        # 初始化对象存储客户端
        storage = S3SyncStorage(
            endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
            access_key="",
            secret_key="",
            bucket_name=os.getenv("COZE_BUCKET_NAME"),
            region="cn-beijing",
        )
        
        # 生成文件名（符合命名规范：只允许字母、数字、点、下划线、短横）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client_prefix = client_name.replace(" ", "_").replace("/", "_") if client_name else "brief"
        file_name = f"brief_{client_prefix}_{timestamp}.md"
        
        # 上传文件到对象存储
        file_key = storage.upload_file(
            file_content=brief_content.encode('utf-8'),
            file_name=file_name,
            content_type="text/markdown",
        )
        
        # 生成签名URL（有效期24小时）
        download_url = storage.generate_presigned_url(
            key=file_key,
            expire_time=86400,  # 24小时
        )
        
        return download_url
        
    except Exception as e:
        return f"保存brief失败：{str(e)}"
