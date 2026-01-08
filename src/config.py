"""
Configuration management for Premier League Content Automation.
Loads and validates environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-3-pro-preview"  # Mandatory model - do not change

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # Apify
    APIFY_API_TOKEN: str = os.getenv("APIFY_API_TOKEN", "")

    # Twitter API (twitterapi.io)
    TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY", "")

    # RapidAPI
    RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")

    # Google Sheets
    GOOGLE_SHEETS_ID: str = os.getenv("GOOGLE_SHEETS_ID", "")
    GOOGLE_SERVICE_ACCOUNT_FILE: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json")

    # Schedule (8:00 AM UK time)
    SCHEDULE_HOUR_UK: int = 8
    SCHEDULE_MINUTE: int = 0

    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate that all required configuration is present.
        Returns a list of missing configuration keys.
        """
        missing = []

        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not cls.TELEGRAM_CHAT_ID:
            missing.append("TELEGRAM_CHAT_ID")
        if not cls.APIFY_API_TOKEN:
            missing.append("APIFY_API_TOKEN")
        if not cls.RAPIDAPI_KEY:
            missing.append("RAPIDAPI_KEY")
        if not cls.GOOGLE_SHEETS_ID:
            missing.append("GOOGLE_SHEETS_ID")

        return missing

    @classmethod
    def is_valid(cls) -> bool:
        """Check if all required configuration is present."""
        return len(cls.validate()) == 0


# Create a singleton instance
config = Config()
