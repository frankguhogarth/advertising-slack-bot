# Slack Bot 快速配置清单

## 📋 配置前检查

### 必需资源
- [ ] 有Slack Workspace（或可以创建）
- [ ] 有Slack账户
- [ ] 有Python 3.8+环境
- [ ] 有开发权限（或可以联系管理员）

### 时间估算
- 创建Slack App: 5分钟
- 配置权限: 5分钟
- 安装依赖: 2分钟
- 运行测试: 5分钟
- **总计: 17分钟**

---

## ⚡ 5步快速配置

### 第1步：创建Slack App（5分钟）

```
1. 访问 https://api.slack.com/apps
2. 点击 "Create New App"
3. 选择 "From scratch"
4. 输入App名称: 广告项目经理Bot
5. 选择你的Workspace
6. 点击 "Create App"
```

### 第2步：配置Bot Token（3分钟）

```
1. 进入 "Bot Token & Scopes"
2. 添加权限:
   - chat:write
   - channels:history
   - files:write
   - files:read
3. 点击 "Install to Workspace"
4. 保存 Bot Token: xoxb-xxxx-xxxx-xxxx
```

### 第3步：配置事件订阅（4分钟）

```
1. 进入 "Event Subscriptions"
2. 开启 "Enable Events"
3. 配置 Request URL（暂时留空，后面配置）
4. 添加事件:
   - message.channels
   - message.im
   - file_shared
5. 点击 "Save Changes"
```

### 第4步：安装依赖（2分钟）

```bash
# 安装Slack SDK和Flask
pip install slack-sdk flask python-dotenv

# 或使用requirements.txt
pip install -r requirements_slack_bot.txt
```

### 第5步：运行测试（5分钟）

```bash
# 设置环境变量
export SLACK_BOT_TOKEN="xoxb-your-token"
export SLACK_SIGNING_SECRET="your-secret"

# 启动服务
python src/slack_bot/main.py

# 另开终端，启动ngrok
ngrok http 5000

# 复制ngrok URL
# 回到Slack App配置
# 更新 Event Subscriptions 的 Request URL
```

---

## 📝 需要保存的信息

### Slack App信息
```
App ID: ____________________
Client ID: ____________________
Bot Token: xoxb-____________________
Signing Secret: ____________________
```

### 服务信息
```
本地端口: 5000
ngrok URL: https://__________________.ngrok.io
Request URL: https://__________________.ngrok.io/slack/events
```

---

## 🧪 测试检查

### 本地测试
- [ ] 服务启动成功
- [ ] ngrok运行正常
- [ ] 可以访问 http://localhost:5000/health

### Slack测试
- [ ] URL验证通过（绿色勾号）
- [ ] Bot已添加到频道
- [ ] 可以发送 @广告项目经理 你好
- [ ] Bot回复消息

### 完整流程测试
- [ ] 发送文本消息 → Bot回复
- [ ] 上传文件 → Bot接收
- [ ] 多轮对话 → 保持历史

---

## ❌ 常见错误

### 错误1: URL验证失败
**原因**: 服务未启动或ngrok未运行  
**解决**: 
```bash
# 检查服务是否运行
curl http://localhost:5000/health

# 重启ngrok
ngrok http 5000
```

### 错误2: Bot不回复
**原因**: Bot未添加到频道或权限不足  
**解决**:
```bash
# 在Slack中邀请Bot
/invite @广告项目经理

# 检查权限
# 确认包含: chat:write, channels:history
```

### 错误3: 环境变量未设置
**原因**: Token或Secret未设置  
**解决**:
```bash
# 检查环境变量
echo $SLACK_BOT_TOKEN
echo $SLACK_SIGNING_SECRET

# 重新设置
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_SIGNING_SECRET="..."
```

---

## 🚀 部署到云服务（可选）

### Render部署（推荐，免费）

```
1. 将代码推送到GitHub
2. 访问 https://render.com/
3. 创建新的 Web Service
4. 连接GitHub仓库
5. 设置环境变量:
   - SLACK_BOT_TOKEN
   - SLACK_SIGNING_SECRET
6. 点击部署
7. 复制生成的URL
8. 更新Slack App的Request URL
```

### Railway部署

```bash
# 安装Railway CLI
npm install -g @railway/cli

# 初始化项目
railway init

# 设置环境变量
railway variables set SLACK_BOT_TOKEN=your-token
railway variables set SLACK_SIGNING_SECRET=your-secret

# 部署
railway up

# 获取URL
railway domain
```

---

## 📊 配置状态跟踪

### 进度
- [ ] Slack App创建完成
- [ ] Bot Token获取成功
- [ ] 权限配置完成
- [ ] 事件订阅配置完成
- [ ] 依赖安装完成
- [ ] 本地服务启动成功
- [ ] ngrok运行正常
- [ ] URL验证通过
- [ ] Slack测试通过
- [ ] 完整流程测试通过

### 完成度
- 当前: 0/10 (0%)
- 目标: 10/10 (100%)

---

## 💡 提示

### 开发提示
1. 使用 `ngrok` 进行本地开发
2. 查看服务日志: `tail -f app.log`
3. 使用Slack的App Directory查看错误

### 安全提示
1. 不要将Token提交到Git
2. 使用 `.env` 文件管理环境变量
3. 定期轮换Bot Token

### 优化提示
1. 使用Redis保存对话历史
2. 实现异步处理提高性能
3. 添加错误重试机制

---

## 🆘 需要帮助？

### 查看日志
```bash
# 查看Flask日志
tail -f app.log

# 查看错误日志
grep ERROR app.log
```

### 重置配置
```bash
# 重新安装依赖
pip install --upgrade slack-sdk flask

# 重启服务
python src/slack_bot/main.py
```

### 联系支持
- 查看完整指南: `docs/SLACK_BOT_GUIDE.md`
- Slack API文档: https://api.slack.com/
- Slack Python SDK: https://slack.dev/python-slack-sdk/

---

## ✅ 配置完成后的下一步

1. **测试功能**
   - 发送文本消息
   - 上传文件
   - 多轮对话

2. **部署到云**
   - 选择Render/Railway
   - 配置环境变量
   - 更新Request URL

3. **集成Agent**
   - 修改`call_agent`函数
   - 对接现有Agent
   - 测试完整流程

4. **添加功能**
   - 富文本消息
   - 按钮交互
   - 文件处理

---

**祝配置顺利！如有问题，请参考完整指南或查看日志。🚀**
