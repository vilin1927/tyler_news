# PRD: Premier League Content Automation

## 1. Introduction/Overview

**Problem:** Manually researching viral Premier League topics takes 1-2 hours daily - scrolling Twitter, checking news sites, and figuring out what's actually trending vs. stale news. By the time a topic is found and scripts are written, the viral moment has passed.

**Solution:** An automated system that discovers trending Premier League topics and generates ready-to-use video scripts for TikTok/Reels/Shorts. The system pulls from Twitter trends and football news, filters for PL relevance, ranks by "drama potential", and generates 3 script ideas in authentic UK football banter style.

**Target User:** Tyler - a content creator focused on Premier League short-form video content for UK football fans.

---

## 2. Goals

1. **Reduce research time** from 1-2 hours daily to under 60 seconds per trigger
2. **Capture trending topics** while they're still viral (< 3 hours old preferred)
3. **Generate quality scripts** in authentic UK football banter style (not generic AI speak)
4. **Full automation** with both manual triggers and scheduled daily runs
5. **Centralized output** to Google Sheets for easy script management

---

## 3. User Stories

### US-1: Manual Topic Discovery
> As Tyler, I want to send `/go` to a Telegram bot and receive trending PL topics with scripts within 60 seconds, so I can quickly create content when I have filming time.

### US-2: Automated Daily Discovery
> As Tyler, I want the system to automatically run at 8:00 AM UK time daily and save results to Google Sheets, so I have fresh content ideas waiting each morning.

### US-3: Drama-Ranked Topics
> As Tyler, I want topics ranked by viral potential (drama score), so I can focus on the highest-engagement content first.

### US-4: Ready-to-Film Scripts
> As Tyler, I want 3 script ideas per topic with hook/premise/punchline structure, so I can pick one and start filming immediately without additional writing.

### US-5: Progress Visibility
> As Tyler, I want real-time Telegram updates during processing, so I know the system is working and can see results as they're generated.

---

## 4. Functional Requirements

### 4.1 Telegram Bot Interface

| ID | Requirement |
|----|-------------|
| FR-1 | The bot MUST respond to `/go` command to trigger manual content discovery |
| FR-2 | The bot MUST send progress updates during processing (fetching trends, fetching news, processing, generating scripts, complete) |
| FR-3 | The bot MUST display the top topic and its drama score when processing completes |
| FR-4 | The bot MUST confirm when scripts have been saved to Google Sheets |
| FR-5 | The bot MUST handle errors gracefully and notify Tyler if something fails |

### 4.2 Data Collection

| ID | Requirement |
|----|-------------|
| FR-6 | The system MUST fetch UK-specific Twitter trends with engagement metrics |
| FR-7 | The system MUST fetch football news from aggregated sources (Goal, ESPN, OneFootball or similar) |
| FR-8 | The system SHOULD use Apify for Twitter trends (Tyler has account with credits) |
| FR-9 | The system MAY use alternative Twitter trend sources if better/cheaper options exist |
| FR-10 | The system SHOULD use RapidAPI "Football News API" aggregator or developer-researched best free-tier option |

### 4.3 AI Processing (Gemini)

| ID | Requirement |
|----|-------------|
| FR-11 | The system MUST use Gemini API with `gemini-3-pro-preview` model ONLY (mandatory) |
| FR-12 | The system MUST merge and deduplicate data from Twitter and news sources |
| FR-13 | The system MUST filter topics for Premier League relevance ONLY |
| FR-14 | The system MUST score each topic 1-10 based on drama/viral potential |
| FR-15 | The system MUST select the highest-scoring topic for script generation |

### 4.4 Drama Scoring System

