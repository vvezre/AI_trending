"""
AI 分析引擎模块 - 支持多种 AI 模型
"""
import os
import json
import warnings
from typing import List, Dict, Optional, Any

# 导入 SDK
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        import google.generativeai as genai
except ImportError:
    genai = None


# 定义支持的 API 提供商配置
AI_PROVIDERS = {
    # 兼容 OpenAI SDK 的提供商
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY", # 兼容旧配置
        "api_type": "openai"
    },
    "glm": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash",
        "env_key": "GLM_API_KEY",
        "api_type": "openai"
    },
    "kimi": {
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-8k",
        "env_key": "KIMI_API_KEY",
        "api_type": "openai"
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY",
        "api_type": "openai"
    },
    
    # 使用专用 SDK 的提供商
    "claude": {
        "model": "claude-3-haiku-20240307",
        "env_key": "ANTHROPIC_API_KEY",
        "api_type": "anthropic"
    },
    "gemini": {
        "model": "gemini-1.5-flash",
        "env_key": "GOOGLE_API_KEY",
        "api_type": "gemini"
    }
}


class AIAnalyzer:
    """通用 AI 分析器基类"""

    def __init__(self, provider: str, api_key: str, api_base: Optional[str] = None, model: Optional[str] = None):
        """
        初始化分析器

        Args:
            provider: 提供商名称 (deepseek, glm, kimi, openai, claude, gemini)
            api_key: API 密钥
            api_base: 自定义 API 基础 URL (可选)
            model: 自定义模型名称 (可选)
        """
        self.provider = provider.lower()
        self.api_key = api_key
        
        # 获取提供商默认配置
        config = AI_PROVIDERS.get(self.provider, AI_PROVIDERS["deepseek"])
        
        self.api_base = api_base or config.get("base_url")
        self.model = model or config.get("model")
        self.api_type = config.get("api_type", "openai")
        
        # 初始化客户端
        self.client = self._init_client()

    def _init_client(self) -> Any:
        """初始化对应的 API 客户端"""
        if not self.api_key:
            return None

        if self.api_type == "openai":
            if not OpenAI:
                raise ImportError("OpenAI SDK 未安装，请运行 pip install openai")
            return OpenAI(api_key=self.api_key, base_url=self.api_base)
            
        elif self.api_type == "anthropic":
            if not anthropic:
                raise ImportError("Anthropic SDK 未安装，请运行 pip install anthropic")
            return anthropic.Anthropic(api_key=self.api_key)
            
        elif self.api_type == "gemini":
            if not genai:
                raise ImportError("Google Generative AI SDK 未安装，请运行 pip install google-generativeai")
            genai.configure(api_key=self.api_key)
            return genai.GenerativeModel(self.model)
            
        else:
            raise ValueError(f"不支持的 API 类型: {self.api_type}")

    def analyze_trending(self, repos: List[Dict]) -> str:
        """
        分析 GitHub Trending 项目
        """
        if not repos:
            return "今日暂无趋势项目"

        # 构建项目数据摘要
        repos_summary = self._build_repos_summary(repos)

        # 构建提示词
        prompt = self._build_analysis_prompt(repos_summary)

        try:
            if self.client is None:
                return self._generate_fallback_report(repos)

            print(f"正在调用 {self.provider} ({self.model}) 进行分析...")
            
            if self.api_type == "openai":
                return self._call_openai(prompt)
            elif self.api_type == "anthropic":
                return self._call_claude(prompt)
            elif self.api_type == "gemini":
                return self._call_gemini(prompt)
            else:
                return "错误: 未知的 API 类型"

        except Exception as e:
            print(f"AI分析失败: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_fallback_report(repos)

    def _call_openai(self, prompt: str) -> str:
        """调用 OpenAI 兼容接口"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位资深的技术专家和开源社区观察者，擅长分析技术趋势和项目价值。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content

    def _call_claude(self, prompt: str) -> str:
        """调用 Claude 接口"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.7,
            system="你是一位资深的技术专家和开源社区观察者，擅长分析技术趋势和项目价值。",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text

    def _call_gemini(self, prompt: str) -> str:
        """调用 Gemini 接口"""
        # Gemini 没有 system prompt 参数，直接加在 prompt 前面
        full_prompt = "你是一位资深的技术专家和开源社区观察者，擅长分析技术趋势和项目价值。\n\n" + prompt
        response = self.client.generate_content(full_prompt)
        return response.text

    def _build_repos_summary(self, repos: List[Dict]) -> str:
        """构建项目数据摘要"""
        summary_lines = []

        for i, repo in enumerate(repos, 1):
            summary = f"""
{i}. **{repo['name']}**
   - URL: {repo['url']}
   - 语言: {repo['language']}
   - 星标: {repo['stars']} (今日新增: {repo['stars_today']})
   - Fork: {repo['forks']}
   - 描述: {repo['description']}
"""
            summary_lines.append(summary.strip())

        return "\n\n".join(summary_lines)

    def _build_analysis_prompt(self, repos_summary: str) -> str:
        """构建分析提示词"""
        prompt = f"""
请分析以下GitHub今日Trending项目，并按照以下三个维度进行总结：

## 待分析的项目列表：

{repos_summary}

## 分析要求：

请按照以下格式输出分析报告（使用中文，专业简练）：

### 📊 趋势洞察
- 识别今日的技术热点趋势（例如：AI Agent爆发、前端工具链更新、云原生发展等）
- 分析这些项目反映出的技术方向和开发者关注点
- 用2-3句话总结核心趋势

### 🌟 核心项目精选（Top 10）
对前10个项目进行深度解析，每个项目包括：
- 项目名称和一句话介绍
- 核心价值和创新点
- 适合人群（开发者/架构师/数据科学家等）
- 推荐指数（⭐⭐⭐⭐⭐）

### 🏷️ 分类汇总
将所有项目按技术领域分类（如：AI/机器学习、Web开发、DevOps工具、编程语言、数据库等），每个分类列出相关项目名称。

### 💡 黑马项目
标注出"今日新增星标占比"特别高的项目（如果有的话）

---

请直接输出分析报告，不要有额外的说明。
"""
        return prompt.strip()

    def analyze_news(self, items: List[Dict]) -> str:
        """分析具身智能资讯条目"""
        if not items:
            return "今日暂无具身智能相关资讯"

        news_summary = self._build_news_summary(items)
        prompt = self._build_news_prompt(news_summary)

        try:
            if self.client is None:
                return self._generate_news_fallback_report(items)

            print(f"正在调用 {self.provider} ({self.model}) 分析具身智能资讯...")

            if self.api_type == "openai":
                return self._call_openai(prompt)
            elif self.api_type == "anthropic":
                return self._call_claude(prompt)
            elif self.api_type == "gemini":
                return self._call_gemini(prompt)
            else:
                return "错误: 未知的 API 类型"

        except Exception as e:
            print(f"AI资讯分析失败: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_news_fallback_report(items)

    def _build_news_summary(self, items: List[Dict]) -> str:
        """构建资讯数据摘要"""
        summary_lines = []

        for i, item in enumerate(items, 1):
            keywords = ", ".join(item.get("matched_keywords", [])) or "未标注"
            summary = f"""
{i}. **{item['title']}**
   - 来源: {item.get('source', 'Unknown')}
   - 时间: {item.get('published_at', 'Unknown')}
   - URL: {item['url']}
   - 命中关键词: {keywords}
   - 摘要: {item.get('summary', '')}
"""
            summary_lines.append(summary.strip())

        return "\n\n".join(summary_lines)

    def _build_news_prompt(self, news_summary: str) -> str:
        """构建具身智能资讯分析提示词"""
        prompt = f"""
请分析以下具身智能、机器人和相关 AI 技术资讯，并输出一份中文日报。

## 待分析资讯：

{news_summary}

## 分析要求：

请按照以下格式输出，专业、简练、避免夸大：

### 今日要闻
- 选出最值得关注的 3-5 条资讯
- 每条说明为什么重要

### 技术趋势
- 总结这些资讯体现出的具身智能技术方向
- 重点关注机器人基础模型、VLA、世界模型、仿真到现实迁移、多模态感知与控制

### 公司与产品动态
- 梳理公司、产品、平台或商业化相关信息
- 如果没有明显公司动态，说明暂无明确商业化信号

### 论文与开源项目
- 梳理论文、开源模型、数据集、工具链
- 如果没有相关条目，说明暂无明显论文或开源项目

### 值得继续跟踪
- 给出 3 个后续观察点

---

请直接输出分析报告，不要有额外说明。
"""
        return prompt.strip()

    def _generate_fallback_report(self, repos: List[Dict]) -> str:
        """生成备用报告（当AI调用失败时）"""
        report_lines = [
            "# GitHub Trending 今日总结\n",
            "## 📋 项目列表\n"
        ]

        for i, repo in enumerate(repos, 1):
            report_lines.append(f"### {i}. {repo['name']}")
            report_lines.append(f"- **语言**: {repo['language']}")
            report_lines.append(f"- **星标**: {repo['stars']} (今日+{repo['stars_today']})")
            report_lines.append(f"- **描述**: {repo['description']}")
            report_lines.append(f"- **链接**: {repo['url']}\n")

        return "\n".join(report_lines)

    def _generate_news_fallback_report(self, items: List[Dict]) -> str:
        """生成资讯备用报告（当AI调用失败时）"""
        report_lines = [
            "# 具身智能最新资讯\n",
            "## 资讯列表\n"
        ]

        for i, item in enumerate(items, 1):
            keywords = ", ".join(item.get("matched_keywords", [])) or "未标注"
            report_lines.append(f"### {i}. {item['title']}")
            report_lines.append(f"- **来源**: {item.get('source', 'Unknown')}")
            report_lines.append(f"- **时间**: {item.get('published_at', 'Unknown')}")
            report_lines.append(f"- **关键词**: {keywords}")
            report_lines.append(f"- **摘要**: {item.get('summary', '')}")
            report_lines.append(f"- **链接**: {item['url']}\n")

        return "\n".join(report_lines)

    def generate_summary(self, repos: List[Dict], max_repos: int = 25) -> str:
        """生成完整的分析报告"""
        repos_to_analyze = repos[:max_repos]

        header = f"""# 🚀 GitHub Trending 今日观察

> 数据时间: {self._get_current_date()}
> AI 模型: {self.provider} ({self.model})
> 分析项目数: {len(repos_to_analyze)}

---

"""
        analysis = self.analyze_trending(repos_to_analyze)
        return header + analysis

    def generate_news_summary(self, items: List[Dict], max_items: int = 25) -> str:
        """生成具身智能资讯分析报告"""
        items_to_analyze = items[:max_items]

        header = f"""# 具身智能最新资讯

> 数据时间: {self._get_current_date()}
> AI 模型: {self.provider} ({self.model})
> 分析资讯数: {len(items_to_analyze)}

---

"""
        analysis = self.analyze_news(items_to_analyze)
        return header + analysis

    def _get_current_date(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y年%m月%d日")


def create_analyzer(provider: str, api_key: str, api_base: Optional[str] = None):
    """工厂函数"""
    return AIAnalyzer(provider, api_key, api_base)


def test_analyzer():
    """测试函数"""
    print("支持的提供商:", list(AI_PROVIDERS.keys()))
    
    # 简单的 mock 测试
    mock_repos = [{"name": "test/repo", "url": "https://github.com/options", "language": "Python", "stars": "100", "stars_today": "10", "forks": "5", "description": "Test repo"}]
    
    # 模拟初始化（不实际调用）
    try:
        analyzer = AIAnalyzer("deepseek", "test_key")
        print(f"初始化成功: {analyzer.provider} - {analyzer.model}")
    except Exception as e:
        print(f"初始化失败: {e}")

if __name__ == "__main__":
    test_analyzer()
