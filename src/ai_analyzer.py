"""
AI 分析引擎模块 - 使用 DeepSeek API
"""
from openai import OpenAI
from typing import List, Dict
import json
import os


class DeepSeekAnalyzer:
    """DeepSeek AI 分析器"""

    def __init__(self, api_key: str, api_base: str = "https://api.deepseek.com"):
        """
        初始化分析器

        Args:
            api_key: DeepSeek API密钥
            api_base: API基础URL
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        self.model = "deepseek-chat"

    def analyze_trending(self, repos: List[Dict]) -> str:
        """
        分析GitHub Trending项目

        Args:
            repos: 项目列表

        Returns:
            分析报告（markdown格式）
        """
        if not repos:
            return "今日暂无趋势项目"

        # 构建项目数据摘要
        repos_summary = self._build_repos_summary(repos)

        # 调用AI进行分析
        prompt = self._build_analysis_prompt(repos_summary)

        try:
            print("正在调用DeepSeek API进行分析...")
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

            analysis = response.choices[0].message.content
            print("AI分析完成！")
            return analysis

        except Exception as e:
            print(f"AI分析失败: {e}")
            return self._generate_fallback_report(repos)

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

    def generate_summary(self, repos: List[Dict], max_repos: int = 25) -> str:
        """
        生成完整的分析报告

        Args:
            repos: 项目列表
            max_repos: 分析的最大项目数

        Returns:
            完整的markdown格式报告
        """
        # 限制分析的项目数量
        repos_to_analyze = repos[:max_repos]

        # 添加报告头部
        header = f"""# 🚀 GitHub Trending 今日观察

> 数据时间: {self._get_current_date()}
> 分析项目数: {len(repos_to_analyze)}

---

"""

        # 生成AI分析
        analysis = self.analyze_trending(repos_to_analyze)

        # 组合完整报告
        full_report = header + analysis

        return full_report

    def _get_current_date(self) -> str:
        """获取当前日期"""
        from datetime import datetime
        return datetime.now().strftime("%Y年%m月%d日")


def test_analyzer():
    """测试AI分析器"""
    # 模拟数据
    mock_repos = [
        {
            "name": "openai / gpt-4",
            "url": "https://github.com/openai/gpt-4",
            "language": "Python",
            "stars": "15000",
            "stars_today": "1500",
            "forks": "2000",
            "description": "GPT-4 API官方Python库"
        },
        {
            "name": "vercel / next.js",
            "url": "https://github.com/vercel/next.js",
            "language": "JavaScript",
            "stars": "120000",
            "stars_today": "800",
            "forks": "25000",
            "description": "React框架，支持SSR和静态生成"
        }
    ]

    # 需要设置环境变量 DEEPSEEK_API_KEY
    api_key = os.getenv("DEEPSEEK_API_KEY", "your-api-key-here")

    if api_key == "your-api-key-here":
        print("请设置环境变量 DEEPSEEK_API_KEY")
        return

    analyzer = DeepSeekAnalyzer(api_key=api_key)
    report = analyzer.generate_summary(mock_repos)
    print(report)


if __name__ == "__main__":
    test_analyzer()
