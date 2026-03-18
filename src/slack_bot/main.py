"""
Slack Bot Service
用于接收Slack消息并调用广告项目经理Agent
"""

import os
import sys
import logging
from typing import Dict, List
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = project_root

if src_path not in sys.path:
    sys.path.insert(0, src_path)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

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

# Slack配置（从环境变量获取）
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")

# 创建Slack客户端
client = WebClient(token=SLACK_BOT_TOKEN)
signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

# 存储Agent实例和对话历史
conversation_agents: Dict[str, object] = {}
conversation_contexts: Dict[str, List[dict]] = {}


@app.route('/slack/events', methods=['POST'])
def slack_events():
    """处理Slack事件"""
    logger.info(f"收到Slack请求")

    # 验证请求签名
    try:
        if not signature_verifier.is_valid_request(request.get_data(), request.headers):
            logger.error("无效的请求签名")
            return jsonify({"error": "Invalid request"}), 403
    except Exception as e:
        logger.error(f"签名验证失败: {str(e)}")
        return jsonify({"error": "Invalid signature"}), 403

    data = request.json
    logger.info(f"请求数据类型: {data.get('type')}")

    # URL验证（Slack首次配置时）
    if data.get('type') == 'url_verification':
        challenge = data.get('challenge')
        logger.info(f"URL验证请求，challenge: {challenge}")
        return jsonify({"challenge": challenge})

    # 处理事件回调
    if data.get('type') == 'event_callback':
        event = data.get('event', {})
        event_type = event.get('type')
        logger.info(f"事件类型: {event_type}")

        # 处理消息事件
        if event_type in ['message', 'file_shared']:
            try:
                handle_event(event)
            except Exception as e:
                logger.error(f"处理事件失败: {str(e)}", exc_info=True)

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
            logger.info("忽略Bot自己的消息")
            return

        # 忽略没有文本的消息
        text = event.get('text', '').strip()
        if not text:
            logger.info("忽略空消息")
            return

        # 获取频道ID和用户ID
        channel_id = event.get('channel')
        user_id = event.get('user')
        channel_type = event.get('channel_type', '')

        logger.info(f"收到消息 - 频道: {channel_id}, 用户: {user_id}, 类型: {channel_type}, 内容: {text}")

        # 获取Bot的用户ID
        bot_user_id = get_bot_user_id()

        # 如果不是私聊，检查是否@机器人
        if channel_type != 'im' and bot_user_id:
            if f"<@{bot_user_id}>" not in text:
                logger.info(f"忽略不是发给机器人的消息")
                return

        # 清理消息文本（移除@机器人）
        if bot_user_id:
            clean_text = text.replace(f"<@{bot_user_id}>", "").strip()
        else:
            clean_text = text

        # 获取或创建Agent实例
        if channel_id not in conversation_agents:
            logger.info(f"创建新的Agent实例 - 频道: {channel_id}")
            ctx = new_context(method="slack_bot")
            agent = build_agent(ctx)
            conversation_agents[channel_id] = agent
            conversation_contexts[channel_id] = []

        # 调用Agent处理消息
        logger.info(f"调用Agent处理消息")
        response = call_agent(conversation_agents[channel_id], clean_text, channel_id)

        # 发送回复
        logger.info(f"发送回复到Slack")
        send_slack_message(channel_id, response)

    except Exception as e:
        logger.error(f"处理消息失败: {str(e)}", exc_info=True)


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
        file_url = file_data.get('url_private', '')
        file_type = file_data.get('filetype', 'unknown')

        logger.info(f"文件详情: {file_name}, 类型: {file_type}, URL: {file_url}")

        # 下载文件
        downloaded_file = download_slack_file(file_url)

        if downloaded_file:
            response = f"✅ 收到文件: {file_name}\n\n📁 文件类型: {file_type}\n\n正在处理文件内容...\n\n⚠️ 注意：当前版本已接收文件，文件处理功能正在开发中。"
        else:
            response = f"❌ 下载文件失败: {file_name}"

        send_slack_message(channel_id, response)

    except Exception as e:
        logger.error(f"处理文件失败: {str(e)}", exc_info=True)
        send_slack_message(event.get('channel'), f"❌ 处理文件时出错: {str(e)}")


def download_slack_file(url):
    """下载Slack文件"""
    try:
        response = client.request({
            'method': 'GET',
            'url': url,
            'headers': {'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
        })
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"下载文件失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"下载文件异常: {str(e)}")
        return None


def call_agent(agent, user_message, channel_id):
    """调用Agent处理消息"""
    try:
        # 保存对话历史
        conversation_contexts[channel_id].append({
            "role": "user",
            "content": user_message
        })

        logger.info(f"正在调用Agent处理消息...")

        # 调用Agent的invoke方法
        from langchain_core.messages import HumanMessage

        # 创建消息对象
        messages = [HumanMessage(content=user_message)]

        # 调用Agent
        result = agent.invoke({"messages": messages})

        # 提取回复内容
        if result and "messages" in result:
            last_message = result["messages"][-1]
            response_content = str(last_message.content)
        else:
            response_content = str(result)

        logger.info(f"Agent回复: {response_content[:100]}...")

        # 保存回复到历史
        conversation_contexts[channel_id].append({
            "role": "assistant",
            "content": response_content
        })

        return response_content

    except Exception as e:
        logger.error(f"调用Agent失败: {str(e)}", exc_info=True)
        return f"❌ 处理失败: {str(e)}"


def send_slack_message(channel_id, text):
    """发送消息到Slack"""
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=text,
            mrkdwn=True
        )
        logger.info(f"消息发送成功，消息ID: {response['ts']}")
    except SlackApiError as e:
        logger.error(f"发送消息失败: {e.response['error']}")


def get_bot_user_id():
    """获取Bot的用户ID"""
    try:
        auth_info = client.auth_test()
        bot_user_id = auth_info['user_id']
        logger.info(f"Bot用户ID: {bot_user_id}")
        return bot_user_id
    except SlackApiError as e:
        logger.error(f"获取Bot ID失败: {e.response['error']}")
        return None


@app.route('/health', methods=['GET'])
def health():
    """健康检查端点"""
    return jsonify({"status": "healthy", "bot_token": "configured" if SLACK_BOT_TOKEN else "not configured"})


@app.route('/info', methods=['GET'])
def info():
    """获取Bot信息"""
    try:
        bot_info = client.auth_test()
        return jsonify({
            "status": "ok",
            "bot_id": bot_info.get('bot_id'),
            "user_id": bot_info.get('user_id'),
            "team": bot_info.get('team'),
            "bot_token_configured": bool(SLACK_BOT_TOKEN),
            "signing_secret_configured": bool(SLACK_SIGNING_SECRET)
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})


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
    logger.info("=" * 50)
    logger.info("启动Slack Bot服务")
    logger.info("=" * 50)
    logger.info(f"端口: {port}")
    logger.info(f"Bot Token: {SLACK_BOT_TOKEN[:20]}...")
    logger.info(f"Signing Secret: {SLACK_SIGNING_SECRET[:10]}...")
    logger.info("=" * 50)

    # 获取Bot信息
    try:
        bot_info = client.auth_test()
        logger.info(f"Bot名称: {bot_info.get('user')}")
        logger.info(f"Team: {bot_info.get('team')}")
    except Exception as e:
        logger.warning(f"无法获取Bot信息: {str(e)}")

    logger.info("服务已启动，等待Slack事件...")
    logger.info("=" * 50)

    app.run(host='0.0.0.0', port=port, debug=False)
