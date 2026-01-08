"""
Gemini AI processor for Premier League content automation.

Handles:
- Merging and deduplicating trends + news
- Filtering for Premier League relevance
- Scoring drama/viral potential
- Generating video scripts in UK football banter style

IMPORTANT: Uses gemini-3-pro-preview model ONLY (mandatory requirement).
"""

import asyncio
import json
import logging
import re
from typing import Optional

import google.generativeai as genai

from config import config

logger = logging.getLogger(__name__)

# Initialize Gemini client
genai.configure(api_key=config.GEMINI_API_KEY)

# MANDATORY: Use gemini-3-pro-preview model only
MODEL_NAME = config.GEMINI_MODEL  # "gemini-3-pro-preview"


def get_model() -> genai.GenerativeModel:
    """Get configured Gemini model instance."""
    return genai.GenerativeModel(MODEL_NAME)


def merge_and_deduplicate(trends: list[dict], news: list[dict]) -> list[dict]:
    """
    Merge Twitter trends and news articles, removing duplicates.

    Args:
        trends: List of Twitter trend dictionaries
        news: List of news article dictionaries

    Returns:
        Combined list of unique topics
    """
    logger.info(f"Merging {len(trends)} trends with {len(news)} news articles...")

    all_topics = []
    seen_topics = set()

    # Add trends first (usually more timely)
    for trend in trends:
        topic_lower = trend.get("topic", "").lower().strip()
        if topic_lower and topic_lower not in seen_topics:
            seen_topics.add(topic_lower)
            all_topics.append({
                "topic": trend.get("topic", ""),
                "tweet_count": trend.get("tweet_count"),
                "source": "twitter",
                "url": trend.get("url", ""),
                "rank": trend.get("rank", 99),
            })

    # Add news articles
    for article in news:
        topic = article.get("topic", "").strip()
        topic_lower = topic.lower()

        # Check for duplicates (exact match or significant overlap)
        is_duplicate = False
        for seen in seen_topics:
            if topic_lower == seen or _is_similar(topic_lower, seen):
                is_duplicate = True
                break

        if not is_duplicate and topic:
            seen_topics.add(topic_lower)
            all_topics.append({
                "topic": topic,
                "summary": article.get("summary", ""),
                "source": article.get("source", "news"),
                "url": article.get("url", ""),
                "published_at": article.get("published_at", ""),
            })

    logger.info(f"Merged into {len(all_topics)} unique topics")
    return all_topics


def _is_similar(text1: str, text2: str, threshold: float = 0.6) -> bool:
    """Check if two texts are similar using simple word overlap."""
    words1 = set(text1.split())
    words2 = set(text2.split())

    if not words1 or not words2:
        return False

    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return (intersection / union) >= threshold if union > 0 else False


async def filter_pl_topics(topics: list[dict]) -> list[dict]:
    """
    Filter topics for Premier League relevance using Gemini.

    Args:
        topics: List of all topic dictionaries

    Returns:
        List of PL-relevant topics only
    """
    if not topics:
        return []

    logger.info(f"Filtering {len(topics)} topics for PL relevance...")

    model = get_model()

    # Prepare topics for the prompt
    topics_text = "\n".join([
        f"{i+1}. {t.get('topic', '')} - {t.get('summary', '')[:100]}"
        for i, t in enumerate(topics[:50])  # Limit to 50 for token efficiency
    ])

    prompt = f"""You are a Premier League football expert. Analyze these topics and identify which ones are SPECIFICALLY about the English Premier League.

Topics to analyze:
{topics_text}

INCLUDE topics about:
- Premier League clubs (Arsenal, Chelsea, Liverpool, Man City, Man United, Tottenham, etc.)
- Premier League players, managers, and staff
- Premier League matches, results, and table standings
- Transfer rumors involving PL clubs
- Manager sackings/appointments at PL clubs
- PL-related controversies and drama

EXCLUDE topics about:
- Other leagues (La Liga, Serie A, Bundesliga, etc.) unless involving PL clubs
- International football (World Cup, Euros) unless directly about PL players
- General sports news not related to Premier League
- Non-football topics

Return ONLY a JSON array of numbers representing the relevant topic indices (1-based).
Example: [1, 3, 7, 12]

If no topics are PL-relevant, return: []"""

    try:
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: model.generate_content(prompt)
        )

        # Parse the response to get indices
        text = response.text.strip()
        # Extract JSON array from response
        match = re.search(r'\[[\d,\s]*\]', text)
        if match:
            indices = json.loads(match.group())
            # Filter to valid indices and get corresponding topics
            pl_topics = [
                topics[i-1] for i in indices
                if 1 <= i <= len(topics)
            ]
            logger.info(f"Found {len(pl_topics)} PL-relevant topics")
            return pl_topics
        else:
            logger.warning("Could not parse PL filter response, returning all topics")
            return topics

    except Exception as e:
        logger.error(f"PL filtering failed: {str(e)}")
        # On error, return all topics and let scoring handle relevance
        return topics


