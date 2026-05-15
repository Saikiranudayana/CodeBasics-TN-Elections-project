"""agent/tools.py — Tavily search tool wrapper for the AI agent."""

import os
import re
from typing import Optional

try:
    from tavily import TavilyClient
    _tavily_available = True
except ImportError:
    _tavily_available = False

_client: Optional[object] = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("TAVILY_API_KEY", "")
        if not api_key:
            raise ValueError(
                "TAVILY_API_KEY environment variable is not set. "
                "Please add it to your .env file."
            )
        if not _tavily_available:
            raise ImportError("tavily-python is not installed. Run: pip install tavily-python")
        _client = TavilyClient(api_key=api_key)
    return _client


TRUSTED_DOMAINS = [
    "thehindu.com",
    "indianexpress.com",
    "ndtv.com",
    "thewire.in",
    "scroll.in",
    "deccanherald.com",
    "ani-news.com",
    "pib.gov.in",
    "youtube.com",
]


def search_news(query: str, max_results: int = 5) -> list[dict]:
    """Search for news articles related to the query."""
    client = _get_client()
    response = client.search(
        query=query,
        search_depth="advanced",
        include_domains=TRUSTED_DOMAINS,
        max_results=max_results,
    )
    results = []
    for r in response.get("results", []):
        results.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", "")[:500],
            "published_date": r.get("published_date", ""),
            "source": r.get("url", "").split("/")[2] if "/" in r.get("url", "") else "",
        })
    return results


def _extract_youtube_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from a URL."""
    patterns = [
        r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def search_youtube(query: str, max_results: int = 3) -> list[dict]:
    """Search for YouTube videos related to the query."""
    client = _get_client()
    response = client.search(
        query=f"{query} site:youtube.com",
        search_depth="basic",
        max_results=max_results,
    )
    results = []
    for r in response.get("results", []):
        url = r.get("url", "")
        video_id = _extract_youtube_video_id(url)
        thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id else None
        results.append({
            "title": r.get("title", ""),
            "url": url,
            "video_id": video_id,
            "thumbnail_url": thumbnail,
        })
    return results


def get_context_for_alert(alert) -> dict:
    """Fetch news and videos for a given DrasticAlert."""
    news = search_news(alert.search_query, max_results=6)
    videos = search_youtube(alert.search_query, max_results=3)
    return {"alert": alert, "news": news, "videos": videos}
