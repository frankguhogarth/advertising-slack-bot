"""
Brief内容获取工具
用于从各种格式的文档URL中提取brief内容
"""

from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk.fetch import FetchClient
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def fetch_brief_content(url: str, runtime: ToolRuntime = None) -> str:
    """
    从文档URL获取brief内容
    
    支持的格式：
    - PDF文档
    - Office文档（doc/docx/ppt/pptx/xls/xlsx/csv）
    - 纯文本文件（txt/text）
    - 电子书（epub/mobi）
    - XML文档
    - 网页HTML
    
    Args:
        url: 文档的URL地址
        
    Returns:
        提取的文本内容
    """
    try:
        # 获取上下文（用于请求追踪）
        ctx = runtime.context if runtime else new_context(method="fetch_brief_content")
        
        # 初始化FetchClient
        client = FetchClient(ctx=ctx)
        
        # 获取文档内容
        response = client.fetch(url=url)
        
        # 检查是否成功
        if response.status_code != 0:
            return f"获取文档失败：{response.status_message}"
        
        # 提取所有文本内容
        text_content = "\n".join(
            item.text for item in response.content if item.type == "text"
        )
        
        if not text_content.strip():
            return f"警告：文档中未找到文本内容，URL: {url}"
        
        return text_content
        
    except Exception as e:
        return f"获取brief内容时发生错误：{str(e)}"
