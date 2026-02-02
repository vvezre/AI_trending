# GitHub Trending AI 总结助手

自动抓取每日 GitHub Trending 项目，使用 AI 进行智能分析总结，并通过邮件推送。

## 功能特性

- 🚀 自动抓取 GitHub Trending 榜单 (Top 10)
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
```

## 项目结构

```
AI_trending/
├── src/
│   ├── crawler.py          # GitHub数据抓取模块
│   ├── ai_analyzer.py      # AI分析引擎
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

## 部署到 GitHub Actions

详见 `.github/workflows/daily_digest.yml` 配置文件。

## 技术栈

- Python 3.10+
- BeautifulSoup4 (网页解析)
- DeepSeek API (AI分析)
- SMTP (邮件发送)

## License

MIT
