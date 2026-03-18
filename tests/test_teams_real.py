"""
测试Teams真实消息发送
"""

import sys
import os

# 添加项目路径到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from tools.teams_notification_tool import (
    send_teams_message_raw,
    send_teams_message,
    send_teams_brief_notification,
    send_teams_project_notification
)


def test_basic_message():
    """测试发送基本消息"""
    print("=== 测试1: 发送基本消息 ===")
    
    message = """
## 🎉 Teams集成配置成功！

广告项目经理Agent已成功连接到Teams频道。

### ✅ 已配置功能
- Brief生成通知
- 员工分配通知
- 项目创建通知
- 邮件发送通知

### 📝 下一步
现在你可以正常使用Agent，所有重要消息都会自动发送到这里！

---
*测试消息 - 由广告项目经理Agent发送*
"""

    result = send_teams_message_raw(message, "🔔 系统通知", color="5CB85C")
    
    if result["success"]:
        print("✅ 消息发送成功！")
        print(f"   结果: {result['message']}")
    else:
        print(f"❌ 消息发送失败: {result['error']}")
    
    print()
    return result["success"]


def test_brief_notification():
    """测试Brief通知"""
    print("=== 测试2: Brief通知 ===")
    
    brief_summary = """**客户**: 星巴克
**项目**: 2024年Q3夏季饮品系列推广
**目标受众**: 18-35岁一二线城市消费者
**预期效果**: 提升品牌知名度30%"""

    title = "📋 星巴克 Brief已生成"
    message = f"""**Brief摘要：**

{brief_summary}

---
*此消息由广告项目经理Agent自动发送*
"""

    result = send_teams_message_raw(message, title, color="0078D4")
    
    if result["success"]:
        print("✅ Brief通知发送成功！")
    else:
        print(f"❌ Brief通知发送失败: {result['error']}")
    
    print()
    return result["success"]


def test_project_notification():
    """测试项目通知"""
    print("=== 测试3: 项目通知 ===")
    
    project_name = "星巴克夏季饮品推广"
    status = "进行中"
    assigned_to = "Lia Liu, Wu Qiong"
    
    title = "🚀 项目已创建"
    message = f"""**项目名称：** {project_name}

**状态：** {status}

**分配给：** {assigned_to}

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
        print("✅ 项目通知发送成功！")
    else:
        print(f"❌ 项目通知发送失败: {result['error']}")
    
    print()
    return result["success"]


def main():
    """运行测试"""
    print("=" * 60)
    print("Teams真实消息发送测试")
    print("=" * 60)
    print()
    
    success_count = 0
    total_tests = 3
    
    # 依次执行测试
    if test_basic_message():
        success_count += 1
    
    if test_brief_notification():
        success_count += 1
    
    if test_project_notification():
        success_count += 1
    
    # 输出总结
    print("=" * 60)
    print(f"测试完成: {success_count}/{total_tests} 成功")
    print("=" * 60)
    
    if success_count == total_tests:
        print("\n🎉 所有测试通过！Teams集成配置成功！")
        print("\n现在你可以在Teams频道看到所有Agent的消息通知了！")
    else:
        print(f"\n⚠️ 有 {total_tests - success_count} 个测试失败")
        print("请检查:")
        print("1. Webhook URL是否正确")
        print("2. 网络连接是否正常")
        print("3. Teams频道权限是否正确")


if __name__ == "__main__":
    main()
