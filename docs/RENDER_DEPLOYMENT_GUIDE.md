# Render部署指南

## 🚀 快速部署到Render

本指南将帮助你在10分钟内将Slack Bot部署到Render（免费）。

---

## 📋 部署前准备

### 必需资源
- [ ] GitHub账号（免费）
- [ ] Render账号（免费，可用GitHub登录）
- [ ] 代码已准备好（已完成✅）

---

## 📝 部署步骤（10分钟）

### 第1步：创建GitHub仓库（3分钟）

1. **访问GitHub**
   - 打开：https://github.com/
   - 登录你的账号

2. **创建新仓库**
   - 点击右上角 **"+"** → **"New repository"**
   - 仓库名称：`advertising-slack-bot`
   - 选择 **Public** 或 **Private**
   - 不要勾选初始化选项（README、.gitignore）
   - 点击 **"Create repository"**

3. **上传代码**
   在你的本地项目目录执行：

   ```bash
   # 初始化Git仓库
   git init

   # 添加所有文件
   git add .

   # 提交
   git commit -m "Initial commit - Slack Bot"

   # 添加远程仓库
   git remote add origin https://github.com/your-username/advertising-slack-bot.git

   # 推送到GitHub
   git push -u origin main
   ```

### 第2步：注册Render（1分钟）

1. **访问Render**
   - 打开：https://render.com/
   - 点击 **"Sign Up"**

2. **使用GitHub登录**
   - 点击 **"Continue with GitHub"**
   - 授权Render访问你的GitHub

3. **创建团队**
   - 如果是第一次使用，可能需要创建团队
   - 选择 **"Personal"**（个人使用）

### 第3步：创建Web服务（4分钟）

1. **创建新服务**
   - 在Render Dashboard，点击 **"New"** → **"Web Service"**

2. **连接GitHub仓库**
   - 在 "Connect a repository" 部分
   - 搜索你的仓库：`advertising-slack-bot`
   - 点击 **"Connect"**

3. **配置服务**
   ```
   Name: advertising-slack-bot
   Region: Singapore (或离你最近的区域)
   Branch: main
   ```

4. **构建和运行配置**
   ```
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python src/slack_bot/main.py
   ```

5. **设置环境变量**
   点击 **"Advanced"** → **"Add Environment Variable"**，添加：

   ```
   SLACK_BOT_TOKEN=<你的Slack Bot Token>
   SLACK_SIGNING_SECRET=<你的Signing Secret>
   PORT=5001
   COZE_WORKSPACE_PATH=/opt/render/project
   ```

   > 提示：这些信息可以从Slack App配置页面获取，不要提交到代码中。

6. **选择免费计划**
   - Instance Type: **Free**
   - 点击 **"Create Web Service"**

### 第4步：等待部署（2分钟）

1. **查看部署日志**
   - Render会自动开始部署
   - 点击 **"Deploying...** 查看进度
   - 等待2-3分钟

2. **部署成功**
   - 看到绿色的 **"Deploy succeeded"**
   - 复制生成的URL，例如：
   ```
   https://advertising-slack-bot.onrender.com
   ```

### 第5步：配置Slack App（1分钟）

1. **更新Request URL**
   - 回到Slack App页面
   - 进入 **"Event Subscriptions"**
   - 在 **"Request URL"** 输入：
   ```
   https://advertising-slack-bot.onrender.com/slack/events
   ```

2. **保存配置**
   - 点击 **"Save Changes"**
   - Slack会验证URL，成功后显示绿色勾号

---

## ✅ 测试Bot

### 在Slack中测试

1. **邀请Bot到频道**
   ```
   /invite @ai_pm
   ```

2. **发送测试消息**
   ```
   @ai_pm 你好
   ```

3. **预期回复**
   ```
   收到你的消息: 你好

   这是Agent的回复。
   ```

### 或者发送真实任务

```
@ai_pm 请帮我整理这个brief：客户是星巴克，需要设计4张banner，用于微博和微信发布。
```

