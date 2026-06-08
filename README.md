# GitHub Trending AI 总结助手

自动抓取每日 GitHub Trending 项目或具身智能最新资讯，使用 AI 进行智能分析总结，并通过邮件推送。

## 功能特性

- 🚀 自动抓取 GitHub Trending 榜单 (Top 10)
- 🤖 抓取具身智能、机器人、人形机器人、VLA 等相关最新资讯
- 🤖 多模型 AI 支持 (DeepSeek/GPT/Claude/Gemini/GLM/Kimi)
- 📊 每日技术热点趋势深度分析
- 📧 邮件自动推送
- 💰 零成本运行（基于 GitHub Actions）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

需要配置：
- `AI_PROVIDER`: 选择 AI 提供商 (如 `deepseek`, `openai`, `glm` 等)
- `AI_API_KEY`: 对应的 API 密钥
- `EMAIL_SENDER`: 发件人邮箱
- `EMAIL_PASSWORD`: 邮箱应用专用密码
- `EMAIL_RECEIVER`: 收件人邮箱

### 3. 运行程序

```bash
# 使用默认配置
python main.py

# 指定 AI 提供商 (例如使用 Kimi)
python main.py -p kimi

# 测试模式 (抓取 Top 10，不发邮件)
python main.py --test --no-email

# 具身智能资讯模式
python main.py --mode embodied-news --test --no-email
```

## 项目结构

```
AI_trending/
├── src/
│   ├── crawler.py          # GitHub数据抓取模块
│   ├── ai_analyzer.py      # AI分析引擎
│   ├── news_crawler.py     # 具身智能资讯抓取模块
│   └── email_sender.py     # 邮件推送模块
├── main.py                 # 主程序入口
├── requirements.txt        # 项目依赖
├── .env.example           # 环境变量示例
├── .env                   # 环境变量配置（需自行创建）
└── README.md              # 项目说明
```

## AI 分析维度

1. **趋势洞察**: 识别今日技术热点趋势
2. **核心项目精选**: Top 5 项目深度解析
3. **分类汇总**: 按 AI/Web/工具等分类整理

## 具身智能资讯模式

运行：

```bash
python main.py --mode embodied-news --no-email
```

默认会从 Google News、arXiv Robotics、IEEE Spectrum Robotics 等 RSS 源抓取资讯，并按关键词过滤：

- 中文：具身智能、机器人、人形机器人、世界模型
- 英文：embodied AI、robotics、humanoid robot、vision-language-action、VLA、robot foundation model

可以通过 `.env` 自定义：

```ini
NEWS_SOURCES=Google News=https://news.google.com/rss/search?q=%22embodied%20AI%22|arXiv Robotics=https://export.arxiv.org/rss/cs.RO
NEWS_KEYWORDS=具身智能,人形机器人,embodied ai,humanoid robot,VLA
```

## 部署到 GitHub Actions

详见 `.github/workflows/daily_digest.yml` 配置文件。

具身智能资讯日报可使用 `.github/workflows/embodied_news_digest.yml`，支持手动触发和每日北京时间 8 点定时运行。

## 技术栈

- Python 3.10+
- BeautifulSoup4 (网页解析)
- DeepSeek API (AI分析)
- SMTP (邮件发送)

## License

MIT
