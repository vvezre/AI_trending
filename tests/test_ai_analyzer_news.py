import unittest

from src.ai_analyzer import AIAnalyzer


class NewsAnalyzer(AIAnalyzer):
    def __init__(self):
        self.provider = "test"
        self.model = "test-model"
        self.api_type = "test"
        self.api_key = "test-key"
        self.api_base = None
        self.client = None
        self.last_prompt = ""

    def analyze_news(self, items):
        self.last_prompt = self._build_news_prompt(self._build_news_summary(items))
        return "### 今日要闻\n- 具身智能新闻摘要"


class AIAnalyzerNewsTest(unittest.TestCase):
    def test_generate_news_summary_includes_news_metadata_and_analysis(self):
        analyzer = NewsAnalyzer()
        items = [
            {
                "title": "Humanoid robot learns dexterous manipulation",
                "url": "https://example.com/robot",
                "source": "Example Robotics",
                "published_at": "Mon, 08 Jun 2026 08:00:00 GMT",
                "summary": "Embodied AI model improves household tasks.",
                "matched_keywords": ["embodied ai", "humanoid robot"],
            }
        ]

        report = analyzer.generate_news_summary(items, max_items=10)

        self.assertIn("具身智能最新资讯", report)
        self.assertIn("分析资讯数: 1", report)
        self.assertIn("今日要闻", report)
        self.assertIn("Humanoid robot learns dexterous manipulation", analyzer.last_prompt)
        self.assertIn("Example Robotics", analyzer.last_prompt)
        self.assertIn("embodied ai, humanoid robot", analyzer.last_prompt)

    def test_generate_news_fallback_report_lists_items_when_ai_fails(self):
        analyzer = NewsAnalyzer()
        items = [
            {
                "title": "VLA model powers warehouse robots",
                "url": "https://example.com/vla",
                "source": "Warehouse AI",
                "published_at": "Mon, 08 Jun 2026 08:00:00 GMT",
                "summary": "Vision-language-action model ships in production robots.",
                "matched_keywords": ["vla"],
            }
        ]

        report = analyzer._generate_news_fallback_report(items)

        self.assertIn("VLA model powers warehouse robots", report)
        self.assertIn("Warehouse AI", report)
        self.assertIn("https://example.com/vla", report)


if __name__ == "__main__":
    unittest.main()
