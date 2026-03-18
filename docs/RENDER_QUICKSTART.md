# Render快速部署清单

## ⚡ 5步快速部署（10分钟）

### 第1步：创建GitHub仓库（3分钟）

```bash
# 在项目目录执行
git init
git add .
git commit -m "Initial commit - Slack Bot"
git remote add origin https://github.com/your-username/advertising-slack-bot.git
git branch -M main
git push -u origin main
```

**替换 `your-username` 为你的GitHub用户名**

---

### 第2步：访问Render（1分钟）

1. 打开：https://render.com/
2. 点击 "Sign Up"
3. 使用GitHub登录

---

### 第3步：创建Web服务（4分钟）

1. **点击** "New" → "Web Service"
2. **搜索并连接** 仓库：`advertising-slack-bot`
3. **配置服务**：
   - Name: `advertising-slack-bot`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python src/slack_bot/main.py`
4. **添加环境变量**：
   - `SLACK_BOT_TOKEN`: `<你的Slack Bot Token>`
   - `SLACK_SIGNING_SECRET`: `<你的Signing Secret>`
   - `PORT`: `5001`
   - `COZE_WORKSPACE_PATH`: `/opt/render/project`

   > 提示：这些信息可以从Slack App配置页面获取。
5. **选择** Free 计划
6. **点击** "Create Web Service"

---

### 第4步：等待部署（2分钟）

- 查看部署日志
- 等待绿色 "Deploy succeeded"
- 复制生成的URL：`https://advertising-slack-bot.onrender.com`

---

### 第5步：配置Slack（1分钟）

1. **进入** Slack App → Event Subscriptions
2. **输入** Request URL：
   ```
   https://advertising-slack-bot.onrender.com/slack/events
   ```
3. **点击** "Save Changes"
4. **验证** URL（绿色勾号）

---

## ✅ 测试

在Slack中发送：

```
@ai_pm 你好
```

应该收到回复！

---

## 📝 需要替换的信息

- `your-username`: 你的GitHub用户名
- `advertising-slack-bot`: 仓库名称（可以自定义）

---

## 🚀 完成！

你的Slack Bot已经部署到Render并开始运行了！

---

**详细步骤请参考**：`docs/RENDER_DEPLOYMENT_GUIDE.md`
