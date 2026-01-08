# Tasks: Premier League Content Automation

## Relevant Files

- `src/main.py` - Main entry point, orchestrates the full pipeline
- `src/config.py` - Configuration management, loads environment variables
- `src/apify_client.py` - Twitter trends fetching via Apify API
- `src/news_client.py` - Football news fetching via RapidAPI
- `src/gemini_processor.py` - Gemini AI processing (filter, score, generate scripts)
- `src/sheets_client.py` - Google Sheets integration for output
- `src/telegram_bot.py` - Telegram bot interface and command handlers
- `src/scheduled_run.py` - Standalone script for cron job execution
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variable template
- `README.md` - Setup, configuration, and deployment documentation

### Notes

- Gemini API must use `gemini-3-pro-preview` model only (mandatory requirement)
- Tyler provides: Apify account with credits, Telegram bot token, Google Sheet URL
- Target deployment: Tyler's existing VPS
- Use `pip install -r requirements.txt` to install dependencies
- All API keys stored in `.env` file (never commit to git)

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` → `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout a new branch: `git checkout -b feature/pl-content-automation`

- [x] 1.0 Set up project structure and dependencies
  - [x] 1.1 Create `src/` directory structure
  - [x] 1.2 Create `requirements.txt` with dependencies (google-generativeai, python-telegram-bot, gspread, oauth2client, requests, apify-client, python-dotenv)
  - [x] 1.3 Create `.env.example` with placeholder environment variables
  - [x] 1.4 Create `src/config.py` for loading and validating configuration
  - [x] 1.5 Create `src/main.py` as the main entry point

- [x] 2.0 Implement Twitter Trends data collection (Apify)
  - [x] 2.1 Research and select appropriate Apify actor for UK Twitter/X trends
  - [x] 2.2 Create `src/apify_client.py` module
  - [x] 2.3 Implement `fetch_uk_trends()` function to get trending topics with engagement metrics
  - [x] 2.4 Add error handling and retry logic for API failures
  - [x] 2.5 Test Apify integration with sample requests

- [x] 3.0 Implement Football News data collection (RapidAPI)
  - [x] 3.1 Research and select best free-tier football news API on RapidAPI
  - [x] 3.2 Create `src/news_client.py` module
  - [x] 3.3 Implement `fetch_football_news()` function to get recent PL-related articles
  - [x] 3.4 Add error handling for API failures
  - [x] 3.5 Test RapidAPI integration with sample requests

- [x] 4.0 Implement Gemini AI processing (merge, filter, score, generate scripts)
  - [x] 4.1 Create `src/gemini_processor.py` module
  - [x] 4.2 Initialize Gemini client with `gemini-3-pro-preview` model (mandatory)
  - [x] 4.3 Implement `merge_and_deduplicate()` function for Twitter + news data
  - [x] 4.4 Implement `filter_pl_topics()` with prompt for Premier League relevance filtering
  - [x] 4.5 Implement `score_drama()` with prompt for drama scoring (club size, controversy, recency, engagement)
  - [x] 4.6 Implement `select_top_topic()` to pick highest-scoring topic
  - [x] 4.7 Implement `generate_scripts()` with prompt for 3 scripts (hook/premise/punchline, UK banter style)
  - [x] 4.8 Test each AI function with sample data

- [x] 5.0 Implement Google Sheets integration
  - [x] 5.1 Create `src/sheets_client.py` module
  - [x] 5.2 Document Google Sheets API setup (service account creation, sharing sheet)
  - [x] 5.3 Implement `connect_to_sheet()` function using gspread
  - [x] 5.4 Implement `append_result()` function to add row (timestamp, topic, score, script1, script2, script3)
  - [x] 5.5 Test write operations to Google Sheet

- [x] 6.0 Implement Telegram Bot interface
  - [x] 6.1 Create `src/telegram_bot.py` module
  - [x] 6.2 Initialize bot with token from environment variables
  - [x] 6.3 Implement `/go` command handler to trigger pipeline
  - [x] 6.4 Implement `send_progress()` helper for status updates (fetching, processing, generating, complete)
  - [x] 6.5 Implement error notification messages when pipeline fails
  - [x] 6.6 Create `run_pipeline()` function that orchestrates: fetch → process → generate → save → notify
  - [x] 6.7 Test bot commands and verify message flow

- [x] 7.0 Implement scheduling (cron job for daily runs)
  - [x] 7.1 Create `src/scheduled_run.py` script for headless cron execution
  - [x] 7.2 Add logging for scheduled runs (success/failure with timestamps)
  - [x] 7.3 Document cron setup: `0 8 * * * cd /path/to/project && python src/scheduled_run.py`
  - [x] 7.4 Configure for 8:00 AM UK time (handle timezone)

- [x] 8.0 Testing, documentation, and deployment
  - [x] 8.1 End-to-end test: trigger `/go` and verify full pipeline completes
  - [x] 8.2 Write `README.md` with setup instructions, API key requirements, and usage guide
  - [x] 8.3 Create deployment script or instructions for Tyler's VPS
  - [ ] 8.4 Deploy to VPS and configure environment variables
  - [ ] 8.5 Set up cron job on VPS
  - [ ] 8.6 Verify scheduled run executes correctly at 8:00 AM UK
  - [ ] 8.7 Handoff to Tyler, begin 1-week support period
