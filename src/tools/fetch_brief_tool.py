"""
Brief内容获取工具
用于从各种格式的文档URL中提取brief内容（包括文字和图片）
"""

from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk.fetch import FetchClient
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def fetch_brief_content(url: str, runtime: ToolRuntime = None) -> str:
    """
    从文档URL获取brief内容（包括文字和图片）
    
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
        提取的文本内容，图片会用[图片1: URL]格式标注
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
        
        # 提取文本和图片内容
        text_parts = []
        image_count = 0
        
        for item in response.content:
            if item.type == "text":
                # 添加文本内容
                text_parts.append(item.text)
            elif item.type == "image":
                # 添加图片信息
                image_count += 1
                image_url = item.image.display_url
                text_parts.append(f"[图片{image_count}: {image_url}]")
            elif item.type == "link":
                # 添加链接信息（可选）
                text_parts.append(f"[链接: {item.url}]")
        
        # 合并所有内容
        combined_content = "\n".join(text_parts)
        
        if not combined_content.strip():
            return f"警告：文档中未找到任何内容，URL: {url}"
        
        # 添加图片统计信息
        if image_count > 0:
            combined_content += f"\n\n[文档共包含 {image_count} 张图片]"
        
        return combined_content
        
    except Exception as e:
        return f"获取brief内容时发生错误：{str(e)}"
