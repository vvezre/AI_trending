# GitHub Actions 部署指南

本文档介绍如何将项目部署到GitHub Actions，实现零成本自动化运行。

## 前置准备

### 1. 获取 DeepSeek API Key

1. 访问 [DeepSeek 官网](https://platform.deepseek.com/)
2. 注册账号并登录
3. 进入 API Keys 页面生成密钥
4. 复制并保存你的 API Key

### 2. 配置邮箱应用专用密码

#### Gmail 配置
1. 登录 Gmail
2. 进入 [Google 账号设置](https://myaccount.google.com/)
3. 选择"安全性" → "两步验证"（必须先启用）
4. 启用后，选择"应用专用密码"
5. 生成一个新的应用密码（选择"邮件"和"Windows电脑"）
6. 保存生成的16位密码

#### QQ邮箱配置
1. 登录 QQ 邮箱
2. 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
3. 开启 IMAP/SMTP 服务
4. 生成授权码
5. 保存授权码

## 部署步骤

### 1. 创建 GitHub 仓库

```bash
# 在项目目录下初始化 Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: GitHub Trending AI助手"

# 关联远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/AI_trending.git

# 推送到GitHub
git push -u origin main
```

### 2. 配置 GitHub Secrets

进入仓库的 Settings → Secrets and variables → Actions

点击 "New repository secret" 添加以下密钥：

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | `sk-xxxxxxxxxxxxx` |
| `EMAIL_SENDER` | 发件人邮箱 | `your_email@gmail.com` |
| `EMAIL_PASSWORD` | 邮箱应用专用密码 | `abcd efgh ijkl mnop` |
| `EMAIL_RECEIVER` | 收件人邮箱 | `receiver@example.com` |
| `SMTP_SERVER` | SMTP服务器 | `smtp.gmail.com` 或 `smtp.qq.com` |
| `SMTP_PORT` | SMTP端口 | `587` |

### 3. 配置 Variables（可选）

进入 Settings → Secrets and variables → Actions → Variables

添加以下变量：

| Variable 名称 | 说明 | 可选值 |
|--------------|------|--------|
| `TRENDING_LANGUAGE` | 语言过滤 | 留空表示全部，或指定：`python`, `javascript`, `rust` 等 |

### 4. 启用 GitHub Actions

1. 进入仓库的 "Actions" 标签
2. 如果提示启用 Actions，点击启用
3. 查看 "GitHub Trending 每日总结" workflow

### 5. 测试运行

#### 方法1: 手动触发（推荐）
1. 进入 Actions → GitHub Trending 每日总结
2. 点击 "Run workflow"
3. 选择分支并运行
4. 查看运行日志

#### 方法2: 等待定时触发
- 默认每天北京时间上午9点自动运行

## 常见问题

### Q1: Actions运行失败怎么办？

查看运行日志，常见问题：
- API Key 配置错误 → 检查 Secrets
- 邮箱密码错误 → 重新生成应用专用密码
- 网络问题 → GitHub Actions 可能访问某些API受限

### Q2: 如何修改运行时间？

编辑 `.github/workflows/daily_digest.yml` 文件：

```yaml
on:
  schedule:
    - cron: '0 1 * * *'  # UTC时间，对应北京时间+8小时
```

Cron 表达式说明：
- `0 1 * * *` = 每天UTC 1:00 (北京时间 9:00)
- `0 13 * * *` = 每天UTC 13:00 (北京时间 21:00)

### Q3: 如何查看生成的报告？

每次运行后，报告会作为 Artifact 上传：
1. 进入 Actions 运行记录
2. 找到对应的运行
3. 下载 "trending-report" artifact

### Q4: 想在本地测试怎么办？

```bash
# 创建 .env 文件
cp .env.example .env

# 编辑 .env，填写配置

# 安装依赖
pip install -r requirements.txt

# 测试运行（只抓取5个项目）
python main.py --test

# 正式运行（抓取25个项目）
python main.py
```

## 成本说明

- **GitHub Actions**: 公开仓库完全免费，私有仓库每月2000分钟免费额度
- **DeepSeek API**: 按调用量计费，每天运行一次成本极低（约0.01元/天）
- **邮件发送**: 使用个人邮箱SMTP，完全免费

总计：**几乎零成本**（每月约0.3元）

## 进阶优化

1. **HTML邮件**: 修改 `email_sender.py` 使用HTML模板
2. **数据持久化**: 添加SQLite数据库，记录历史趋势
3. **多语言支持**: 配置多个workflow，分别抓取不同语言
4. **Telegram/钉钉推送**: 除了邮件，还可以推送到其他平台

## 故障排查

运行日志关键信息：
- ✓ 表示成功
- ✗ 表示失败
- 查看具体错误信息进行排查

常用命令：
```bash
# 查看最近的报告
ls -lt reports/

# 查看报告内容
cat reports/github_trending_YYYYMMDD.md
```

## 技术支持

遇到问题可以查看：
- GitHub Issues
- 项目 README.md
- DeepSeek API 文档