---

## 🔍 查看日志

### 在Render上查看日志

1. **进入服务页面**
   - 在Render Dashboard
   - 点击你的服务名称

2. **查看日志**
   - 点击 **"Logs"** 标签
   - 实时查看Bot运行日志

3. **查看部署日志**
   - 点击 **"Deployments"** 标签
   - 查看部署历史

---

## 🔄 更新代码

### 更新流程

1. **修改代码**
   - 在本地修改代码

2. **提交到GitHub**
   ```bash
   git add .
   git commit -m "Update bot feature"
   git push
   ```

3. **自动部署**
   - Render会自动检测到更新
   - 自动重新部署
   - 2-3分钟后新版本上线

---

## 💰 成本说明

### Render免费套餐
- ✅ **750小时/月** 的运行时间
- ✅ **512MB RAM**
- ✅ **0.1 CPU**
- ✅ **无限带宽**
- ✅ **完全免费**

### 适合场景
- 小团队使用（10-20人）
- 每天间歇性使用
- 测试和开发

### 如果需要更多资源
- Standard: $7/月（512MB RAM + 0.5 CPU）
- Pro: $25/月（1GB RAM + 1 CPU）

---

## 🔧 故障排查

### 问题1：部署失败

**可能原因**：
- requirements.txt格式错误
- 代码中有语法错误
- 环境变量未设置

**解决方法**：
1. 查看部署日志
2. 检查错误信息
3. 修复问题后重新推送代码

### 问题2：Bot不响应

**可能原因**：
- 服务未启动
- Request URL配置错误
- 环境变量未正确设置

**解决方法**：
1. 检查服务是否在线（绿色状态）
2. 验证Request URL是否正确
3. 检查环境变量是否设置
4. 查看实时日志

### 问题3：URL验证失败

**可能原因**：
- URL格式错误
- 服务未启动
- 网络问题

**解决方法**：
1. 确保URL格式正确：`https://xxx.onrender.com/slack/events`
2. 确保服务状态为"Deploy succeeded"
3. 等待1-2分钟后重试

---

## 🚀 性能优化

### 优化建议

1. **使用Gunicorn（生产环境）**
   ```bash
   # 修改Start Command
   gunicorn src.slack_bot.main:app -w 4 -b 0.0.0.0:5001
   ```

2. **启用日志轮转**
   - 避免日志文件过大
   - 使用logging.handlers.RotatingFileHandler

3. **添加健康检查**
   - Render会定期检查/health端点
   - 确保服务正常运行

---

## 🔐 安全建议

1. **不要提交敏感信息**
   - Token和Secret已配置在环境变量中
   - 不要在代码中硬编码

2. **使用私有仓库**
   - 如果不想公开代码
   - 使用GitHub Private仓库

3. **定期更新依赖**
   - 定期运行 `pip install --upgrade -r requirements.txt`
   - 保持依赖最新版本

---

## 📊 监控和告警

### Render内置监控

1. **资源使用**
   - CPU使用率
   - 内存使用
   - 网络流量

2. **部署历史**
   - 查看所有部署
   - 回滚到历史版本

3. **服务日志**
   - 实时日志
   - 历史日志

---

## 🎯 成功标志

当以下条件都满足时，说明部署成功：

- ✅ Render服务状态为绿色
- ✅ 可以访问 `https://your-app.onrender.com/health`
- ✅ Slack App的Request URL显示绿色勾号
- ✅ 在Slack中可以@机器人对话
- ✅ Bot能正常回复

---

## 📚 相关链接

- [Render文档](https://render.com/docs)
- [Render定价](https://render.com/pricing)
- [GitHub文档](https://docs.github.com/)
- [Slack API文档](https://api.slack.com/)

---

## 🆘 需要帮助？

### 获取帮助

1. **查看Render日志**
2. **查看Slack App配置**
3. **检查代码是否有错误**
4. **参考本文档的故障排查章节**

---

**祝部署顺利！🚀**
