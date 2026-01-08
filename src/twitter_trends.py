"""
Twitter client for fetching Premier League tweets using twitterapi.io.

Searches for PL-related tweets and returns the most engaged posts.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta

import requests

from config import config

logger = logging.getLogger(__name__)

# API endpoint
TWITTER_API_URL = "https://api.twitterapi.io/twitter/tweet/advanced_search"

# Search queries for Premier League content (English only)
PL_SEARCH_QUERIES = [
    "Premier League news lang:en",
    "Premier League lang:en",
    "EPL lang:en",
]


def get_headers() -> dict:
    """Get API headers."""
    return {
        "X-API-Key": config.TWITTER_API_KEY,
    }


async def fetch_uk_trends(location: str = "United Kingdom", max_results: int = 40) -> list[dict]:
    """
    Fetch Premier League tweets from Twitter using twitterapi.io.

    Args:
        location: Not used (kept for compatibility)
        max_results: Maximum number of tweets to return

    Returns:
        List of tweet dictionaries sorted by engagement with keys:
        - topic: Tweet text
        - tweet_count: Engagement (likes + retweets)
        - url: URL to the tweet
        - rank: Position based on engagement
    """
    logger.info("Fetching Premier League tweets from Twitter...")

    try:
        tweets = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: _fetch_tweets_sync(max_results)
        )
        return tweets

    except Exception as e:
        logger.error(f"Failed to fetch tweets: {str(e)}")
        return []


def _fetch_tweets_sync(max_results: int) -> list[dict]:
    """Synchronous implementation of tweet fetching."""
    all_tweets = []

    for i, query in enumerate(PL_SEARCH_QUERIES):
        # Rate limit: wait between requests
        if i > 0:
            time.sleep(4)
        try:
            logger.info(f"Searching Twitter for: {query}")

            response = requests.get(
                TWITTER_API_URL,
                params={
                    "queryType": "Latest",
                    "query": query,
                },
                headers=get_headers(),
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            tweets = data.get("tweets", [])
            logger.info(f"Found {len(tweets)} tweets for '{query}'")

            for tweet in tweets:
                # Filter: only tweets from last 3 days
                if not _is_recent(tweet.get("createdAt", ""), days=3):
                    continue

                # Skip replies to focus on original content
                if tweet.get("isReply"):
                    continue

                engagement = (
                    (tweet.get("likeCount") or 0) +
                    (tweet.get("retweetCount") or 0) +
                    (tweet.get("quoteCount") or 0)
                )

                all_tweets.append({
                    "topic": tweet.get("text", "").strip()[:300],
                    "tweet_count": engagement,
                    "url": tweet.get("url") or tweet.get("twitterUrl", ""),
                    "source": "twitter",
                    "user": tweet.get("author", {}).get("userName", ""),
                    "user_name": tweet.get("author", {}).get("name", ""),
                    "likes": tweet.get("likeCount") or 0,
                    "retweets": tweet.get("retweetCount") or 0,
                    "views": tweet.get("viewCount") or 0,
                    "created_at": tweet.get("createdAt", ""),
                    "is_verified": tweet.get("author", {}).get("isBlueVerified", False),
                })

        except Exception as e:
            logger.warning(f"Failed to search for '{query}': {e}")
            continue

    # Remove duplicates by tweet text
    seen = set()
    unique_tweets = []
    for tweet in all_tweets:
        text_key = tweet["topic"][:100].lower()
        if text_key and text_key not in seen:
            seen.add(text_key)
            unique_tweets.append(tweet)

    # Sort by engagement (highest first)
    unique_tweets.sort(key=lambda x: x["tweet_count"], reverse=True)

    # Update ranks
    for i, tweet in enumerate(unique_tweets):
        tweet["rank"] = i + 1

    logger.info(f"Fetched {len(unique_tweets)} unique tweets (sorted by engagement)")
    return unique_tweets[:max_results]


def _is_recent(created_at: str, days: int = 3) -> bool:
    """Check if tweet is from the last N days."""
    if not created_at:
        return True  # Assume recent if no date

    try:
        # Parse Twitter date format: "Thu Jan 08 13:00:25 +0000 2026"
        tweet_time = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
        now = datetime.now(tweet_time.tzinfo)
        return (now - tweet_time) < timedelta(days=days)
    except Exception:
        return True  # Assume recent if parsing fails


async def fetch_twitter_search(query: str, max_results: int = 20) -> list[dict]:
    """
    Search Twitter for specific terms.

    Args:
        query: Search query (e.g., "Arsenal transfer")
        max_results: Maximum results to return

    Returns:
        List of tweet dictionaries
    """
    logger.info(f"Searching Twitter for: {query}")

    try:
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.get(
                TWITTER_API_URL,
                params={"queryType": "Latest", "query": query},
                headers=get_headers(),
                timeout=30
            )
        )
        response.raise_for_status()
        data = response.json()

        results = []
        for tweet in data.get("tweets", [])[:max_results]:
            results.append({
                "text": tweet.get("text", ""),
                "user": tweet.get("author", {}).get("userName", ""),
                "retweets": tweet.get("retweetCount") or 0,
                "likes": tweet.get("likeCount") or 0,
                "created_at": tweet.get("createdAt", ""),
                "url": tweet.get("url", ""),
            })

        return results

    except Exception as e:
        logger.error(f"Failed to search Twitter: {str(e)}")
        return []


# For testing
if __name__ == "__main__":
    async def test():
        tweets = await fetch_uk_trends(max_results=10)
        print(f"Found {len(tweets)} tweets:")
        for t in tweets[:5]:
            print(f"  [{t.get('tweet_count', 0)} eng] @{t.get('user', '?')}: {t['topic'][:60]}...")

    asyncio.run(test())
