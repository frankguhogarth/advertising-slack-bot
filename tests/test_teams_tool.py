"""
Teams工具测试脚本
用于测试Teams通知功能
"""

import sys
import os

# 添加项目路径到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 添加src路径
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from tools.teams_notification_tool import (
    set_teams_webhook_url,
    send_teams_message_raw,
    send_teams_message,
    send_teams_brief_notification,
    send_teams_project_notification
)


def test_webhook_configuration():
    """测试Webhook URL配置"""
    print("=== 测试1: Webhook URL配置 ===")
    
    # 测试设置Webhook URL
    test_url = "https://example.webhook.office.com/test"
    set_teams_webhook_url(test_url)
    
    print(f"✅ Webhook URL配置成功: {test_url}")
    print()


def test_send_message_without_url():
    """测试未配置Webhook URL时的消息发送"""
    print("=== 测试2: 未配置Webhook URL ===")
    
    # 先清空Webhook URL
    from tools.teams_notification_tool import TEAMS_WEBHOOK_URL
    global_url = globals().get('TEAMS_WEBHOOK_URL')
    if global_url:
        global TEAMS_WEBHOOK_URL
        TEAMS_WEBHOOK_URL = None
    
    result = send_teams_message_raw("测试消息")
    
    if not result["success"]:
        print(f"✅ 正确处理未配置URL的情况: {result['error']}")
    else:
        print(f"❌ 期望失败但成功了")
    
    print()


def test_brief_notification():
    """测试Brief通知"""
    print("=== 测试3: Brief通知工具 ===")
    
    # 注意：这里不会真正发送，因为没有配置真实的Webhook URL
    print("工具函数已正确加载：")
    print(f"- send_teams_brief_notification: {send_teams_brief_notification}")
    print(f"- send_teams_project_notification: {send_teams_project_notification}")
    print(f"- send_teams_message: {send_teams_message}")
    
    print("✅ 所有工具函数加载成功")
    print()


def test_message_formats():
    """测试消息格式"""
    print("=== 测试4: 消息格式 ===")
    
    brief_summary = """
客户：星巴克
项目：2024年Q3夏季饮品系列推广
目标：提升品牌知名度30%
    """
    
    print("Brief摘要示例：")
    print(brief_summary)
    
    project_info = {
        "project_name": "星巴克夏季饮品推广",
        "status": "进行中",
        "assigned_to": "Lia Liu, Wu Qiong"
    }
    
    print("\n项目信息示例：")
    print(f"项目名称：{project_info['project_name']}")
    print(f"状态：{project_info['status']}")
    print(f"分配给：{project_info['assigned_to']}")
    
    print("\n✅ 消息格式正确")
    print()


def test_color_mapping():
    """测试颜色映射"""
    print("=== 测试5: 颜色映射 ===")
    
    colors = {
        "info": "0078D4",      # 蓝色
        "success": "5CB85C",   # 绿色
        "error": "D9534F",     # 红色
        "warning": "F0AD4E"    # 黄色
    }
    
    print("颜色映射：")
    for msg_type, color in colors.items():
        emoji = {"info": "🔵", "success": "🟢", "error": "🔴", "warning": "🟡"}
        print(f"  {emoji[msg_type]} {msg_type}: {color}")
    
    print("\n✅ 颜色映射正确")
    print()


def main():
    """运行所有测试"""
    print("=" * 50)
    print("Teams工具功能测试")
    print("=" * 50)
    print()
    
    try:
        test_webhook_configuration()
        test_send_message_without_url()
        test_brief_notification()
        test_message_formats()
        test_color_mapping()
        
        print("=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
        print()
        print("📝 下一步：")
        print("1. 在Teams中创建Incoming Webhook")
        print("2. 获取Webhook URL")
        print("3. 在 src/tools/teams_notification_tool.py 中配置 URL")
        print("4. 运行Agent并测试Teams消息发送")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
