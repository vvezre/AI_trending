"""
Embodied AI news crawler.
"""
from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape
import re
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import requests


DEFAULT_NEWS_SOURCES = [
    {
        "name": "Google News - Embodied AI",
        "url": "https://news.google.com/rss/search?q=%22embodied%20AI%22%20OR%20%22humanoid%20robot%22%20OR%20%22vision-language-action%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "arXiv Robotics",
        "url": "https://export.arxiv.org/rss/cs.RO",
    },
    {
        "name": "IEEE Spectrum Robotics",
        "url": "https://spectrum.ieee.org/rss/robotics/fulltext",
    },
]

DEFAULT_KEYWORDS = [
    "具身智能",
    "机器人",
    "人形机器人",
    "世界模型",
    "embodied ai",
    "embodied intelligence",
    "robotics",
    "humanoid robot",
    "vision-language-action",
    "vla",
    "robot foundation model",
]


class EmbodiedAINewsCrawler:
    """Fetch and normalize embodied AI news from RSS feeds."""

    def __init__(
        self,
        sources: Optional[List[Dict[str, str]]] = None,
        keywords: Optional[Iterable[str]] = None,
        timeout: int = 30,
    ):
        self.sources = sources if sources is not None else DEFAULT_NEWS_SOURCES
        self.keywords = [keyword.strip().lower() for keyword in (keywords or DEFAULT_KEYWORDS) if keyword.strip()]
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/rss+xml,application/xml,text/xml,text/html;q=0.8",
        }

    def fetch_latest(self, limit: int = 25) -> List[Dict]:
        """Fetch, filter, dedupe, and sort news items."""
        items = []
        for source in self.sources:
            try:
                response = requests.get(source["url"], headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                items.extend(self.parse_feed(response.text, source["name"]))
            except requests.RequestException as exc:
                print(f"资讯源抓取失败 [{source['name']}]: {exc}")

        return self.sort_items(items)[:limit]

    def parse_feed(self, xml_text: str, source_name: str) -> List[Dict]:
        """Parse RSS/Atom feed text into normalized news dictionaries."""
        try:
            root = ET.fromstring(xml_text.encode("utf-8"))
        except ET.ParseError as exc:
            print(f"资讯源解析失败 [{source_name}]: {exc}")
            return []

        raw_items = []
        for item in root.findall(".//item"):
            raw_items.append(self._parse_rss_item(item, source_name))
        for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
            raw_items.append(self._parse_atom_entry(entry, source_name))

        filtered = []
        seen = set()
        for item in raw_items:
            if not item["title"] or not item["url"]:
                continue
            matched_keywords = self._matched_keywords(item)
            if not matched_keywords:
                continue
            dedupe_key = self._dedupe_key(item)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            item["matched_keywords"] = matched_keywords
            filtered.append(item)

        return self.sort_items(filtered)

    def sort_items(self, items: List[Dict]) -> List[Dict]:
        """Sort items newest first using RSS/Atom date strings."""
        return sorted(items, key=lambda item: self._parse_datetime(item.get("published_at", "")), reverse=True)

    def _parse_rss_item(self, item, source_name: str) -> Dict:
        title = self._text(item, "title")
        description = self._clean_html(self._text(item, "description"))
        return {
            "title": title,
            "url": self._text(item, "link"),
            "source": source_name,
            "published_at": self._text(item, "pubDate"),
            "summary": description,
            "matched_keywords": [],
        }

    def _parse_atom_entry(self, entry, source_name: str) -> Dict:
        ns = "{http://www.w3.org/2005/Atom}"
        link = ""
        link_node = entry.find(f"{ns}link")
        if link_node is not None:
            link = link_node.attrib.get("href", "")
        return {
            "title": self._text(entry, f"{ns}title"),
            "url": link,
            "source": source_name,
            "published_at": self._text(entry, f"{ns}published") or self._text(entry, f"{ns}updated"),
            "summary": self._clean_html(self._text(entry, f"{ns}summary")),
            "matched_keywords": [],
        }

    def _matched_keywords(self, item: Dict) -> List[str]:
        haystack = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        return [keyword for keyword in self.keywords if keyword in haystack]

    def _dedupe_key(self, item: Dict) -> str:
        title = re.sub(r"\s+", " ", item.get("title", "").strip().lower())
        if title:
            return f"title:{title}"
        parsed = urlparse(item.get("url", ""))
        return f"url:{parsed.netloc}{parsed.path}".lower()

    def _parse_datetime(self, value: str) -> datetime:
        if not value:
            return datetime.min
        try:
            dt = parsedate_to_datetime(value)
            return dt.replace(tzinfo=None)
        except (TypeError, ValueError):
            pass
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return datetime.min

    def _text(self, node, tag: str) -> str:
        child = node.find(tag)
        if child is None or child.text is None:
            return ""
        return child.text.strip()

    def _clean_html(self, value: str) -> str:
        text = re.sub(r"<[^>]+>", " ", value)
        text = unescape(text)
        return re.sub(r"\s+", " ", text).strip()


def parse_sources(raw_sources: str) -> List[Dict[str, str]]:
    """Parse pipe-separated name=url pairs or bare URLs into source dictionaries."""
    sources = []
    for index, part in enumerate(raw_sources.split("|"), 1):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            name, url = part.split("=", 1)
            sources.append({"name": name.strip(), "url": url.strip()})
        else:
            sources.append({"name": f"News Source {index}", "url": part})
    return sources
