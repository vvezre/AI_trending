"""
GitHub Trending 数据抓取模块
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time


class GitHubTrendingCrawler:
    """GitHub Trending 爬虫类"""

    def __init__(self, language: str = "", since: str = "daily"):
        """
        初始化爬虫

        Args:
            language: 编程语言过滤，留空表示所有语言
            since: 时间范围 (daily, weekly, monthly)
        """
        self.base_url = "https://github.com/trending"
        self.language = language
        self.since = since
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

    def get_trending_url(self) -> str:
        """构建Trending页面URL"""
        url = self.base_url
        if self.language:
            url = f"{url}/{self.language}"
        url = f"{url}?since={self.since}"
        return url

    def fetch_trending(self) -> List[Dict]:
        """
        抓取GitHub Trending数据

        Returns:
            项目列表，每个项目包含：name, url, description, language, stars, stars_today, forks
        """
        url = self.get_trending_url()
        print(f"正在抓取: {url}")

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'lxml')
            return self._parse_repositories(soup)

        except requests.RequestException as e:
            print(f"抓取失败: {e}")
            return []

    def _parse_repositories(self, soup: BeautifulSoup) -> List[Dict]:
        """解析仓库列表"""
        repositories = []

        # GitHub Trending 页面的文章列表
        articles = soup.find_all('article', class_='Box-row')

        for article in articles:
            try:
                repo_data = self._parse_single_repo(article)
                if repo_data:
                    repositories.append(repo_data)
            except Exception as e:
                print(f"解析单个项目失败: {e}")
                continue

        print(f"成功抓取 {len(repositories)} 个项目")
        return repositories

    def _parse_single_repo(self, article) -> Optional[Dict]:
        """解析单个仓库信息"""
        import re
        repo_data = {}

        # 项目名称和URL
        h2 = article.find('h2', class_='h3')
        if not h2:
            return None

        link = h2.find('a')
        if not link:
            return None

        repo_data['name'] = link.get('href', '').strip('/').replace('/', ' / ')
        repo_data['url'] = f"https://github.com{link.get('href', '')}"

        # 项目描述
        description_element = article.find('p', class_='col-9')
        repo_data['description'] = description_element.get_text(strip=True) if description_element else "No description"

        # 编程语言
        language_element = article.find('span', attrs={'itemprop': 'programmingLanguage'})
        repo_data['language'] = language_element.get_text(strip=True) if language_element else "Unknown"

        # 获取统计信息div
        stats_div = article.find('div', class_='f6')
        stats_text = stats_div.get_text() if stats_div else ""

        # 提取总星标数（从统计文本中提取第一个数字）
        star_match = re.search(r'([\d,]+)', stats_text)
        repo_data['stars'] = star_match.group(1) if star_match else "0"

        # 提取Fork数（从统计文本中提取第二个数字）
        all_numbers = re.findall(r'([\d,]+)', stats_text)
        repo_data['forks'] = all_numbers[1] if len(all_numbers) > 1 else "0"

        # 今日新增星标（查找"stars today"模式）
        stars_today_match = re.search(r'([\d,]+)\s+stars?\s+today', stats_text)
        repo_data['stars_today'] = stars_today_match.group(1) if stars_today_match else "0"

        return repo_data

    def _parse_number(self, text: str) -> str:
        """解析数字（处理k后缀）"""
        text = text.strip().replace(',', '')
        if 'k' in text.lower():
            try:
                num = float(text.lower().replace('k', ''))
                return str(int(num * 1000))
            except:
                return text
        return text

    def get_top_n(self, n: int = 25) -> List[Dict]:
        """
        获取Top N个项目

        Args:
            n: 获取的项目数量

        Returns:
            项目列表
        """
        repos = self.fetch_trending()
        return repos[:n]


def test_crawler():
    """测试爬虫功能"""
    crawler = GitHubTrendingCrawler(language="", since="daily")
    repos = crawler.get_top_n(10)

    print("\n=== GitHub Trending Top 10 ===\n")
    for i, repo in enumerate(repos, 1):
        print(f"{i}. {repo['name']}")
        print(f"   URL: {repo['url']}")
        print(f"   语言: {repo['language']}")
        print(f"   星标: {repo['stars']} (今日+{repo['stars_today']})")
        print(f"   描述: {repo['description'][:100]}...")
        print()


if __name__ == "__main__":
    test_crawler()
