"""
Google Sheets client for saving content automation results.

Setup Instructions:
1. Go to Google Cloud Console (https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google Sheets API
4. Create a Service Account:
   - Go to IAM & Admin > Service Accounts
   - Create new service account
   - Download JSON key file
   - Save as 'credentials.json' in project root
5. Share your Google Sheet with the service account email
   (found in credentials.json as 'client_email')
"""

import logging
from datetime import datetime
from typing import Optional

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from config import config

logger = logging.getLogger(__name__)

# Google Sheets API scope
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Column headers for the sheet
HEADERS = [
    "Timestamp",
    "Topic",
    "Drama Score",
    "Topics Considered",  # Summary of all topics and their scores
    "Script 1 - Hook",
    "Script 1 - Premise",
    "Script 1 - Punchline",
    "Script 2 - Hook",
    "Script 2 - Premise",
    "Script 2 - Punchline",
    "Script 3 - Hook",
    "Script 3 - Premise",
    "Script 3 - Punchline"
]


def get_sheets_client() -> gspread.Client:
    """
    Get authenticated Google Sheets client.

    Returns:
        Authenticated gspread client
    """
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        config.GOOGLE_SERVICE_ACCOUNT_FILE,
        SCOPES
    )
    return gspread.authorize(creds)


def connect_to_sheet() -> gspread.Worksheet:
    """
    Connect to Tyler's Google Sheet.

    Returns:
        The first worksheet of the configured sheet
    """
    client = get_sheets_client()
    sheet = client.open_by_key(config.GOOGLE_SHEETS_ID)
    worksheet = sheet.sheet1

    # Ensure headers exist
    _ensure_headers(worksheet)

    return worksheet


def _ensure_headers(worksheet: gspread.Worksheet) -> None:
    """
    Ensure the worksheet has the correct headers.

    Only adds headers if the first row is empty.
    """
    try:
        first_row = worksheet.row_values(1)
        if not first_row or first_row[0] == "":
            worksheet.update("A1:M1", [HEADERS])  # A-M for 13 columns
            logger.info("Added headers to sheet")
    except Exception as e:
        logger.warning(f"Could not check/add headers: {str(e)}")


def append_result(
    timestamp: str,
    topic: str,
    score: str,
    scripts: list[dict],
    topics_summary: str = ""
) -> bool:
    """
    Append a new result row to the Google Sheet.

    Args:
        timestamp: ISO timestamp string
        topic: The selected topic
        score: Drama score with breakdown (e.g., "8/10 - Big 6 drama")
        scripts: List of 3 script dictionaries with hook/premise/punchline
        topics_summary: Summary of all topics considered and their scores

    Returns:
        True if successful, False otherwise
    """
    logger.info("Appending result to Google Sheet...")

    try:
        worksheet = connect_to_sheet()

        # Build row data
        row = [
            timestamp,
            topic,
            score,
            topics_summary,  # New column for topics considered
        ]

        # Add scripts (pad to 3 if less)
        for i in range(3):
            if i < len(scripts):
                script = scripts[i]
                row.extend([
                    script.get("hook", ""),
                    script.get("premise", ""),
                    script.get("punchline", "")
                ])
            else:
                row.extend(["", "", ""])

        # Append the row
        worksheet.append_row(row, value_input_option="USER_ENTERED")

        logger.info("Successfully appended result to sheet")
        return True

    except Exception as e:
        logger.error(f"Failed to append to sheet: {str(e)}")
        return False


def get_recent_entries(count: int = 10) -> list[dict]:
    """
    Get the most recent entries from the sheet.

    Args:
        count: Number of recent entries to retrieve

    Returns:
        List of entry dictionaries
    """
    try:
        worksheet = connect_to_sheet()
        all_values = worksheet.get_all_values()

        # Skip header row
        data_rows = all_values[1:] if len(all_values) > 1 else []

        # Get last N rows
        recent = data_rows[-count:] if len(data_rows) >= count else data_rows

        entries = []
        for row in reversed(recent):  # Most recent first
            if len(row) >= 3:
                entries.append({
                    "timestamp": row[0],
                    "topic": row[1],
                    "score": row[2],
                    "scripts": [
                        {"hook": row[3] if len(row) > 3 else "",
                         "premise": row[4] if len(row) > 4 else "",
                         "punchline": row[5] if len(row) > 5 else ""},
                        {"hook": row[6] if len(row) > 6 else "",
                         "premise": row[7] if len(row) > 7 else "",
                         "punchline": row[8] if len(row) > 8 else ""},
                        {"hook": row[9] if len(row) > 9 else "",
                         "premise": row[10] if len(row) > 10 else "",
                         "punchline": row[11] if len(row) > 11 else ""},
                    ]
                })

        return entries

    except Exception as e:
        logger.error(f"Failed to get recent entries: {str(e)}")
        return []


# For testing
if __name__ == "__main__":
    print("Testing Google Sheets connection...")

    # Test connection
    try:
        worksheet = connect_to_sheet()
        print(f"Connected to sheet: {worksheet.title}")

        # Test append
        test_scripts = [
            {"hook": "Test hook 1", "premise": "Test premise 1", "punchline": "Test punchline 1"},
            {"hook": "Test hook 2", "premise": "Test premise 2", "punchline": "Test punchline 2"},
            {"hook": "Test hook 3", "premise": "Test premise 3", "punchline": "Test punchline 3"},
        ]

        success = append_result(
            timestamp=datetime.now().isoformat(),
            topic="Test Topic - Arsenal bottling again",
            score="8/10 - Big 6, classic bottle job",
            scripts=test_scripts
        )

        print(f"Append test: {'Success' if success else 'Failed'}")

    except Exception as e:
        print(f"Test failed: {str(e)}")
