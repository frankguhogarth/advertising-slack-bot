"""
Microsoft Teams消息通知工具
通过Incoming Webhook发送消息到Teams频道
"""

import requests
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context

# Teams Webhook URL（需要用户配置后填写）
TEAMS_WEBHOOK_URL = None


def set_teams_webhook_url(webhook_url: str):
    """设置Teams Webhook URL
    
    Args:
        webhook_url: Teams Incoming Webhook URL
    """
    global TEAMS_WEBHOOK_URL
    TEAMS_WEBHOOK_URL = webhook_url


def send_teams_message_raw(message: str, title: str = None, color: str = "0078D4") -> dict:
    """发送消息到Teams（内部函数，不被@tool装饰）
    
    Args:
        message: 消息内容（支持Markdown）
        title: 消息标题（可选）
        color: 消息卡片颜色（可选），默认蓝色0078D4
            - 0078D4: 蓝色（默认，信息）
            - 5CB85C: 绿色（成功）
            - D9534F: 红色（错误）
            - F0AD4E: 黄色（警告）
    
    Returns:
        发送结果字典
    """
    global TEAMS_WEBHOOK_URL
    
    if not TEAMS_WEBHOOK_URL:
        return {
            "success": False,
            "error": "Teams Webhook URL未配置，请先调用set_teams_webhook_url设置"
        }
    
    try:
        # 构建Teams消息卡片（Adaptive Card格式）
        webhook_data = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": "广告项目经理Agent通知",
            "themeColor": color,
            "title": title if title else "📋 广告项目经理Agent",
            "sections": [
                {
                    "text": message
                }
            ],
            "markdown": True
        }
        
        # 发送HTTP POST请求
        response = requests.post(
            TEAMS_WEBHOOK_URL,
            json=webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        response.raise_for_status()
        
        return {
            "success": True,
            "message": "消息已发送到Teams"
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"发送失败：{str(e)}"
        }


@tool
def send_teams_message(message: str, title: str = None, message_type: str = "info", runtime: ToolRuntime = None) -> str:
    """
    发送文本通知消息到Teams频道
    
    Args:
        message: 消息内容（支持Markdown格式）
        title: 消息标题（可选），默认使用"广告项目经理Agent通知"
        message_type: 消息类型，可选值：
            - "info": 信息通知（蓝色）
            - "success": 成功消息（绿色）
            - "error": 错误消息（红色）
            - "warning": 警告消息（黄色）
    
    Returns:
        发送结果描述
        
    Examples:
        send_teams_message("项目已创建成功", "项目通知", "success")
        send_teams_message("Brief已发送到邮箱", "邮件通知", "info")
    """
    ctx = runtime.context if runtime else new_context(method="send_teams_message")
    
    # 消息类型颜色映射
    color_map = {
        "info": "0078D4",      # 蓝色
        "success": "5CB85C",   # 绿色
        "error": "D9534F",     # 红色
        "warning": "F0AD4E"    # 黄色
    }
    
    color = color_map.get(message_type, "0078D4")
    
    # 调用内部发送函数
    result = send_teams_message_raw(message, title, color)
    
    if result["success"]:
        return f"✅ 消息已发送到Teams：{message[:50]}..."
    else:
        return f"❌ 发送失败：{result['error']}"


@tool
def send_teams_brief_notification(brief_summary: str, client_name: str = None, runtime: ToolRuntime = None) -> str:
    """
    发送Brief创建通知到Teams频道
    
    Args:
        brief_summary: Brief摘要内容
        client_name: 客户名称（可选）
    
    Returns:
        发送结果描述
    """
    ctx = runtime.context if runtime else new_context(method="send_teams_brief_notification")
    
    title = "📋 Brief已生成" if not client_name else f"📋 {client_name} Brief已生成"
    
    message = f"""
**Brief摘要：**

{brief_summary}

---
*此消息由广告项目经理Agent自动发送*
"""
    
    result = send_teams_message_raw(message, title, color="0078D4")
    
    if result["success"]:
        return f"✅ Brief通知已发送到Teams"
    else:
        return f"❌ 发送失败：{result['error']}"


@tool
def send_teams_project_notification(project_name: str, status: str, assigned_to: str = None, runtime: ToolRuntime = None) -> str:
    """
    发送项目创建/更新通知到Teams频道
    
    Args:
        project_name: 项目名称
        status: 项目状态
        assigned_to: 分配给的员工（可选）
    
    Returns:
        发送结果描述
    """
    ctx = runtime.context if runtime else new_context(method="send_teams_project_notification")
    
    title = "🚀 项目已创建"
    
    message = f"""
**项目名称：** {project_name}

**状态：** {status}
"""
    
    if assigned_to:
        message += f"\n**分配给：** {assigned_to}"
    
    message += f"""
---
*此消息由广告项目经理Agent自动发送*
"""
    
    # 根据状态选择颜色
    color_map = {
        "未开始": "F0AD4E",    # 黄色
        "进行中": "0078D4",    # 蓝色
        "已完成": "5CB85C",    # 绿色
        "已延期": "D9534F",    # 红色
    }
    color = color_map.get(status, "0078D4")
    
    result = send_teams_message_raw(message, title, color)
    
    if result["success"]:
        return f"✅ 项目通知已发送到Teams"
    else:
        return f"❌ 发送失败：{result['error']}"
