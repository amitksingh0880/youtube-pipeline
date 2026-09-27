"""
Trend Scout: discovers breakout viral hooks and topics across YouTube and Google Trends.
Completely free, no paid scrapers required.
"""

import random
import xml.etree.ElementTree as ET
import requests
from typing import List, Optional
from src.core.config import settings


class TrendScout:
    def __init__(self, youtube_api_key: Optional[str] = None):
        self.youtube_api_key = youtube_api_key

    def fetch_google_trends(self, geo: str = "US") -> List[str]:
        """
        Fetches real-time breakout queries from Google Trends RSS feed.
        100% free, no API key required.
        """
        url = f"https://trends.google.com/trending/rss?geo={geo}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if not resp.ok:
                return []
            root = ET.fromstring(resp.content)
            trends = []
            for item in root.findall(".//item"):
                title_elem = item.find("title")
                if title_elem is not None and title_elem.text:
                    trends.append(title_elem.text.strip())
            return trends
        except Exception:
            return []

    def fetch_youtube_trending(self, query: str, max_results: int = 5) -> List[str]:
        """
        Queries YouTube Data API v3 for top-performing Shorts in the niche.
        Uses free read-only key if provided.
        """
        if not self.youtube_api_key:
            return []

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": f"{query} shorts",
            "type": "video",
            "videoDuration": "short",
            "order": "viewCount",
            "maxResults": max_results,
            "key": self.youtube_api_key,
        }
        try:
            resp = requests.get(url, params=params, timeout=15)
            if not resp.ok:
                return []
            items = resp.json().get("items", [])
            return [it["snippet"]["title"] for it in items if "snippet" in it]
        except Exception:
            return []

    def get_seed_query(self, niche: dict) -> str:
        """Picks a random seed query from the niche's catalog."""
        seeds = niche.get("seed_queries", [])
        if seeds:
            return random.choice(seeds)
        return niche.get("name", "interesting facts")
