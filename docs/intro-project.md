# Premier League Content Automation - Project Goal

## What It Does
Automatically discovers trending Premier League topics and generates ready-to-use video scripts for TikTok/Reels/Shorts. Pulls from Twitter trends + football news, filters for PL relevance, ranks by "drama potential", then generates 3 script ideas in authentic UK football banter style.

## The Problem
Manually researching viral PL topics takes 1-2 hours daily - scrolling Twitter, checking news sites, figuring out what's actually trending vs. stale news. By the time you find a topic, write scripts, and film - the moment has passed. This process doesn't scale and requires constant attention to not miss viral moments.

## The Solution
Telegram bot trigger → System fetches trends → AI filters & ranks → Generates scripts:
- **Twitter Trends** (UK-specific, real-time engagement data)
- **Football News** (Goal, ESPN, OneFootball aggregated)
- **Drama Scoring** (1-10 scale based on controversy, club size, recency)
- **Script Generation** (3 ideas per topic with hook/premise/punchline)

---

## Tyler's Content Focus

Premier League short-form video content targeting UK football fans. Topics include:
- Transfer drama and rumors
- Manager sackings/appointments
- Match results and bottlejobs
- Player controversies
- Fan reactions and memes

Style: **UK football banter** - not generic AI corporate speak.

---

## How It Works

### Step 1: TRIGGER
- **Manual:** Send `/go` to Telegram bot anytime
- **Automatic:** Daily 8:00 AM UK (configurable via cron)

### Step 2: DATA COLLECTION
- **Twitter Trends:** Apify scraper pulls UK trending topics with engagement metrics
- **Football News:** RapidAPI aggregator (Goal, ESPN, OneFootball) - free tier

### Step 3: AI PROCESSING (Claude)
- **Merge & Deduplicate:** Combine sources, remove duplicates
- **PL Filter:** AI filters for Premier League relevance ONLY
- **Drama Ranker:** Score each topic 1-10 based on viral potential
- **Topic Selector:** Pick the highest-scoring topic

### Step 4: SCRIPT GENERATION (Claude)
- Generate 3 script ideas for the top topic
- Each script has: **Hook** → **Premise** → **Punchline**
- Written in authentic UK football banter style

### Step 5: OUTPUT
- Save to Google Sheets (timestamp, topic, score, 3 scripts)
- Send Telegram notification with summary

---

## Drama Scoring System

| Factor | Points |
|--------|--------|
| **Club Size** | Big 6 = +3, Mid-table = +1, Lower = 0 |
| **Controversy** | Manager sacking = +3, Player drama = +2, Match result = +1 |
| **Recency** | < 3 hours = +2, < 12 hours = +1, > 12 hours = 0 |
| **Engagement** | Trending #1 = +2, Top 5 = +1 |

**Final Score:** 1-10 (higher = more viral potential)

---

## Sample Telegram Flow

```
You: /go

Bot: ⏳ Fetching Twitter trends (UK)...

Bot: ⏳ Fetching football news...

Bot: 📊 Found 8 Premier League topics

Bot: 🔥 Top drama: "Arsenal bottle 2-0 lead" (Score: 8/10)

Bot: ✍️ Generating scripts...

Bot: ✅ Done! 3 scripts added to Sheet
```

**Total time: ~30-60 seconds**

---

## Sample Google Sheets Output

| Field | Example |
|-------|---------|
| **Timestamp** | 2026-01-04 09:15:00 |
| **Topic** | Arsenal bottle 2-0 lead vs Brighton |
| **Drama Score** | 8/10 - Big 6, bottle job, high engagement |
| **Script 1** | HOOK: "Arsenal fans at halftime vs full time" \| PREMISE: Show celebration then despair \| PUNCHLINE: "It's the hope that kills you" |
| **Script 2** | HOOK: "Arteta's excuses loading..." \| PREMISE: List classic manager excuses \| PUNCHLINE: "The wind was against us for both halves" |
| **Script 3** | HOOK: "Brighton really said 'hold my beer'" \| PREMISE: Show comeback stats \| PUNCHLINE: "Levels to this game" |

---

## Why Python + Claude (Not n8n/Make.com)

| Factor | n8n / Make.com | Python + Claude |
|--------|----------------|-----------------|
| **Drama Detection** | Basic keyword matching | AI understands context, sarcasm, rivalry |
| **Script Quality** | Generic GPT output | Tailored banter with proper prompting |
| **PL Filtering** | Simple club name matching | Understands transfers, manager drama, fan culture |
| **Customization** | Limited to node options | Full control over every decision |
| **Monthly Cost** | $20-50/mo platform fee + API | API costs only (~$10-15/mo) |

**The difference:** n8n/Make.com are great for "if this, then that" workflows. But Tyler needs something that actually *understands* which topics have viral potential and *writes* scripts in authentic UK football banter.

---

## Technical Stack

| Component | Technology |
|-----------|------------|
| Manual Trigger | Telegram Bot (`/go` command) |
| Auto Schedule | Cron job (8:00 AM UK daily) |
| Twitter Trends | Apify (UK trending scraper) |
| Football News | RapidAPI (free tier aggregator) |
| AI Processing | Claude API |
| Output | Google Sheets |
| Notifications | Telegram Bot |
| Hosting | Tyler's existing VPS |

---

## User Inputs

1. `/go` command on Telegram (manual trigger)
2. Or wait for daily auto-run at 8:00 AM UK

No other inputs needed - system is fully automated.

---

## Outputs

- **Google Sheets:** Topic, drama score, 3 scripts with timestamps
- **Telegram:** Real-time progress updates + completion notification

---

## Cost Breakdown

### One-Time Development
| Item | Cost |
|------|------|
| Complete system development & deployment | **$250 USD** |

### Ongoing Monthly (Tyler pays directly)
| Service | Est. Monthly |
|---------|--------------|
| Apify (Twitter Trends) | ~$5 |
| RapidAPI Football News | Free tier |
| Claude API | ~$5-10 |
| VPS (already have) | $0 |
| **Total Monthly** | **~$10-15** |

---

## What's NOT Included

- Ongoing maintenance beyond 1 week
- Additional features not in this spec
- API costs (Tyler pays providers directly)
- Multiple scheduled runs per day (1 scheduled + unlimited manual)
- Video editing or content creation beyond scripts
- Social media posting automation

---

## Timeline

| Day | Task | Milestone |
|-----|------|-----------|
| 1 | API integrations (Twitter + News) | Data pipeline working |
| 2 | PL filtering + drama ranking | Smart filtering live |
| 3 | Script generation + Sheets output | End-to-end working |
| 4-5 | Telegram bot + deployment + testing | Delivery |

**Estimated delivery:** 3-5 working days from project start