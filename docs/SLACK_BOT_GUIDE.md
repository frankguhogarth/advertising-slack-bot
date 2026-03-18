# Slack Bot 完整配置指南

## 概述

本指南将帮助你在Slack中创建一个完整的对话Bot，实现：
- ✅ 双向对话（Slack ↔ Agent）
- ✅ 文件上传和处理
- ✅ 多轮对话
- ✅ 消息历史
- ✅ **完全免费**

## 架构说明

```
Slack用户
    ↓ (消息/文件)
Slack Bot
    ↓ (Events API)
你的Bot服务 (Python)
    ↓ (调用)
广告项目经理Agent
    ↓ (回复)
Bot服务
    ↓ (Web API)
Slack (显示给用户)
```

## 目录

1. [前置要求](#前置要求)
2. [创建Slack App](#创建slack-app)
3. [配置Bot权限](#配置bot权限)
4. [安装到Workspace](#安装到workspace)
5. [代码实现](#代码实现)
6. [启动和测试](#启动和测试)
7. [常见问题](#常见问题)
8. [进阶功能](#进阶功能)

---

## 前置要求

### 必需资源
1. **Slack Workspace**（免费）
   - 如果没有，需要创建一个
   - 访问：https://slack.com/get-started
   - 创建免费Workspace

2. **开发环境**
   - Python 3.8+
   - pip包管理器
   - Slack账户（有管理权限更好）

### 可选但推荐
- VS Code或其他代码编辑器
- Postman（用于API测试）
- Slack CLI工具

---

## 创建Slack App

### 步骤1：创建App

1. **进入Slack API网站**
   - 访问：https://api.slack.com/apps
   - 使用Slack账户登录

2. **创建新App**
   - 点击右上角的 **"Create New App"**
   - 选择 **"From scratch"**
   
3. **配置基本信息**
   ```
   App Name: 广告项目经理Bot
   Pick a workspace: 选择你的Workspace
   ```
   
4. **点击 "Create App"**
   - App创建成功！

### 步骤2：配置基本信息

1. **进入App设置**
   - 在左侧菜单找到 **"Basic Information"**
   - 记录以下信息：
   ```
   App ID: (自动生成)
   Client ID: (自动生成)
   Client Secret: (暂时不需要)
   Signing Secret: (后面会用到)
   ```

2. **配置App描述（可选）**
   ```
   Short Description: 广告项目管理和Brief整理助手
   Description: 帮助团队整理客户brief、分配员工、创建项目的AI助手
   ```

---

## 配置Bot权限

### 步骤1：添加Bot功能

1. **进入"Add features and functionality"**
   - 在左侧菜单找到 **"Features"**
   - 点击 **"Bot Token & Scopes"**

2. **配置Bot权限（Scopes）**
   
   **点击 "Add an OAuth Scope"**，添加以下权限：
   
   **Bot Token Scopes**：
   ```
   chat:write          - 发送消息
   channels:history    - 读取频道历史
   groups:history      - 读取私有频道历史
   im:history          - 读取私聊历史
   mpim:history        - 读取多对多私聊历史
   files:write         - 上传文件
   files:read          - 读取文件
   reactions:write     - 添加表情回复
   ```

3. **安装Bot到Workspace**
   - 滚动到页面顶部
   - 点击 **"Install to Workspace"**
   - 点击 **"Allow"** 授权

4. **保存Bot Token**
   ```
   Bot User OAuth Token: xoxb-xxxx-xxxx-xxxx
   ```
   > ⚠️ **重要**：请保存这个Token，类似密码！

---

## 配置事件订阅

### 步骤1：启用事件订阅

1. **进入"Event Subscriptions"**
   - 在左侧菜单找到 **"Features"**
   - 点击 **"Event Subscriptions"**
   - 打开 **"Enable Events"** 开关

2. **配置Request URL**
   
   **这是你的Bot服务接收消息的地址**
   
   如果你有服务器：
   ```
   Request URL: https://your-server.com/slack/events
   ```
   
   如果使用ngrok测试（本地开发）：
   ```
   Request URL: https://your-ngrok-url.ngrok.io/slack/events
   ```
   
   > 注意：这个URL需要验证，稍后在代码中实现

3. **订阅事件（Subscribe to bot events）**
   
   点击 **"Subscribe to bot events"**，添加：
   ```
   message.channels    - 频道消息
   message.groups      - 私有频道消息
   message.im          - 私聊消息
   message.mpim        - 多对多私聊消息
   file_shared         - 文件共享
   ```

4. **保存配置**
   - 点击页面底部的 **"Save Changes"**

---

## 配置App Manifest（快速配置）

### 快速配置方法

如果你想快速配置，可以使用App Manifest：

1. **进入App设置**
   - 在左侧菜单找到 **"Basic Information"**
   - 点击 **"Manifest"**

2. **粘贴以下Manifest**

```yaml
display_information:
  name: 广告项目经理Bot
  description: 广告项目管理和Brief整理助手
  background_color: "#2D3748"
  long_description: 这是一个帮助广告公司整理客户brief、智能分配员工、创建项目的AI助手。支持多轮对话、文件上传、自动任务分配等功能。

features:
  bot_user:
    display_name: 广告项目经理
    always_online: false

oauth_config:
  scopes:
    bot:
      - chat:write
      - channels:history
      - groups:history
      - im:history
      - mpim:history
      - files:write
      - files:read
      - reactions:write

settings:
  event_subscriptions:
    bot_events:
      - message.channels
      - message.groups
      - message.im
      - message.mpim
      - file_shared
  interactivity:
    is_enabled: true
```

3. **点击 "Next"**
4. **点击 "Create"**

---

## 安装到Workspace

### 步骤1：安装App

1. **进入"Install App"**
   - 在左侧菜单找到 **"Install your app"**
   - 点击 **"Install to Workspace"**

2. **授权访问**
   - 查看请求的权限
   - 点击 **"Allow"**

3. **保存Token**
   ```
   Bot User OAuth Token: xoxb-xxxx-xxxx-xxxx
   ```
   > ⚠️ **重要**：这个Token只显示一次，请立即保存！

### 步骤2：将Bot添加到频道

1. **在Slack中邀请Bot**
   - 进入你想让Bot工作的频道
   - 输入 `/invite @广告项目经理`
   - 点击邀请

2. **测试Bot是否在线**
   - 发送消息给Bot：`@广告项目经理 你好`
   - Bot应该会回复（如果代码已部署）

---

## 代码实现

### 步骤1：安装依赖

```bash
# 安装Slack SDK
pip install slack-sdk

# 安装Web框架
pip install flask

# 安装其他依赖
pip install python-dotenv
pip install requests
```

### 步骤2：创建Bot服务代码

创建 `src/slack_bot/main.py`：

```python
"""
Slack Bot Service
用于接收Slack消息并调用广告项目经理Agent
"""

import os
import sys
import logging
from typing import Dict, List
from io import BytesIO

# 添加项目路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

# 导入Agent
from agents.agent import build_agent
from coze_coding_utils.runtime_ctx.context import new_context

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)

# Slack配置
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# 创建Slack客户端
client = WebClient(token=SLACK_BOT_TOKEN)
signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

# 存储Agent实例和对话历史
conversation_agents: Dict[str, object] = {}
conversation_contexts: Dict[str, List[dict]] = {}


@app.route('/slack/events', methods=['POST'])
def slack_events():
    """处理Slack事件"""
    # 验证请求签名
    if not signature_verifier.is_valid_request(request.get_data(), request.headers):
        return jsonify({"error": "Invalid request"}), 403
    
    data = request.json
    
    # URL验证（Slack首次配置时）
    if data.get('type') == 'url_verification':
        return jsonify({"challenge": data.get('challenge')})
    
    # 处理事件回调
    if data.get('type') == 'event_callback':
        event = data.get('event', {})
        event_type = event.get('type')
        
        # 处理消息事件
        if event_type in ['message', 'file_shared']:
            try:
                handle_event(event)
            except Exception as e:
                logger.error(f"处理事件失败: {str(e)}")
    
    return jsonify({"status": "ok"})


def handle_event(event):
    """处理单个事件"""
    event_type = event.get('type')
    
    if event_type == 'message':
        handle_message(event)
    elif event_type == 'file_shared':
        handle_file(event)


def handle_message(event):
    """处理消息事件"""
    try:
        # 忽略Bot自己的消息
        if event.get('subtype') == 'bot_message':
            return
        
        # 忽略没有文本的消息
        text = event.get('text', '').strip()
        if not text:
            return
        
        # 获取频道ID和用户ID
        channel_id = event.get('channel')
        user_id = event.get('user')
        
        # 检查是否是@机器人
        bot_user_id = get_bot_user_id()
        if f"<@{bot_user_id}>" not in text and event.get('channel_type') != 'im':
            return  # 忽略不是发给机器人的消息
        
        # 清理消息文本（移除@机器人）
        clean_text = text.replace(f"<@{bot_user_id}>", "").strip()
        
        logger.info(f"收到消息 - 频道: {channel_id}, 用户: {user_id}, 内容: {clean_text}")
        
        # 获取或创建Agent实例
        if channel_id not in conversation_agents:
            ctx = new_context(method="slack_bot")
            agent = build_agent(ctx)
            conversation_agents[channel_id] = agent
            conversation_contexts[channel_id] = []
        
        # 调用Agent处理消息
        response = call_agent(conversation_agents[channel_id], clean_text, channel_id)
        
        # 发送回复
        send_slack_message(channel_id, response)
        
    except Exception as e:
        logger.error(f"处理消息失败: {str(e)}")
        import traceback
        traceback.print_exc()


def handle_file(event):
    """处理文件分享事件"""
    try:
        file_id = event.get('file_id')
        channel_id = event.get('channel')
        user_id = event.get('user')
        
        logger.info(f"收到文件 - 文件ID: {file_id}, 频道: {channel_id}, 用户: {user_id}")
        
        # 获取文件信息
        file_info = client.files_info(file=file_id)
        file_data = file_info['file']
        
        file_name = file_data['name']
        file_url = file_data['url_private']
        
        logger.info(f"文件详情: {file_name}, URL: {file_url}")
        
        # 下载文件
        downloaded_file = download_slack_file(file_url)
        
        if downloaded_file:
            # 处理文件内容（这里需要实现文件解析）
            response = f"收到文件: {file_name}\n\n正在处理文件内容...\n\n文件已下载到服务器。"
        else:
            response = f"❌ 下载文件失败: {file_name}"
        
        send_slack_message(channel_id, response)
        
    except Exception as e:
        logger.error(f"处理文件失败: {str(e)}")


def download_slack_file(url):
    """下载Slack文件"""
    try:
        response = client.request({
            'method': 'GET',
            'url': url,
            'headers': {'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
        })
        return response.content
    except Exception as e:
        logger.error(f"下载文件失败: {str(e)}")
        return None


def call_agent(agent, user_message, channel_id):
    """调用Agent处理消息"""
    try:
        # 这里需要实现与Agent的集成
        # 由于Agent是同步的，需要特殊处理
        
        # 保存对话历史
        conversation_contexts[channel_id].append({
            "role": "user",
            "content": user_message
        })
        
        # 模拟Agent响应（实际需要集成你的Agent）
        response = f"收到你的消息: {user_message}\n\n这是Agent的回复。"
        
        # 保存回复到历史
        conversation_contexts[channel_id].append({
            "role": "assistant",
            "content": response
        })
        
        return response
        
    except Exception as e:
        logger.error(f"调用Agent失败: {str(e)}")
        return f"❌ 处理失败: {str(e)}"


def send_slack_message(channel_id, text):
    """发送消息到Slack"""
    try:
        client.chat_postMessage(
            channel=channel_id,
            text=text,
            mrkdwn=True
        )
    except SlackApiError as e:
        logger.error(f"发送消息失败: {e.response['error']}")


def get_bot_user_id():
    """获取Bot的用户ID"""
    try:
        auth_info = client.auth_test()
        return auth_info['user_id']
    except SlackApiError as e:
        logger.error(f"获取Bot ID失败: {e.response['error']}")
        return None


@app.route('/health', methods=['GET'])
def health():
    """健康检查端点"""
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    # 检查环境变量
    if not SLACK_BOT_TOKEN:
        logger.error("SLACK_BOT_TOKEN 未设置")
        sys.exit(1)
    
    if not SLACK_SIGNING_SECRET:
        logger.error("SLACK_SIGNING_SECRET 未设置")
        sys.exit(1)
    
    # 启动服务
    port = int(os.getenv('PORT', 5000))
    logger.info(f"启动Slack Bot服务 - 端口: {port}")
    
    app.run(host='0.0.0.0', port=port, debug=True)
```

### 步骤3：创建环境变量文件

创建 `.env` 文件：

```bash
# Slack Bot配置
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here

# Agent配置
COZE_WORKSPACE_PATH=/workspace/projects

# 服务配置
PORT=5000
```

### 步骤4：更新requirements.txt

添加到 `requirements.txt`：

```txt
# 现有依赖...
langchain>=0.1.0
langchain-openai>=0.0.5
langgraph>=0.0.20

# Slack Bot
slack-sdk>=3.26.0
flask>=3.0.0
python-dotenv>=1.0.0
requests>=2.31.0
```

---

## 启动和测试

### 步骤1：安装依赖

```bash
# 进入项目目录
cd /workspace/projects

# 安装依赖
pip install slack-sdk flask python-dotenv

# 或者从requirements.txt安装
pip install -r requirements.txt
```

### 步骤2：设置环境变量

**方法A：使用.env文件**
```bash
# 编辑.env文件
nano .env
```

**方法B：直接设置环境变量**
```bash
export SLACK_BOT_TOKEN="xoxb-your-token-here"
export SLACK_SIGNING_SECRET="your-secret-here"
```

### 步骤3：本地启动

```bash
# 启动服务
python src/slack_bot/main.py
```

服务启动后应该看到：
```
INFO - 启动Slack Bot服务 - 端口: 5000
 * Running on http://0.0.0.0:5000
```

### 步骤4：测试本地服务

使用ngrok创建隧道（让Slack可以访问本地服务）：

```bash
# 安装ngrok
# 访问：https://ngrok.com/ 下载并安装

# 启动ngrok
ngrok http 5000

# 复制显示的URL，例如：
# https://xxxx-xx-xx-xx-xx.ngrok.io
```

### 步骤5：更新Slack App配置

1. **回到Slack App设置**
   - 进入 **"Event Subscriptions"**
   - 更新 **Request URL**：
   ```
   https://your-ngrok-url.ngrok.io/slack/events
   ```

2. **验证URL**
   - Slack会自动验证URL
   - 如果成功，会显示绿色勾号

3. **保存配置**

### 步骤6：在Slack中测试

1. **邀请Bot到频道**
   ```
   /invite @广告项目经理
   ```

2. **发送测试消息**
   ```
   @广告项目经理 你好
   ```

3. **预期回复**
   ```
   收到你的消息: 你好
   
   这是Agent的回复。
   ```

---

## 常见问题

### Q1: Bot不回复消息

**可能原因**：
- Bot未添加到频道
- Request URL配置错误
- 环境变量未设置
- 服务未启动

**解决方法**：
1. 确认Bot已邀请到频道
2. 检查ngrok是否正常运行
3. 验证环境变量是否正确设置
4. 查看服务日志

### Q2: 文件上传失败

**可能原因**：
- Bot没有文件权限
- 文件太大
- 文件格式不支持

**解决方法**：
1. 确认Bot Token包含 `files:write` 和 `files:read` 权限
2. 检查文件大小限制
3. 确认支持的文件格式

### Q3: 消息历史丢失

**可能原因**：
- 会话ID不一致
- 服务器重启

**解决方法**：
1. 使用channel_id作为会话标识
2. 考虑使用Redis或数据库保存对话历史
3. 实现会话持久化

### Q4: 验证URL失败

**可能原因**：
- ngrok未启动
- 端口不对
- 代码中的错误

**解决方法**：
1. 确认ngrok正在运行
2. 检查端口是否正确（默认5000）
3. 查看服务日志，看是否有错误

### Q5: 无法连接到Agent

**可能原因**：
- Agent服务未运行
- 依赖包未安装
- 环境变量配置错误

**解决方法**：
1. 确认Agent服务正常运行
2. 安装所有必要的依赖包
3. 检查环境变量配置

---

## 进阶功能

### 1. 支持富文本消息

```python
def send_slack_message_with_blocks(channel_id, text, blocks):
    """发送带富文本的消息"""
    try:
        client.chat_postMessage(
            channel=channel_id,
            text=text,
            blocks=blocks
        )
    except SlackApiError as e:
        logger.error(f"发送消息失败: {e.response['error']}")
```

### 2. 支持按钮交互

```python
def send_slack_message_with_buttons(channel_id, text):
    """发送带按钮的消息"""
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "确认"
                    },
                    "action_id": "confirm_button",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "取消"
                    },
                    "action_id": "cancel_button"
                }
            ]
        }
    ]
    
    send_slack_message_with_blocks(channel_id, text, blocks)
```

### 3. 上传文件到Slack

```python
def upload_file_to_slack(channel_id, file_path, file_name):
    """上传文件到Slack"""
    try:
        with open(file_path, 'rb') as f:
            client.files_upload(
                channels=channel_id,
                file=f,
                filename=file_name
            )
        logger.info(f"文件上传成功: {file_name}")
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
```

### 4. 对话历史持久化

```python
import json
from datetime import datetime

def save_conversation(channel_id, message):
    """保存对话历史到文件"""
    conversation_file = f"conversations/{channel_id}.json"
    
    if not os.path.exists(conversation_file):
        with open(conversation_file, 'w') as f:
            json.dump([], f)
    
    with open(conversation_file, 'r') as f:
        history = json.load(f)
    
    history.append({
        "timestamp": datetime.now().isoformat(),
        **message
    })
    
    with open(conversation_file, 'w') as f:
        json.dump(history, f, indent=2)


def load_conversation(channel_id):
    """加载对话历史"""
    conversation_file = f"conversations/{channel_id}.json"
    
    if not os.path.exists(conversation_file):
        return []
    
    with open(conversation_file, 'r') as f:
        return json.load(f)
```

---

## 部署到云服务

### 方案1：Render（推荐，免费）

1. **准备GitHub仓库**
   - 将代码推送到GitHub
   - 确保包含 `.env.example`

2. **在Render创建服务**
   - 访问：https://render.com/
   - 创建新的 **Web Service**
   - 连接GitHub仓库
   - 设置环境变量

3. **部署**
   - Render会自动部署
   - 获得公网URL
   - 更新Slack App的Request URL

### 方案2：Railway

1. **安装Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **初始化项目**
   ```bash
   railway init
   railway up
   ```

3. **配置环境变量**
   ```bash
   railway variables set SLACK_BOT_TOKEN=your-token
   railway variables set SLACK_SIGNING_SECRET=your-secret
   ```

### 方案3：Heroku

1. **安装Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Windows
   # 下载安装程序
   ```

2. **创建应用**
   ```bash
   heroku create your-bot-name
   ```

3. **配置环境变量**
   ```bash
   heroku config:set SLACK_BOT_TOKEN=your-token
   heroku config:set SLACK_SIGNING_SECRET=your-secret
   ```

4. **部署**
   ```bash
   git push heroku main
   ```

---

## 成本估算

### Slack
- ✅ **完全免费**
- 无限消息
- 无限用户
- 所有功能免费

### 云服务（可选）
| 平台 | 免费额度 | 付费方案 |
|------|---------|---------|
| Render | 750小时/月 | $7/月起 |
| Railway | $5免费额度 | $5/月起 |
| Heroku | 550小时/月 | $5/月起 |
| AWS Lambda | 100万次请求/月 | 按使用量 |

**总成本**：$0（本地开发）或 $0-7/月（云部署）

---

## 安全建议

1. **保护Token**
   - 不要在代码中硬编码Token
   - 使用环境变量
   - 不要提交到Git仓库
   - 定期轮换Token

2. **验证请求**
   - 始终验证Slack请求签名
   - 防止伪造请求

3. **权限最小化**
   - 只给Bot必要的权限
   - 定期审查权限设置

4. **日志和监控**
   - 记录所有事件
   - 监控Bot使用情况
   - 设置告警

---

## 资源链接

- [Slack API文档](https://api.slack.com/)
- [Slack Python SDK](https://slack.dev/python-slack-sdk/)
- [Slack Bot最佳实践](https://api.slack.com/bot-users/best-practices)
- [Slack事件订阅](https://api.slack.com/apis/connections/events-api)

---

## 下一步

1. ✅ **测试本地开发**
   - 使用ngrok测试
   - 在Slack中测试对话

2. ✅ **部署到云服务**
   - 选择Render/Railway/Heroku
   - 配置环境变量
   - 更新Slack App配置

3. ✅ **集成现有Agent**
   - 修改`call_agent`函数
   - 对接广告项目经理Agent
   - 测试完整流程

4. ✅ **添加功能**
   - 文件处理
   - 富文本消息
   - 按钮交互

---

## 需要帮助？

如果在配置过程中遇到问题：
1. 查看本指南的"常见问题"章节
2. 查看Slack API官方文档
3. 检查服务日志
4. 使用Slack的App Directory查看错误信息

---

**祝配置顺利！🚀**
