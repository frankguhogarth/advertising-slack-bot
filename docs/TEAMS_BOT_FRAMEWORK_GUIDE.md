# Microsoft Teams Bot Framework 完整配置指南

## 概述

本指南将帮助你在Microsoft Teams中创建一个完整的对话Bot，实现：
- ✅ 双向对话（Teams ↔ Agent）
- ✅ 文件上传和处理
- ✅ 多轮对话
- ✅ 消息历史
- ✅ 富文本和卡片支持

## 架构说明

```
Teams用户
    ↓ (消息/文件)
Microsoft Teams
    ↓ (Bot Framework)
Azure Bot Service
    ↓ (HTTP请求)
你的Bot服务 (Python)
    ↓ (调用)
广告项目经理Agent
    ↓ (回复)
Bot服务
    ↓ (发送响应)
Teams (显示给用户)
```

## 目录

1. [前置要求](#前置要求)
2. [Azure资源配置](#azure资源配置)
3. [Bot应用注册](#bot应用注册)
4. [代码实现](#代码实现)
5. [部署配置](#部署配置)
6. [Teams中配置Bot](#teams中配置bot)
7. [测试验证](#测试验证)
8. [常见问题](#常见问题)

---

## 前置要求

### 必需资源
1. **Azure账户**（付费或免费）
   - 访问：https://portal.azure.com/
   - 如果没有账户，需要创建一个
   - 免费账户有$200额度，足够测试使用

2. **开发环境**
   - Python 3.8+
   - pip包管理器
   - Git（可选）

3. **Teams账户**
   - 有权限创建和管理Teams应用
   - 通常需要管理员权限

### 可选但推荐
- VS Code或其他代码编辑器
- Postman（用于API测试）
- Azure CLI（用于快速配置）

---

## Azure资源配置

### 步骤1：创建Azure Bot资源

1. **登录Azure Portal**
   - 访问：https://portal.azure.com/
   - 使用你的Azure账户登录

2. **创建Bot资源**
   - 点击左侧菜单的 **"创建资源"**
   - 搜索 **"Azure Bot"**
   - 点击 **"创建"**

3. **配置基本信息**
   ```
   Bot handle: advertising-project-manager-bot
   定价层: Free (F0) - 适合测试
   发布类型: 多租户
   应用类型: 多租户
   ```

4. **创建完成后保存信息**
   ```
   Bot ID: (自动生成)
   Microsoft App ID: (自动生成)
   ```

### 步骤2：配置Bot的Endpoint

1. **进入Bot配置页面**
   - 在Azure Portal中找到你创建的Bot
   - 点击左侧菜单的 **"Configuration"**

2. **配置Messaging Endpoint**
   ```
   Messaging endpoint:
   https://your-domain.com/api/messages
   ```
   > 注意：这个URL是你的Bot服务运行时的地址，部署后需要更新

### 步骤3：获取Bot凭据

1. **进入"Configuration"页面**
   - 找到 **"Microsoft App ID"**
   - 点击旁边的 **"管理密码"** 链接

2. **保存凭据信息**
   ```
   App ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   Client Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Tenant ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```
   > ⚠️ **重要**：Client Secret只显示一次，请立即保存！

---

## Bot应用注册

### 步骤1：Azure AD应用注册

1. **进入Azure AD**
   - 在Azure Portal中搜索 **"App registrations"**
   - 点击 **"New registration"**

2. **配置应用注册**
   ```
   Name: Advertising Project Manager Bot
   Supported account types: Accounts in any organizational directory and personal Microsoft accounts
   Redirect URI (optional): 留空
   ```

3. **保存应用信息**
   ```
   Application (client) ID: (与Bot的App ID相同)
   Directory (tenant) ID: (与Bot的Tenant ID相同)
   ```

### 步骤2：配置API权限

1. **进入应用的"API permissions"页面**
   - 点击左侧菜单 **"API permissions"**
   - 点击 **"Add a permission"**

2. **添加Microsoft Graph权限**
   ```
   选择 APIs my organization uses → Microsoft Graph
   选择 Delegated permissions
   勾选以下权限：
   - Chat.ReadWrite
   - ChannelMessage.Send.All
   - Team.ReadBasic.All
   - User.Read
   ```

3. **同意授权**
   - 点击 **"Add permissions"**
   - 点击 **"Grant admin consent for [your organization]"**
   > 需要管理员权限

### 步骤3：创建Client Secret

1. **进入"Certificates & secrets"页面**
   - 点击左侧菜单 **"Certificates & secrets"**
   - 点击 **"New client secret"**

2. **配置Secret**
   ```
   Description: Bot Secret
   Expires: 选择合适的时间（推荐180天）
   ```

3. **保存Secret**
   ```
   Value: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   > ⚠️ **重要**：这个Value就是Client Secret，只显示一次！

---

## 代码实现

### 步骤1：安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装Bot Framework SDK
pip install botbuilder-core botbuilder-schema botbuilder-integration-aiohttp
pip install aiohttp
pip install python-dotenv
```

### 步骤2：创建Bot服务代码

创建 `src/teams_bot/main.py`：

```python
"""
Microsoft Teams Bot Service
用于接收Teams消息并调用广告项目经理Agent
"""

import os
import sys
from typing import Dict
import logging
from io import BytesIO

# 添加项目路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from botbuilder.core import (
    BotFrameworkAdapter,
    ActivityHandler,
    TurnContext,
    CardFactory
)
from botbuilder.schema import Activity, ActivityTypes, Attachment

# 导入Agent
from agents.agent import build_agent
from coze_coding_utils.runtime_ctx.context import new_context

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot配置
APP_ID = os.getenv("MICROSOFT_APP_ID")
APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD")

# 创建Adapter
adapter = BotFrameworkAdapter(APP_ID, APP_PASSWORD)


class TeamsBot(ActivityHandler):
    """Teams Bot处理器"""

    def __init__(self):
        self.conversation_agents: Dict[str, object] = {}
        self.conversation_contexts: Dict[str, object] = {}

    async def on_message_activity(self, turn_context: TurnContext):
        """处理接收到的消息"""
        try:
            # 获取会话ID
            conversation_id = turn_context.activity.conversation.id

            # 获取用户消息
            user_message = turn_context.activity.text
            logger.info(f"收到来自Teams的消息: {user_message}")

            # 检查是否有文件附件
            attachments = turn_context.activity.attachments
            if attachments:
                file_info = await self._process_attachments(attachments)
                user_message = f"{user_message}\n\n文件附件: {file_info}"

            # 获取或创建Agent实例
            if conversation_id not in self.conversation_agents:
                ctx = new_context(method="teams_bot")
                agent = build_agent(ctx)
                self.conversation_agents[conversation_id] = agent
                self.conversation_contexts[conversation_id] = {"messages": []}
            else:
                agent = self.conversation_agents[conversation_id]

            # 调用Agent处理消息
            response = await self._call_agent(agent, user_message)

            # 发送回复
            await turn_context.send_activity(response)

        except Exception as e:
            logger.error(f"处理消息时出错: {str(e)}")
            await turn_context.send_activity(f"❌ 处理消息时出错: {str(e)}")

    async def _process_attachments(self, attachments):
        """处理文件附件"""
        file_info = []
        for attachment in attachments:
            if attachment.content_type and attachment.content_url:
                file_info.append(f"📎 {attachment.name} ({attachment.content_type})")
                # 这里可以下载文件并传递给Agent
                logger.info(f"收到文件附件: {attachment.name}, URL: {attachment.content_url}")
        return "\n".join(file_info)

    async def _call_agent(self, agent, user_message):
        """调用Agent处理消息"""
        try:
            # 这里需要实现同步调用Agent的逻辑
            # 由于Agent是同步的，需要使用asyncio.to_thread
            import asyncio

            # 模拟Agent响应（实际需要集成你的Agent）
            response = f"收到你的消息: {user_message}\n\n这是Agent的回复。"
            return response

        except Exception as e:
            logger.error(f"调用Agent时出错: {str(e)}")
            return f"❌ Agent处理出错: {str(e)}"

    async def on_conversation_update_activity(self, turn_context: TurnContext):
        """处理会话更新（如用户加入）"""
        if turn_context.activity.type == ActivityTypes.conversation_update:
            for member in turn_context.activity.members_added:
                if member.id != turn_context.activity.recipient.id:
                    await turn_context.send_activity(
                        "👋 你好！我是广告项目经理Agent。\n"
                        "请发送你的brief内容或上传brief文档，我会帮你分析和整理。"
                    )


# 创建Bot实例
bot = TeamsBot()


async def messages_handler(request):
    """处理传入的HTTP请求"""
    if "application/json" in request.headers["Content-Type"]:
        body = await request.json()
    else:
        return {"status": 415}

    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    try:
        response = await adapter.process_activity(activity, auth_header, bot.on_turn)
        if response:
            return response.body
        return {"status": 200}
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return {"status": 500, "error": str(e)}


# 用于aiohttp的请求处理
from aiohttp import web

async def handle_messages(request):
    """aiohttp请求处理器"""
    body = await request.json()
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    try:
        response = await adapter.process_activity(activity, auth_header, bot.on_turn)
        if response:
            return web.json_response(response.body)
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return web.json_response({"error": str(e)}, status=500)


def create_bot_app():
    """创建aiohttp应用"""
    app = web.Application()
    app.router.add_post("/api/messages", handle_messages)
    return app
```

### 步骤3：创建环境变量文件

创建 `.env` 文件：

```bash
# Azure Bot配置
MICROSOFT_APP_ID=your-app-id-here
MICROSOFT_APP_PASSWORD=your-client-secret-here

# Agent配置
COZE_WORKSPACE_PATH=/workspace/projects
```

---

## 部署配置

### 方案1：本地部署（测试用）

1. **启动Bot服务**

```bash
# 安装aiohttp
pip install aiohttp

# 运行Bot服务
cd src/teams_bot
python main.py
```

2. **使用ngrok创建隧道（测试用）**

```bash
# 安装ngrok
# 访问：https://ngrok.com/ 下载并安装

# 启动ngrok隧道
ngrok http 3978

# 复制显示的HTTPS URL，例如：
# https://xxxx-xx-xx-xx-xx.ngrok.io
```

3. **配置Bot的Endpoint**
   - 回到Azure Portal的Bot配置页面
   - 更新Messaging endpoint：
   ```
   https://your-ngrok-url.ngrok.io/api/messages
   ```

### 方案2：云部署（生产用）

可以使用以下平台部署：

#### Azure App Service（推荐）
```bash
# 使用Azure CLI
az webapp up --name advertising-bot --resource-group myResourceGroup --sku B1

# 配置环境变量
az webapp config appsettings set --name advertising-bot --settings \
  MICROSOFT_APP_ID="your-app-id" \
  MICROSOSOFT_APP_PASSWORD="your-secret"
```

#### Docker部署
创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 3978

CMD ["python", "src/teams_bot/main.py"]
```

构建和运行：
```bash
docker build -t teams-bot .
docker run -p 3978:3978 -e MICROSOFT_APP_ID="xxx" -e MICROSOFT_APP_PASSWORD="xxx" teams-bot
```

#### 其他平台
- **Heroku**
- **AWS Lambda + API Gateway**
- **Google Cloud Functions**

---

## Teams中配置Bot

### 步骤1：创建Teams App

1. **打开Teams App Studio**
   - 在Teams中搜索并添加 **"App Studio"**
   - 或者访问：https://dev.teams.microsoft.com/

2. **创建新应用**
   - 点击 **"Apps"** → **"Create a new app"**
   - 配置基本信息：
   ```
   App name: 广告项目经理Bot
   Version: 1.0.0
   Description: 广告项目管理和Brief整理助手
   Developer name: Your Name
   Website: https://your-website.com
   Privacy URL: https://your-privacy.com
   Terms of use URL: https://your-terms.com
   ```

3. **配置Bot信息**
   - 点击左侧 **"Bot features"**
   - 点击 **"Create a bot"**
   - 输入Bot信息：
   ```
   Bot name: 广告项目经理
   Scope: Team, Personal, Group Chat
   ```

4. **连接Azure Bot**
   - 输入之前创建的Azure Bot的 **Microsoft App ID**
   - 选择你的Bot
   - 保存

5. **发布应用**
   - 点击左侧 **"Publish"**
   - 点击 **"Publish to your org"**
   - 或下载应用包，分发给其他用户

### 步骤2：在Teams中添加Bot

1. **在Teams中搜索应用**
   - 点击左侧 **"Apps"**
   - 搜索你创建的Bot名称

2. **添加到团队或个人**
   - 可以添加到团队频道
   - 或添加到个人聊天

3. **开始对话**
   - 向Bot发送消息
   - Bot应该会回复欢迎消息

---

## 测试验证

### 测试1：基本对话

```
你: 你好
Bot: 👋 你好！我是广告项目经理Agent。请发送你的brief内容或上传brief文档，我会帮你分析和整理。
```

### 测试2：发送文本Brief

```
你: 请帮我整理这个brief：客户是星巴克，需要设计4张banner...
Bot: [Agent处理后的Brief内容]
```

### 测试3：上传文件

1. 在Teams对话中点击 **"附件"** 图标
2. 上传brief文档（PDF/Word/PPT等）
3. Bot应该能接收并处理文件

### 测试4：多轮对话

```
你: 分析这个brief
Bot: [Brief内容]
你: 内容正确，请分配员工
Bot: [员工分配信息]
你: 确认
Bot: [发送邮件和创建项目]
```

---

## 常见问题

### Q1: Bot不回复消息

**可能原因**：
- Endpoint配置错误
- Bot服务未启动
- 防火墙阻止连接

**解决方法**：
1. 检查Azure Portal中的Messaging endpoint是否正确
2. 确认Bot服务正在运行
3. 检查防火墙和网络设置

### Q2: 文件上传失败

**可能原因**：
- Bot没有文件读取权限
- 文件太大
- 文件格式不支持

**解决方法**：
1. 确认Azure AD应用有正确的权限
2. 检查文件大小限制
3. 确认支持的文件格式

### Q3: Bot无法访问Agent

**可能原因**：
- Agent服务未运行
- 依赖包未安装
- 环境变量配置错误

**解决方法**：
1. 确认Agent服务正常运行
2. 安装所有必要的依赖包
3. 检查环境变量配置

### Q4: 对话历史丢失

**可能原因**：
- 会话ID不一致
- Agent内存未正确保存

**解决方法**：
1. 使用conversation_id作为会话标识
2. 在Bot中保存会话状态
3. 考虑使用外部存储（Redis/数据库）

### Q5: 成本问题

**Azure Bot定价**：
- Free (F0): 10,000条消息/月（适合测试）
- Standard (S1): 1,000,000条消息/月（适合生产）

**建议**：
- 测试阶段使用Free层
- 生产环境根据实际使用量选择

---

## 成本估算

### Azure Bot Service
- Free (F0): $0/月（10,000条消息）
- Standard (S1): $0.0025/1000条消息

### 其他Azure服务
- App Service (B1): ~$14/月
- 存储: ~$0.02/GB/月
- 带宽: 前100GB免费

**总计（生产环境）**：约$20-30/月

---

## 安全建议

1. **保护凭据**
   - 使用环境变量存储App ID和Secret
   - 不要在代码中硬编码凭据
   - 定期轮换Secret

2. **访问控制**
   - 限制Bot的可访问范围
   - 使用权限控制谁能使用Bot

3. **日志和监控**
   - 启用Azure Monitor
   - 监控Bot使用情况
   - 设置告警

---

## 下一步

1. **准备Azure账户**
   - 如果没有，先创建一个

2. **按照本指南配置**
   - 逐步完成每个步骤
   - 每完成一步就测试一次

3. **集成现有Agent**
   - 将Bot与现有的广告项目经理Agent集成
   - 实现完整的对话流程

4. **测试和优化**
   - 测试各种使用场景
   - 收集用户反馈
   - 持续优化

---

## 资源链接

- [Bot Framework文档](https://docs.microsoft.com/en-us/azure/bot-service/)
- [Teams开发文档](https://docs.microsoft.com/en-us/microsoftteams/platform/)
- [Bot Framework SDK (Python)](https://github.com/microsoft/botbuilder-python)
- [Azure Bot Pricing](https://azure.microsoft.com/en-us/pricing/details/bot-service/)

---

## 需要帮助？

如果在配置过程中遇到问题，可以：
1. 查看Azure Portal的诊断日志
2. 查看Bot服务的日志输出
3. 参考官方文档
4. 联系技术支持
