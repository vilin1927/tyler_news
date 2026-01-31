"""
Telegram Bot interface for Premier League Content Automation.

Commands:
- /start - Welcome message and auto-register for updates
- /go - Trigger the content pipeline manually
- /status - Check bot status and schedule state
- /recent - Show recent generated topics
- /pause - Pause daily scheduled runs (8 AM cron)
- /resume - Resume daily scheduled runs

The bot sends progress updates during pipeline execution.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import config

logger = logging.getLogger(__name__)

# File to store registered chat IDs
CHATS_FILE = Path(__file__).parent.parent / "registered_chats.json"

# File to store schedule state (pause/resume)
SCHEDULE_STATE_FILE = Path(__file__).parent.parent / "schedule_state.json"


def load_registered_chats() -> set[str]:
    """Load registered chat IDs from file."""
    try:
        if CHATS_FILE.exists():
            with open(CHATS_FILE, "r") as f:
                return set(json.load(f))
    except Exception as e:
        logger.error(f"Failed to load registered chats: {e}")
    return set()


def save_registered_chats(chats: set[str]) -> None:
    """Save registered chat IDs to file."""
    try:
        with open(CHATS_FILE, "w") as f:
            json.dump(list(chats), f)
        logger.info(f"Saved {len(chats)} registered chats")
    except Exception as e:
        logger.error(f"Failed to save registered chats: {e}")


def register_chat(chat_id: str) -> bool:
    """Register a new chat ID. Returns True if newly registered."""
    chats = load_registered_chats()
    if chat_id not in chats:
        chats.add(chat_id)
        save_registered_chats(chats)
        logger.info(f"Registered new chat: {chat_id}")
        return True
    return False


def load_schedule_state() -> dict:
    """Load schedule state from file."""
    try:
        if SCHEDULE_STATE_FILE.exists():
            with open(SCHEDULE_STATE_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load schedule state: {e}")
    return {"paused": False, "paused_by": None, "paused_at": None}


def save_schedule_state(state: dict) -> None:
    """Save schedule state to file."""
    try:
        with open(SCHEDULE_STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
        logger.info(f"Saved schedule state: paused={state.get('paused')}")
    except Exception as e:
        logger.error(f"Failed to save schedule state: {e}")


def is_schedule_paused() -> bool:
    """Check if scheduled runs are paused."""
    return load_schedule_state().get("paused", False)


# Global application instance
_app: Optional[Application] = None
_bot_instance = None


async def get_bot():
    """Get the bot instance for sending messages."""
    global _bot_instance
    if _bot_instance is None:
        from telegram import Bot
        _bot_instance = Bot(token=config.TELEGRAM_BOT_TOKEN)
    return _bot_instance


async def send_progress(message: str, chat_id: Optional[str] = None) -> bool:
    """
    Send a progress update message to all registered chats.

    Args:
        message: The message to send
        chat_id: Optional specific chat ID (if None, sends to all registered)

    Returns:
        True if sent to at least one chat successfully, False otherwise
    """
    bot = await get_bot()
    success = False

    # Get target chats
    if chat_id:
        target_chats = [chat_id]
    else:
        # Send to all registered chats + configured chat ID
        target_chats = list(load_registered_chats())
        if config.TELEGRAM_CHAT_ID and config.TELEGRAM_CHAT_ID not in target_chats:
            target_chats.append(config.TELEGRAM_CHAT_ID)

    if not target_chats:
        logger.warning("No chat IDs configured for progress messages")
        return False

    for target in target_chats:
        try:
            await bot.send_message(
                chat_id=target,
                text=message,
                parse_mode="HTML"
            )
            success = True
        except Exception as e:
            logger.error(f"Failed to send to chat {target}: {str(e)}")

    return success


async def send_error(error_message: str, chat_id: Optional[str] = None) -> bool:
    """Send an error notification."""
    return await send_progress(f"❌ Error: {error_message}", chat_id)


async def cmd_go(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /go command - trigger the content pipeline.

    This is the main command Tyler will use to generate content ideas.
    """
    chat_id = str(update.effective_chat.id)
    logger.info(f"/go command received from chat {chat_id}")

    await update.message.reply_text("⏳ Starting content pipeline...")

    try:
        # Import here to avoid circular imports
        from main import run_pipeline

        # Run the pipeline with Telegram updates
        result = await run_pipeline(send_telegram_updates=True)

        if result["success"]:
            # Build topics considered summary
            topics_list = ""
            all_topics = result.get("all_scored_topics", [])
            if all_topics:
                for i, t in enumerate(all_topics[:5], 1):
                    marker = "→" if i == 1 else " "
                    topics_list += f"\n{marker} {i}. [{t.get('score', '?')}/10] {t.get('topic', '')[:50]}"

            # Send summary
            summary = (
                f"✅ <b>Pipeline Complete!</b>\n\n"
                f"<b>Sources:</b> {result.get('twitter_count', 0)} Twitter, {result.get('news_count', 0)} News\n\n"
                f"<b>Topics Ranked:</b>{topics_list}\n\n"
                f"📌 <b>Winner:</b> {result['topic'][:60]}\n"
                f"🔥 <b>Score:</b> {result['score']}/10\n\n"
                f"📝 3 scripts have been added to your Google Sheet."
            )
            await update.message.reply_text(summary, parse_mode="HTML")
        else:
            await update.message.reply_text(
                f"❌ Pipeline failed: {result.get('error', 'Unknown error')}"
            )

    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command - check bot status."""
    state = load_schedule_state()
    schedule_status = "⏸ PAUSED" if state.get("paused") else "▶️ Active"

    status_msg = f"✅ <b>Bot is running!</b>\n\n"
    status_msg += f"<b>Schedule:</b> {schedule_status}\n"

    if state.get("paused"):
        status_msg += f"Paused at: {state.get('paused_at', 'Unknown')}\n"

    status_msg += (
        f"\n<b>Commands:</b>\n"
        f"/go - Generate content ideas\n"
        f"/recent - Show recent topics\n"
        f"/status - Check bot status\n"
        f"/pause - Pause daily runs\n"
        f"/resume - Resume daily runs"
    )

    await update.message.reply_text(status_msg, parse_mode="HTML")


async def cmd_recent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /recent command - show recent generated topics."""
    try:
        from sheets_client import get_recent_entries

        entries = get_recent_entries(5)

        if not entries:
            await update.message.reply_text("No recent entries found.")
            return

        message = "📋 <b>Recent Topics:</b>\n\n"
        for i, entry in enumerate(entries, 1):
            message += (
                f"{i}. <b>{entry['topic'][:50]}...</b>\n"
                f"   Score: {entry['score']} | {entry['timestamp'][:10]}\n\n"
            )

        await update.message.reply_text(message, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error fetching recent entries: {str(e)}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - welcome message and auto-register."""
    chat_id = str(update.effective_chat.id)

    # Auto-register this chat
    is_new = register_chat(chat_id)

    if is_new:
        await update.message.reply_text(
            f"👋 Welcome to PL Content Bot!\n\n"
            f"✅ <b>You are now registered!</b>\n"
            f"You will receive all updates and notifications.\n\n"
            f"Commands:\n"
            f"/go - Generate content ideas now\n"
            f"/recent - Show recent topics\n"
            f"/status - Check bot status\n\n"
            f"The bot also runs automatically at 8:00 AM UK time daily.",
            parse_mode="HTML"
        )
        logger.info(f"New user registered: {chat_id}")
    else:
        await update.message.reply_text(
            f"👋 Welcome back!\n\n"
            f"You're already registered for updates.\n\n"
            f"Commands:\n"
            f"/go - Generate content ideas now\n"
            f"/recent - Show recent topics\n"
            f"/status - Check bot status",
            parse_mode="HTML"
        )


async def cmd_pause(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /pause command - pause daily scheduled runs."""
    chat_id = str(update.effective_chat.id)
    logger.info(f"/pause command received from chat {chat_id}")

    state = load_schedule_state()
    if state.get("paused"):
        await update.message.reply_text(
            f"⏸ Schedule is already paused.\n"
            f"Paused by: {state.get('paused_by', 'Unknown')}\n"
            f"Paused at: {state.get('paused_at', 'Unknown')}\n\n"
            f"Use /resume to re-enable.",
            parse_mode="HTML"
        )
        return

    state = {
        "paused": True,
        "paused_by": chat_id,
        "paused_at": datetime.now().isoformat()
    }
    save_schedule_state(state)

    await update.message.reply_text(
        "⏸ <b>Daily schedule paused</b>\n\n"
        "The 8 AM automatic run is now disabled.\n"
        "Manual /go commands still work.\n\n"
        "Use /resume to re-enable.",
        parse_mode="HTML"
    )


async def cmd_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /resume command - resume daily scheduled runs."""
    chat_id = str(update.effective_chat.id)
    logger.info(f"/resume command received from chat {chat_id}")

    state = load_schedule_state()
    if not state.get("paused"):
        await update.message.reply_text(
            "▶️ Schedule is already active.\n"
            "Daily runs at 8 AM UK time are enabled.",
            parse_mode="HTML"
        )
        return

    state = {
        "paused": False,
        "paused_by": None,
        "paused_at": None,
        "resumed_by": chat_id,
        "resumed_at": datetime.now().isoformat()
    }
    save_schedule_state(state)

    await update.message.reply_text(
        "▶️ <b>Daily schedule resumed</b>\n\n"
        "The 8 AM automatic run is now enabled.\n"
        "Next run: Tomorrow at 8:00 AM UK time.",
        parse_mode="HTML"
    )


def create_application() -> Application:
    """Create and configure the Telegram bot application."""
    global _app

    if _app is not None:
        return _app

    # Build application
    _app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    _app.add_handler(CommandHandler("start", cmd_start))
    _app.add_handler(CommandHandler("go", cmd_go))
    _app.add_handler(CommandHandler("status", cmd_status))
    _app.add_handler(CommandHandler("recent", cmd_recent))
    _app.add_handler(CommandHandler("pause", cmd_pause))
    _app.add_handler(CommandHandler("resume", cmd_resume))

    logger.info("Telegram bot application created")
    return _app


async def run_bot() -> None:
    """Run the Telegram bot (blocking)."""
    app = create_application()

    logger.info("Starting Telegram bot...")
    await app.initialize()
    await app.start()

    # Start polling for updates
    await app.updater.start_polling(drop_pending_updates=True)

    logger.info("Bot is running. Press Ctrl+C to stop.")

    # Keep running until interrupted
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


def main():
    """Main entry point for running the bot standalone."""
    # Validate configuration
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return

    # Run the bot
    asyncio.run(run_bot())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    main()
