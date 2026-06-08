import unittest

from src.news_crawler import EmbodiedAINewsCrawler


RSS_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Sample News</title>
    <item>
      <title>Humanoid robot learns a new vision-language-action policy</title>
      <link>https://example.com/robot-vla</link>
      <description>Embodied AI systems are getting better at manipulation.</description>
      <pubDate>Mon, 08 Jun 2026 08:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Cloud database startup raises funding</title>
      <link>https://example.com/database</link>
      <description>Database infrastructure news.</description>
      <pubDate>Mon, 08 Jun 2026 07:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Humanoid robot learns a new vision-language-action policy</title>
      <link>https://example.com/robot-vla?utm=copy</link>
      <description>Duplicate title should be removed.</description>
      <pubDate>Mon, 08 Jun 2026 09:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""


class EmbodiedAINewsCrawlerTest(unittest.TestCase):
    def test_parse_feed_filters_embodied_ai_items_and_deduplicates_titles(self):
        crawler = EmbodiedAINewsCrawler(
            sources=[],
            keywords=["embodied ai", "humanoid robot", "vision-language-action"],
        )

        items = crawler.parse_feed(RSS_SAMPLE, "Sample News")

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Humanoid robot learns a new vision-language-action policy")
        self.assertEqual(items[0]["source"], "Sample News")
        self.assertEqual(items[0]["url"], "https://example.com/robot-vla")
        self.assertIn("humanoid robot", items[0]["matched_keywords"])
        self.assertIn("vision-language-action", items[0]["matched_keywords"])

    def test_sort_items_orders_newest_first(self):
        crawler = EmbodiedAINewsCrawler(sources=[], keywords=["robot"])
        items = [
            {"title": "Older robot news", "published_at": "Mon, 08 Jun 2026 07:00:00 GMT"},
            {"title": "Newer robot news", "published_at": "Mon, 08 Jun 2026 09:00:00 GMT"},
        ]

        sorted_items = crawler.sort_items(items)

        self.assertEqual([item["title"] for item in sorted_items], ["Newer robot news", "Older robot news"])


if __name__ == "__main__":
    unittest.main()
