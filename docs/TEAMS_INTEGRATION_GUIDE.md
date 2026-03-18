# Microsoft Teams 集成配置指南

## 概述

本Agent支持将重要消息自动发送到Microsoft Teams频道，实现实时通知和协作。

## 配置步骤

### 第一步：在Teams中创建Incoming Webhook

1. **打开Teams并登录**

2. **进入目标频道**
   - 导航到你想要接收通知的频道
   - 例如："项目管理" 或 "Brief通知"

3. **添加Incoming Webhook**
   - 点击频道名称右上角的 **三个点（...）**
   - 选择 **"Connectors"（连接器）**
   - 在连接器列表中搜索 **"Incoming Webhook"**
   - 点击 **"Configure"（配置）**

4. **配置Webhook**
   - **Name**：输入连接器名称，例如 `广告项目经理Agent`
   - **Image**：（可选）上传一个头像图片
   - 点击 **"Create"（创建）**

5. **复制Webhook URL**
   - 创建后会显示一个URL，格式类似：
     ```
     https://your-team.webhook.office.com/webhookb2/xxx/IncomingWebhook/yyy/zzz
     ```
   - 点击 **"Copy"（复制）**
   - **妥善保存这个URL**，下一步需要使用

6. **完成**
   - 点击 **"Done"** 完成配置

### 第二步：在Agent中配置Webhook URL

有两种方式配置Webhook URL：

#### 方式A：通过代码配置（推荐）

1. **编辑工具文件**
   - 打开 `src/tools/teams_notification_tool.py`
   - 找到文件开头的全局变量 `TEAMS_WEBHOOK_URL`
   - 将你的Webhook URL粘贴进去：

   ```python
   # Teams Webhook URL
   TEAMS_WEBHOOK_URL = "https://your-team.webhook.office.com/webhookb2/xxx/IncomingWebhook/yyy/zzz"
   ```

2. **保存文件**

#### 方式B：运行时配置（临时）

如果不想修改代码，可以在Agent运行时调用 `set_teams_webhook_url` 函数设置：

```python
from tools.teams_notification_tool import set_teams_webhook_url

# 设置Webhook URL
set_teams_webhook_url("https://your-team.webhook.office.com/webhookb2/xxx/IncomingWebhook/yyy/zzz")
```

## 使用说明

配置完成后，Agent会自动在以下场景发送Teams消息：

### 1. Brief生成通知
当Brief内容确认后，发送Brief摘要到Teams

### 2. 角色确认通知
当确认所需员工角色后，发送角色信息到Teams

### 3. 员工分配通知
当确认员工选择后，发送员工分配信息到Teams

### 4. 邮件发送通知
当Brief发送给执行人员后，发送邮件通知到Teams

### 5. 项目创建通知
当在Notion创建项目卡片后，发送项目信息到Teams

## 消息格式

Teams消息包含以下信息：
- **标题**：消息类型（Brief、角色、员工、项目等）
- **内容**：详细信息摘要
- **颜色**：根据消息类型显示不同颜色
  - 🔵 蓝色（信息通知）
  - 🟢 绿色（成功消息）
  - 🔴 红色（错误消息）
  - 🟡 黄色（警告消息）

## 安全注意事项

⚠️ **重要提示**：
1. **妥善保管Webhook URL**：这个URL是唯一的，泄露后其他人可能向你的频道发送消息
2. **定期更换**：建议定期更换Webhook URL以提高安全性
3. **权限控制**：确保只有授权人员可以访问这个URL

## 故障排查

### 问题1：消息没有发送到Teams

**可能原因**：
- Webhook URL未配置或配置错误
- 网络连接问题
- Teams频道权限问题

**解决方法**：
1. 检查Webhook URL是否正确配置
2. 测试网络连接
3. 确认Teams频道权限是否允许接收外部消息

### 问题2：消息格式显示异常

**可能原因**：
- Markdown格式不兼容
- 特殊字符未正确转义

**解决方法**：
1. 简化消息内容
2. 避免使用复杂的Markdown格式

### 问题3：Webhook URL失效

**可能原因**：
- Webhook连接器被删除
- URL已过期

**解决方法**：
1. 重新创建Incoming Webhook
2. 更新Agent中的Webhook URL

## 示例消息

### Brief生成通知示例
```
📋 星巴克 Brief已生成

**Brief摘要：**

星巴克2024年Q3夏季饮品系列品牌宣传推广活动
- 目标受众：18-35岁一二线城市消费者
- 预期效果：提升品牌知名度30%
- 创意方向：清新、活力、夏日清凉

---
*此消息由广告项目经理Agent自动发送*
```

### 项目创建通知示例
```
🚀 项目已创建

**项目名称：** 星巴克2024年Q3夏季饮品推广

**状态：** 进行中

**分配给：** Lia Liu, Wu Qiong

---
*此消息由广告项目经理Agent自动发送*
```

## 技术支持

如果遇到问题，请：
1. 检查本文档的故障排查部分
2. 查看Agent日志了解详细错误信息
3. 确认Teams和网络配置正确

## 更新日志

### v1.0.0 (2024-03-18)
- 初始版本
- 支持Brief通知、员工分配通知、项目创建通知
- 支持Markdown格式
- 支持彩色消息卡片
