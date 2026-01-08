"""
Premier League Content Automation - Main Entry Point

Orchestrates the full pipeline:
1. Fetch Twitter trends (Apify)
2. Fetch football news (RapidAPI)
3. Process with Gemini AI (filter, score, generate scripts)
4. Save to Google Sheets
5. Send Telegram notifications
"""

import asyncio
import logging
from datetime import datetime

from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_pipeline(send_telegram_updates: bool = True) -> dict:
    """
    Execute the full content automation pipeline.

    Args:
        send_telegram_updates: Whether to send progress updates via Telegram

    Returns:
        dict with results: topic, score, scripts, success status
    """
    # Import modules here to avoid circular imports
    from twitter_trends import fetch_uk_trends
    from news_client import fetch_football_news
    from gemini_processor import (
        merge_and_deduplicate,
        filter_pl_topics,
        score_drama,
        select_top_topic,
        generate_scripts
    )
    from sheets_client import append_result
    from telegram_bot import send_progress

    result = {
        "success": False,
        "topic": None,
        "score": None,
        "scripts": [],
        "error": None,
        "all_scored_topics": [],  # All topics with their scores for summary
        "twitter_count": 0,
        "news_count": 0,
    }

    try:
        # Step 1: Fetch Twitter trends
        if send_telegram_updates:
            await send_progress("Fetching Twitter trends (UK)...")
        logger.info("Fetching Twitter trends...")
        trends = await fetch_uk_trends()
        result["twitter_count"] = len(trends)
        logger.info(f"Found {len(trends)} Twitter trends")

        # Step 2: Fetch football news
        if send_telegram_updates:
            await send_progress("Fetching football news...")
        logger.info("Fetching football news...")
        news = await fetch_football_news()
        result["news_count"] = len(news)
        logger.info(f"Found {len(news)} news articles")

        # Step 3: Merge and deduplicate
        if send_telegram_updates:
            await send_progress("Processing topics...")
        logger.info("Merging and deduplicating...")
        all_topics = merge_and_deduplicate(trends, news)
        logger.info(f"Merged into {len(all_topics)} unique topics")

        # Step 4: Filter for Premier League relevance
        logger.info("Filtering for PL relevance...")
        pl_topics = await filter_pl_topics(all_topics)
        logger.info(f"Found {len(pl_topics)} PL-relevant topics")

        if not pl_topics:
            result["error"] = "No Premier League topics found"
            if send_telegram_updates:
                await send_progress("No PL topics found today. Try again later.")
            return result

        # Step 5: Score drama potential
        logger.info("Scoring drama potential...")
        scored_topics = await score_drama(pl_topics)

        # Sort and store all scored topics for summary
        sorted_topics = sorted(scored_topics, key=lambda x: x.get("score", 0), reverse=True)
        result["all_scored_topics"] = sorted_topics[:10]  # Top 10 for summary

        # Step 6: Select top topic
        top_topic = select_top_topic(scored_topics)
        result["topic"] = top_topic["topic"]
        result["score"] = top_topic["score"]
        logger.info(f"Top topic: {top_topic['topic']} (Score: {top_topic['score']}/10)")

        if send_telegram_updates:
            await send_progress(f"Top drama: \"{top_topic['topic']}\" (Score: {top_topic['score']}/10)")

        # Step 7: Generate scripts
        if send_telegram_updates:
            await send_progress("Generating scripts...")
        logger.info("Generating scripts...")
        scripts = await generate_scripts(top_topic)
        result["scripts"] = scripts
        logger.info(f"Generated {len(scripts)} scripts")

        # Step 8: Save to Google Sheets
        logger.info("Saving to Google Sheets...")

        # Build topics summary for the sheet
        topics_summary_lines = [f"Sources: {result['twitter_count']} Twitter, {result['news_count']} News"]
        topics_summary_lines.append("---")
        for i, t in enumerate(result["all_scored_topics"][:5], 1):
            topics_summary_lines.append(
                f"{i}. [{t.get('score', '?')}/10] {t.get('topic', '')[:60]}"
            )
        topics_summary = "\n".join(topics_summary_lines)

        append_result(
            timestamp=datetime.now().isoformat(),
            topic=top_topic["topic"],
            score=f"{top_topic['score']}/10 - {top_topic.get('score_breakdown', '')}",
            scripts=scripts,
            topics_summary=topics_summary
        )

        # Step 9: Send completion notification
        if send_telegram_updates:
            await send_progress(f"Done! 3 scripts added to Sheet")

        result["success"] = True
        logger.info("Pipeline completed successfully")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        result["error"] = str(e)
        if send_telegram_updates:
            await send_progress(f"Error: {str(e)}")

    return result


def main():
    """Main entry point for running the pipeline directly."""
    # Validate configuration
    missing = config.validate()
    if missing:
        logger.error(f"Missing configuration: {', '.join(missing)}")
        logger.error("Please check your .env file")
        return

    # Run the pipeline
    asyncio.run(run_pipeline(send_telegram_updates=False))


if __name__ == "__main__":
    main()
