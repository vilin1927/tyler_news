"""
Football news client using RapidAPI.

Fetches Premier League news from various sources via RapidAPI.
Recommended APIs (free tier available):
- "football-news-aggregator" - Aggregates from Goal, ESPN, OneFootball
- "football-news1" - Alternative news aggregator
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

import requests

from config import config

logger = logging.getLogger(__name__)

# RapidAPI endpoints - using football news aggregator
RAPIDAPI_HOST = "football-news-aggregator-live.p.rapidapi.com"
RAPIDAPI_BASE_URL = f"https://{RAPIDAPI_HOST}"

# Alternative API if primary fails
ALT_RAPIDAPI_HOST = "football-news1.p.rapidapi.com"
ALT_RAPIDAPI_BASE_URL = f"https://{ALT_RAPIDAPI_HOST}"


def get_headers(host: str = RAPIDAPI_HOST) -> dict:
    """Get RapidAPI headers with authentication."""
    return {
        "X-RapidAPI-Key": config.RAPIDAPI_KEY,
        "X-RapidAPI-Host": host,
    }


async def fetch_football_news(max_results: int = 30) -> list[dict]:
    """
    Fetch recent Premier League football news.

    Args:
        max_results: Maximum number of articles to return

    Returns:
        List of news article dictionaries with keys:
        - topic: Article headline/title
        - summary: Brief description
        - source: News source (Goal, ESPN, etc.)
        - url: Link to article
        - published_at: Publication timestamp
    """
    logger.info("Fetching football news from RapidAPI...")

    try:
        # Run in thread pool since requests is synchronous
        news = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: _fetch_news_sync(max_results)
        )
        return news

    except Exception as e:
        logger.error(f"Failed to fetch football news: {str(e)}")
        # Try alternative API
        try:
            logger.info("Trying alternative news API...")
            news = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: _fetch_news_alt_sync(max_results)
            )
            return news
        except Exception as e2:
            logger.error(f"Alternative API also failed: {str(e2)}")
            return []


def _fetch_news_sync(max_results: int) -> list[dict]:
    """
    Synchronous implementation for primary news API.

    Uses football-news-aggregator on RapidAPI.
    """
    news = []

    # Check if RAPIDAPI_KEY is configured
    if not get_headers().get("X-RapidAPI-Key"):
        logger.warning("RAPIDAPI_KEY not configured - skipping news fetch")
        return []

    # Fetch Premier League specific news
    endpoints = [
        "/news/fourfourtwo/epl",
    ]

    for endpoint in endpoints:
        try:
            logger.info(f"Fetching news from {RAPIDAPI_BASE_URL}{endpoint}")
            response = requests.get(
                f"{RAPIDAPI_BASE_URL}{endpoint}",
                headers=get_headers(),
                timeout=30
            )
            logger.info(f"News API response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            logger.info(f"News API returned {len(data) if isinstance(data, list) else 'dict'} items")

            # Parse response - format may vary by API
            articles = data if isinstance(data, list) else data.get("data", data.get("articles", data.get("news", [])))

            for article in articles:
                news_item = _parse_article(article)
                if news_item and news_item["topic"]:
                    news.append(news_item)

        except Exception as e:
            logger.warning(f"Failed to fetch from {endpoint}: {str(e)}")
            continue

    # Remove duplicates by title
    seen_titles = set()
    unique_news = []
    for item in news:
        title_lower = item["topic"].lower()
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_news.append(item)

    logger.info(f"Fetched {len(unique_news)} unique news articles")
    return unique_news[:max_results]


def _fetch_news_alt_sync(max_results: int) -> list[dict]:
    """
    Synchronous implementation for alternative news API.

    Fallback if primary API fails.
    """
    news = []

    try:
        response = requests.get(
            f"{ALT_RAPIDAPI_BASE_URL}/news/premierleague",
            headers=get_headers(ALT_RAPIDAPI_HOST),
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        articles = data if isinstance(data, list) else data.get("result", [])

        for article in articles:
            news_item = _parse_article(article)
            if news_item and news_item["topic"]:
                news.append(news_item)

    except Exception as e:
        logger.error(f"Alternative API request failed: {str(e)}")

    return news[:max_results]


def _parse_article(article: dict) -> Optional[dict]:
    """
    Parse article data from various API formats.

    Handles different response formats from different APIs.
    """
    if not article:
        return None

    # Try various field names used by different APIs
    title = (
        article.get("title") or
        article.get("headline") or
        article.get("name") or
        ""
    )

    summary = (
        article.get("summary") or
        article.get("description") or
        article.get("excerpt") or
        article.get("content", "")[:200]
    )

    source = (
        article.get("source") or
        article.get("provider") or
        article.get("sourceName") or
        "Unknown"
    )

    url = (
        article.get("url") or
        article.get("link") or
        article.get("originalUrl") or
        ""
    )

    published = (
        article.get("publishedAt") or
        article.get("published_at") or
        article.get("date") or
        article.get("timestamp") or
        ""
    )

    return {
        "topic": title.strip(),
        "summary": summary.strip() if summary else "",
        "source": source,
        "url": url,
        "published_at": published,
        "type": "news"
    }


def is_recent(published_at: str, hours: int = 24) -> bool:
    """
    Check if an article was published within the specified hours.

    Args:
        published_at: ISO timestamp string
        hours: Number of hours to consider "recent"

    Returns:
        True if article is recent, False otherwise
    """
    if not published_at:
        return True  # Assume recent if no timestamp

    try:
        # Try parsing ISO format
        pub_time = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        now = datetime.now(pub_time.tzinfo) if pub_time.tzinfo else datetime.now()
        return (now - pub_time) < timedelta(hours=hours)
    except Exception:
        return True  # Assume recent if parsing fails


# For testing
if __name__ == "__main__":
    async def test():
        news = await fetch_football_news()
        print(f"Found {len(news)} news articles:")
        for article in news[:5]:
            print(f"  - [{article['source']}] {article['topic'][:60]}...")

    asyncio.run(test())