async def score_drama(topics: list[dict]) -> list[dict]:
    """
    Score each topic for drama/viral potential using Gemini.

    Scoring factors:
    - Club size (Big 6 = +3, Mid-table = +1, Lower = 0)
    - Controversy type (Manager sacking = +3, Player drama = +2, Match result = +1)
    - Recency (implied by trend position)
    - Engagement (tweet count, trend rank)

    Args:
        topics: List of PL-relevant topic dictionaries

    Returns:
        List of topics with added 'score' and 'score_breakdown' fields
    """
    if not topics:
        return []

    logger.info(f"Scoring drama potential for {len(topics)} topics...")

    model = get_model()

    topics_text = "\n".join([
        f"{i+1}. {t.get('topic', '')} (Source: {t.get('source', 'unknown')}, Tweets: {t.get('tweet_count', 'N/A')})"
        for i, t in enumerate(topics[:20])  # Limit for token efficiency
    ])

    prompt = f"""You are a viral content expert specializing in Premier League football drama.

Score each topic from 1-10 based on VIRAL POTENTIAL for UK football fans on TikTok/Reels.

Topics to score:
{topics_text}

SCORING CRITERIA:
- Club Size: Big 6 (Arsenal, Chelsea, Liverpool, Man City, Man United, Tottenham) = higher score
- Controversy Level: Manager sacking/drama > Player controversy > Transfer rumors > Match results
- Meme Potential: Topics that can be turned into jokes, banter, or reactions
- Timeliness: Breaking news > Ongoing stories > Old news
- Fan Engagement: Topics that will trigger strong reactions from fans

For each topic, provide:
1. Score (1-10)
2. Brief breakdown explaining the score

Return as JSON array:
[
  {{"index": 1, "score": 8, "breakdown": "Big 6 drama, manager controversy, high meme potential"}},
  {{"index": 2, "score": 5, "breakdown": "Mid-table club, routine transfer, moderate interest"}}
]

Only return the JSON array, no other text."""

    try:
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: model.generate_content(prompt)
        )

        text = response.text.strip()
        # Extract JSON array
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            scores = json.loads(match.group())

            # Apply scores to topics
            for score_item in scores:
                idx = score_item.get("index", 0) - 1
                if 0 <= idx < len(topics):
                    topics[idx]["score"] = score_item.get("score", 5)
                    topics[idx]["score_breakdown"] = score_item.get("breakdown", "")

            # Ensure all topics have a score
            for topic in topics:
                if "score" not in topic:
                    topic["score"] = 5
                    topic["score_breakdown"] = "Default score"

            logger.info("Drama scoring complete")
            return topics
        else:
            logger.warning("Could not parse scoring response")
            # Assign default scores
            for topic in topics:
                topic["score"] = 5
                topic["score_breakdown"] = "Default score (parsing failed)"
            return topics

    except Exception as e:
        logger.error(f"Drama scoring failed: {str(e)}")
        for topic in topics:
            topic["score"] = 5
            topic["score_breakdown"] = f"Default score (error: {str(e)[:50]})"
        return topics


def select_top_topic(scored_topics: list[dict]) -> dict:
    """
    Select the highest-scoring topic.

    Args:
        scored_topics: List of topics with scores

    Returns:
        The top-scoring topic dictionary
    """
    if not scored_topics:
        return {"topic": "No topics available", "score": 0}

    # Sort by score descending
    sorted_topics = sorted(scored_topics, key=lambda x: x.get("score", 0), reverse=True)
    top = sorted_topics[0]

    logger.info(f"Selected top topic: {top.get('topic', '')} (Score: {top.get('score', 0)}/10)")
    return top


