# 快速上手指南

## 5分钟本地测试

### 步骤 1: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 2: 配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写以下必需配置：

```ini
# DeepSeek API（必需）
DEEPSEEK_API_KEY=sk-your-api-key-here

# 邮箱配置（必需）
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECEIVER=receiver@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 步骤 3: 测试运行

```bash
# 测试模式（只抓取5个项目，不发邮件）
python main.py --test --no-email
```

如果看到类似输出，说明运行成功：

```
============================================================
GitHub Trending AI 总结助手
============================================================

[1/3] 抓取GitHub Trending数据...
正在抓取: https://github.com/trending?since=daily
成功抓取 5 个项目

[2/3] 调用DeepSeek AI进行分析...
正在调用DeepSeek API进行分析...
AI分析完成

[3/3] 跳过邮件发送

✓ 任务完成！报告已保存到本地
报告已保存: reports/github_trending_20260201.md
```

### 步骤 4: 查看生成的报告

```bash
# Windows
type reports\github_trending_20260201.md

# Linux/Mac
cat reports/github_trending_20260201.md
```

## 完整运行（包含邮件发送）

```bash
# 正式运行，抓取25个项目并发送邮件
python main.py
```

## 命令行参数

```bash
# 指定抓取数量
python main.py -n 10

# 不发送邮件
python main.py --no-email

# 测试模式
python main.py --test

# 查看帮助
python main.py --help
```

## 常见问题

### DeepSeek API Key 在哪里获取？

1. 访问 https://platform.deepseek.com/
2. 注册并登录
3. 进入 API Keys 页面
4. 创建新的 API Key

新用户一般有免费额度！

### Gmail 应用专用密码怎么生成？

1. 访问 https://myaccount.google.com/
2. 安全性 → 两步验证（必须先启用）
3. 应用专用密码
4. 选择"邮件"和"Windows电脑"
5. 生成并复制16位密码

### 我想只看Python项目怎么办？

编辑 `.env` 文件，添加：

```ini
TRENDING_LANGUAGE=python
```

支持的语言：`python`, `javascript`, `rust`, `go`, `java`, `typescript` 等

### 如何部署到GitHub Actions自动运行？

详见 [DEPLOYMENT.md](DEPLOYMENT.md) 部署指南。

## 下一步

- [ ] 本地测试成功后，部署到GitHub Actions
- [ ] 配置定时任务，每天自动接收报告
- [ ] 自定义AI分析的维度和风格
- [ ] 升级为HTML邮件格式

享受你的 GitHub Trending 每日总结吧！🎉