| ID | Requirement |
|----|-------------|
| FR-16 | Drama score MUST factor in club size (Big 6 = +3, Mid-table = +1, Lower = 0) |
| FR-17 | Drama score MUST factor in controversy type (Manager sacking = +3, Player drama = +2, Match result = +1) |
| FR-18 | Drama score MUST factor in recency (< 3 hours = +2, < 12 hours = +1, > 12 hours = 0) |
| FR-19 | Drama score MUST factor in engagement (Trending #1 = +2, Top 5 = +1) |
| FR-20 | Final score MUST be normalized to 1-10 scale |

### 4.5 Script Generation

| ID | Requirement |
|----|-------------|
| FR-21 | The system MUST generate exactly 3 script ideas per top topic |
| FR-22 | Each script MUST include: Hook, Premise, and Punchline |
| FR-23 | Scripts MUST be written in authentic UK football banter style |
| FR-24 | Scripts MUST NOT use generic AI corporate language |

### 4.6 Google Sheets Output

| ID | Requirement |
|----|-------------|
| FR-25 | The system MUST connect to Tyler's Google Sheet via API (Tyler creates the Sheet) |
| FR-26 | The system MUST save: Timestamp, Topic, Drama Score, Script 1, Script 2, Script 3 |
| FR-27 | The system MUST append new rows (not overwrite existing data) |

### 4.7 Scheduling

| ID | Requirement |
|----|-------------|
| FR-28 | The system MUST support automated daily runs via cron job |
| FR-29 | Default schedule MUST be 8:00 AM UK time |
| FR-30 | Schedule MUST be configurable via cron expression |

---

## 5. Non-Goals (Out of Scope)

The following are explicitly **NOT** part of this project:

- Ongoing maintenance beyond 1 week post-delivery
- Additional features not specified in this PRD
- API cost payments (Tyler pays providers directly)
- Multiple scheduled runs per day (only 1 scheduled + unlimited manual)
- Video editing or content creation beyond scripts
- Social media posting automation
- Image/thumbnail generation
- Multi-language support (English/UK only)
- Historical trend analysis or reporting dashboards
- User authentication or multi-user support

---

## 6. Design Considerations

### Telegram Bot Flow

```
User: /go

Bot: Fetching Twitter trends (UK)...

Bot: Fetching football news...

Bot: Found 8 Premier League topics

Bot: Top drama: "Arsenal bottle 2-0 lead" (Score: 8/10)

Bot: Generating scripts...

Bot: Done! 3 scripts added to Sheet
```

### Google Sheets Structure

| Column | Content | Example |
|--------|---------|---------|
| A | Timestamp | 2026-01-04 09:15:00 |
| B | Topic | Arsenal bottle 2-0 lead vs Brighton |
| C | Drama Score | 8/10 - Big 6, bottle job, high engagement |
| D | Script 1 | HOOK: "Arsenal fans at halftime vs full time" \| PREMISE: Show celebration then despair \| PUNCHLINE: "It's the hope that kills you" |
| E | Script 2 | HOOK: "Arteta's excuses loading..." \| ... |
| F | Script 3 | HOOK: "Brighton really said 'hold my beer'" \| ... |

---

## 7. Technical Considerations

### Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| AI Processing | Gemini API (gemini-3-pro-preview model ONLY) |
| Twitter Trends | Apify (Tyler's existing account) - open to alternatives |
| Football News | RapidAPI aggregator (free tier) - developer to research best option |
| Output | Google Sheets API |
| Notifications | Telegram Bot API (Tyler's existing token) |
| Scheduling | Cron job |
| Hosting | Tyler's existing VPS |

### Dependencies

- Tyler provides: Apify account with credits, Telegram bot token, Google Sheet (created by Tyler)
- Developer sets up: Google Sheets API connection, all code and integrations

### API Cost Estimates (Monthly)

| Service | Estimated Cost |
|---------|----------------|
| Apify (Twitter Trends) | ~$5 |
| RapidAPI Football News | Free tier |
| Gemini API | Free tier / ~$0-5 |
| VPS | $0 (existing) |
| **Total** | **~$5-10/month** |

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| End-to-end execution time | < 60 seconds |
| Manual trigger response | Bot acknowledges within 2 seconds |
| PL topic accuracy | > 90% of filtered topics are genuinely PL-related |
| Script quality | Tyler rates scripts as "usable without major rewrites" > 70% of the time |
| System reliability | < 2 failures per week |
| Uptime | Scheduled runs execute successfully > 95% of the time |

---

## 9. Open Questions

| # | Question | Status |
|---|----------|--------|
| 1 | Which specific Apify actor/scraper should be used for UK Twitter trends? | Developer to research |
| 2 | What is the Google Sheet ID / URL that Tyler will create? | Pending from Tyler |
| 3 | What is the Telegram bot token? | Pending from Tyler (has token ready) |
| 4 | Should the system handle multiple topics per run, or always just the top 1? | Assumed: Top 1 only |
| 5 | Is there a specific VPS setup (OS, Python version) to target? | Pending from Tyler |
| 6 | Should failed runs be retried automatically? | Assumed: No, just notify |

---

## Appendix: Content Style Guide

### Topics to Cover
- Transfer drama and rumors
- Manager sackings/appointments
- Match results and bottlejobs
- Player controversies
- Fan reactions and memes

### Script Style
- **DO:** UK football banter, rivalry references, self-deprecating humor, meme formats
- **DON'T:** Generic AI speak, American sports terminology, corporate language

### Example Good Script
> HOOK: "Arsenal fans at halftime vs full time"
> PREMISE: Show celebration then despair
> PUNCHLINE: "It's the hope that kills you"

### Example Bad Script (Avoid)
> HOOK: "Exciting match results today!"
> PREMISE: Arsenal experienced a challenging second half
> PUNCHLINE: "Better luck next time, team!"