async def generate_scripts(topic: dict) -> list[dict]:
    """
    Generate 3 video scripts for the top topic.

    Each script has: Hook, Premise, Punchline
    Written in authentic UK football banter style.

    Args:
        topic: The selected topic dictionary

    Returns:
        List of 3 script dictionaries
    """
    logger.info(f"Generating scripts for: {topic.get('topic', '')}")

    model = get_model()

    prompt = f"""You are a UK football content creator who makes viral TikTok/Reels videos.
Your style is authentic football banter - the way real fans talk in the pub, on Twitter, and in the stands.

Generate 3 SHORT video script ideas for this topic:
TOPIC: {topic.get('topic', '')}
CONTEXT: {topic.get('summary', topic.get('score_breakdown', ''))}
DRAMA SCORE: {topic.get('score', 5)}/10

Each script MUST have:
1. HOOK (first 1-3 seconds) - Grab attention immediately. Use text-on-screen format.
2. PREMISE (main content) - Brief setup, 5-15 seconds of content
3. PUNCHLINE (ending) - Memorable ending, callback, or twist

STYLE REQUIREMENTS:
- Write like a real UK football fan, NOT a corporate AI
- Use banter, rivalry references, self-deprecating humor
- Reference memes, chants, and football culture
- Keep it punchy - these are 15-30 second videos
- Include emojis sparingly where they add to the joke

BAD EXAMPLES (avoid this style):
- "Exciting match results today!"
- "The team showed great determination"
- "Better luck next time!"

GOOD EXAMPLES:
- "Arsenal fans at halftime vs full time"
- "Pep when someone asks about the charges"
- "United fans explaining why THIS is the year"

Return as JSON array:
[
  {{
    "hook": "Text that appears on screen in first 3 seconds",
    "premise": "What happens in the video (describe the content/reaction/comparison)",
    "punchline": "The ending text or final message"
  }},
  ...
]

Generate exactly 3 scripts. Only return the JSON array."""

    try:
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: model.generate_content(prompt)
        )

        text = response.text.strip()
        # Extract JSON array
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            scripts = json.loads(match.group())
            logger.info(f"Generated {len(scripts)} scripts")
            return scripts[:3]  # Ensure max 3 scripts
        else:
            logger.error("Could not parse scripts response")
            return _get_fallback_scripts(topic)

    except Exception as e:
        logger.error(f"Script generation failed: {str(e)}")
        return _get_fallback_scripts(topic)


def _get_fallback_scripts(topic: dict) -> list[dict]:
    """Return fallback scripts if generation fails."""
    topic_name = topic.get("topic", "This topic")
    return [
        {
            "hook": f"POV: You just saw {topic_name[:30]}...",
            "premise": "Show reaction from different fan perspectives",
            "punchline": "The beautiful game innit"
        },
        {
            "hook": "Football Twitter right now:",
            "premise": f"Compilation of reactions to {topic_name[:30]}",
            "punchline": "And they say football is just a game"
        },
        {
            "hook": "Me explaining to my non-football friends:",
            "premise": f"Dramatic retelling of {topic_name[:30]}",
            "punchline": "You wouldn't understand"
        }
    ]


# For testing
if __name__ == "__main__":
    async def test():
        # Test with sample data
        sample_topics = [
            {"topic": "Arsenal lose 2-0 lead against Brighton", "source": "twitter", "tweet_count": 50000},
            {"topic": "Ten Hag sacked by Manchester United", "source": "news", "summary": "Breaking news"},
            {"topic": "Haaland scores hat-trick", "source": "twitter", "tweet_count": 30000},
        ]

        print("Testing PL filter...")
        pl_topics = await filter_pl_topics(sample_topics)
        print(f"PL topics: {len(pl_topics)}")

        print("\nTesting drama scoring...")
        scored = await score_drama(pl_topics)
        for t in scored:
            print(f"  {t['topic']}: {t.get('score', 'N/A')}/10")

        print("\nTesting script generation...")
        top = select_top_topic(scored)
        scripts = await generate_scripts(top)
        for i, s in enumerate(scripts, 1):
            print(f"\nScript {i}:")
            print(f"  HOOK: {s['hook']}")
            print(f"  PREMISE: {s['premise']}")
            print(f"  PUNCHLINE: {s['punchline']}")

    asyncio.run(test())
