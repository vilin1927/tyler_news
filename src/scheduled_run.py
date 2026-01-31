#!/usr/bin/env python3
"""
Scheduled run script for Premier League Content Automation.

This script is designed to be executed by cron for daily automated runs.
It runs the full pipeline and sends results via Telegram.

Cron setup for 8:00 AM UK time:
    # Edit crontab: crontab -e
    # Add this line (adjust path as needed):
    0 8 * * * cd /path/to/project && /path/to/venv/bin/python src/scheduled_run.py >> logs/cron.log 2>&1

For UK timezone handling on servers not in UK:
    # Option 1: Set TZ in cron
    TZ=Europe/London
    0 8 * * * cd /path/to/project && python src/scheduled_run.py

    # Option 2: Use UTC offset (UK is UTC+0 in winter, UTC+1 in summer/BST)
    # Winter (November-March): 0 8 * * *
    # Summer (March-October): 0 7 * * * (to run at 8am BST)
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import config

# Configure logging for cron execution
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "scheduled_run.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def run_scheduled():
    """
    Execute the scheduled pipeline run.

    Sends Telegram notifications for both success and failure.
    """
    start_time = datetime.now()
    logger.info("=" * 50)
    logger.info(f"Starting scheduled run at {start_time.isoformat()}")

    # Validate configuration
    missing = config.validate()
    if missing:
        logger.error(f"Missing configuration: {', '.join(missing)}")
        logger.error("Scheduled run aborted - check .env file")
        return False

    try:
        # Import here to ensure config is loaded
        from main import run_pipeline
        from telegram_bot import send_progress, is_schedule_paused

        # Check if schedule is paused
        if is_schedule_paused():
            logger.info("Scheduled run is PAUSED - skipping execution")
            await send_progress("⏸ Scheduled run skipped (paused)\n\nUse /resume to re-enable.")
            return {"success": True, "skipped": True, "reason": "paused"}

        # Send start notification
        await send_progress("🕐 Scheduled run starting (8:00 AM UK)...")

        # Run the pipeline
        result = await run_pipeline(send_telegram_updates=True)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        if result["success"]:
            logger.info(f"Scheduled run completed successfully in {duration:.1f}s")
            logger.info(f"Topic: {result['topic']}")
            logger.info(f"Score: {result['score']}/10")

            # Send success summary
            await send_progress(
                f"✅ <b>Daily Run Complete!</b>\n\n"
                f"📌 <b>Topic:</b> {result['topic']}\n"
                f"🔥 <b>Score:</b> {result['score']}/10\n"
                f"⏱ <b>Duration:</b> {duration:.1f}s\n\n"
                f"📝 3 scripts added to Google Sheet."
            )
            return True

        else:
            logger.error(f"Scheduled run failed: {result.get('error', 'Unknown error')}")
            await send_progress(
                f"❌ <b>Daily Run Failed</b>\n\n"
                f"Error: {result.get('error', 'Unknown error')}\n\n"
                f"Use /go to retry manually."
            )
            return False

    except Exception as e:
        logger.exception(f"Scheduled run exception: {str(e)}")

        try:
            from telegram_bot import send_error
            await send_error(f"Scheduled run crashed: {str(e)}")
        except Exception:
            pass

        return False


def main():
    """Main entry point for scheduled execution."""
    try:
        success = asyncio.run(run_scheduled())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Scheduled run interrupted")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
