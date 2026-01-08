# Premier League Content Automation

Automatically discover trending Premier League topics and generate ready-to-use TikTok/Reels video scripts.

## What It Does

1. **Fetches Twitter Trends** - UK-specific trending topics via Apify
2. **Fetches Football News** - Aggregated from Goal, ESPN, OneFootball via RapidAPI
3. **Filters for PL Relevance** - AI identifies Premier League topics only
4. **Scores Drama Potential** - Ranks topics 1-10 based on viral potential
5. **Generates Scripts** - 3 video scripts per topic in UK football banter style
6. **Saves to Google Sheets** - Organized output with timestamps
7. **Notifies via Telegram** - Real-time progress updates

## Quick Start

### 1. Clone and Install

```bash
cd /path/to/project
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys (see API Setup below)
```

### 3. Run the Bot

```bash
# Run Telegram bot (interactive mode)
python src/telegram_bot.py

# Or run pipeline directly (no Telegram)
python src/main.py
```

### 4. Set Up Cron (Optional)

```bash
# Add to crontab for daily 8:00 AM UK runs
crontab -e

# Add this line:
0 8 * * * cd /path/to/project && /path/to/venv/bin/python src/scheduled_run.py >> logs/cron.log 2>&1
```

## API Setup

### Gemini API (Required)
1. Go to [Google AI Studio](https://ai.google.dev/)
2. Create API key
3. Add to `.env`: `GEMINI_API_KEY=your_key`

**Important:** This project uses `gemini-3-pro-preview` model only.

### Telegram Bot (Required)
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow prompts
3. Copy the bot token
4. Add to `.env`: `TELEGRAM_BOT_TOKEN=your_token`
5. Start a chat with your bot and send `/start`
6. Get your chat ID from the response
7. Add to `.env`: `TELEGRAM_CHAT_ID=your_chat_id`

### Apify (Required)
1. Sign up at [Apify](https://apify.com/)
2. Go to Settings > Integrations
3. Copy API token
4. Add to `.env`: `APIFY_API_TOKEN=your_token`

### RapidAPI (Required)
1. Sign up at [RapidAPI](https://rapidapi.com/)
2. Subscribe to a football news API (free tier available)
3. Copy API key from dashboard
4. Add to `.env`: `RAPIDAPI_KEY=your_key`

### Google Sheets (Required)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable "Google Sheets API"
4. Go to IAM & Admin > Service Accounts
5. Create service account, download JSON key
6. Save as `credentials.json` in project root
7. Create a Google Sheet
8. Share the sheet with the service account email (from credentials.json)
9. Copy the Sheet ID from the URL: `docs.google.com/spreadsheets/d/[SHEET_ID]/edit`
10. Add to `.env`: `GOOGLE_SHEETS_ID=your_sheet_id`

## Usage

### Telegram Commands

| Command | Description |
|---------|-------------|
| `/go` | Generate content ideas now |
| `/recent` | Show recent topics |
| `/status` | Check bot status |
| `/start` | Welcome message + your chat ID |

### Sample Flow

```
You: /go

Bot: ⏳ Starting content pipeline...
Bot: ⏳ Fetching Twitter trends (UK)...
Bot: ⏳ Fetching football news...
Bot: ⏳ Processing topics...
Bot: 🔥 Top drama: "Arsenal bottle 2-0 lead" (Score: 8/10)
Bot: ⏳ Generating scripts...
Bot: ✅ Pipeline Complete!

📌 Topic: Arsenal bottle 2-0 lead
🔥 Score: 8/10

📝 3 scripts added to Google Sheet.
```

## Google Sheets Output

| Column | Content |
|--------|---------|
| Timestamp | When generated |
| Topic | The trending topic |
| Drama Score | Score/10 with breakdown |
| Script 1-3 | Hook, Premise, Punchline for each |

## Project Structure

```
├── src/
│   ├── main.py           # Main pipeline orchestration
│   ├── config.py         # Configuration management
│   ├── apify_client.py   # Twitter trends fetching
│   ├── news_client.py    # Football news fetching
│   ├── gemini_processor.py # AI processing
│   ├── sheets_client.py  # Google Sheets output
│   ├── telegram_bot.py   # Telegram interface
│   └── scheduled_run.py  # Cron job script
├── logs/                 # Log files
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── credentials.json     # Google service account (not in git)
└── README.md
```

## Troubleshooting

### "Missing configuration" error
Check your `.env` file has all required keys. Run:
```bash
python -c "from src.config import config; print(config.validate())"
```

### Telegram bot not responding
1. Make sure the bot token is correct
2. Try sending `/start` to initialize the chat
3. Check if the bot is running: `ps aux | grep telegram_bot`

### Google Sheets permission error
1. Verify `credentials.json` exists and is valid
2. Check the service account email is shared on the sheet
3. Ensure the sheet ID in `.env` is correct

### No PL topics found
- Twitter/news APIs may have no current PL content
- Try again during active news periods (match days, transfer windows)
- Check API rate limits haven't been exceeded

## Cost Estimates

| Service | Monthly Cost |
|---------|--------------|
| Apify | ~$5 |
| RapidAPI | Free tier |
| Gemini API | Free tier / ~$0-5 |
| **Total** | **~$5-10** |

## License

Private project for Tyler's content automation.
