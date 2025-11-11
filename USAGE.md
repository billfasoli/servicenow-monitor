# ServiceNow Monitor - Usage Guide

## Quick Start

The ServiceNow Monitor can be run in two ways:
1. **Command Line Interface (CLI)** - For terminal output and scripting
2. **Web Dashboard** - For interactive browsing

## Command Line Interface (CLI)

### Basic Usage

**Get help:**
```bash
python src/main.py --help
```

**Default behavior (no arguments):**
```bash
python src/main.py
```
This fetches:
- SEC filings from last 90 days
- Press releases from last 60 days
- News articles from last 30 days

### Convenient Time Period Presets

**Last week:**
```bash
python src/main.py --period week
```
Fetches data from the last 7 days across all sources.

**Last month:**
```bash
python src/main.py --period month
```
Fetches data from the last 30 days across all sources.

**Last quarter:**
```bash
python src/main.py --period quarter
```
Fetches data from the last 90 days across all sources.

**Last year:**
```bash
python src/main.py --period year
```
Fetches data from the last 365 days across all sources.

### Custom Time Periods

**Custom days (all sources):**
```bash
python src/main.py --days 14
```
Fetches data from the last 14 days across all sources.

**Custom days per source:**
```bash
python src/main.py --filings-days 30 --releases-days 15 --articles-days 7
```
- SEC filings: last 30 days
- Press releases: last 15 days
- News articles: last 7 days

### Real-World Examples

**What happened this week?**
```bash
python src/main.py --period week
```

**What happened this month?**
```bash
python src/main.py --period month
```

**Recent filings only (last 30 days):**
```bash
python src/main.py --filings-days 30 --releases-days 0 --articles-days 0
```

**Just today's news:**
```bash
python src/main.py --articles-days 1 --filings-days 0 --releases-days 0
```

## Output Format

The CLI outputs data in a structured format:

```
============================================================
SERVICENOW MONITOR - SUMMARY
============================================================

📄 SEC FILINGS
------------------------------------------------------------

2025-10-30 - 10-Q
  Quarterly Report

  AI SUMMARY:
  • Q3 2025 revenue grew 24% YoY to $2.6B
  • Subscription billings increased 25% YoY
  • Strong AI platform adoption driving growth
  • Raised full-year guidance based on demand

  https://www.sec.gov/Archives/edgar/...

📰 PRESS RELEASES
------------------------------------------------------------

2025-10-29 - ServiceNow Reports Q3 Results
  Category: earnings | Source: Business Wire

  AI SUMMARY:
  • Beat revenue expectations with $2.6B in Q3
  • Operating margin improved to 26%
  • 10,000+ customers now using AI products

  https://www.businesswire.com/...

📰 NEWS ARTICLES
------------------------------------------------------------

2025-10-28 - ServiceNow Stock Jumps on Strong Earnings
  Source: TechCrunch | Author: Sarah Johnson

  AI SUMMARY:
  • Stock price increased 8% after earnings
  • Analysts raised price targets
  • Cloud migration trends benefiting ServiceNow

  https://techcrunch.com/...

============================================================
```

## Web Dashboard

**Start the web server:**
```bash
python src/web_app.py
```

**Access the dashboard:**
Open your browser to `http://localhost:5000`

**Features:**
- Click "Refresh" to fetch latest data
- Switch between tabs (Filings, Releases, Articles)
- View AI summaries inline
- Click links to read full content
- See summary statistics at the top

## Environment Variables

**Required for AI summarization:**
```bash
export ANTHROPIC_API_KEY='your-claude-api-key'
```

**Optional for news monitoring:**
```bash
export NEWS_API_KEY='your-newsapi-key'
```

Get a free NewsAPI key at: https://newsapi.org/register

## Configuration File

For advanced settings, create `config/config.yaml`:

```bash
cp config/config.yaml.example config/config.yaml
```

Edit to customize:
- AI model and summarization settings
- Enable/disable specific data sources
- Custom keywords for news monitoring
- Output preferences

## Tips

1. **Start with a week**: Get familiar with the output format
   ```bash
   python src/main.py --period week
   ```

2. **Use the web dashboard**: Better for browsing and exploring
   ```bash
   python src/web_app.py
   ```

3. **Customize for your needs**: Different sources update at different frequencies
   - SEC filings: Monthly/quarterly
   - Press releases: As announced
   - News: Daily

4. **Save output**: Redirect to a file for later reference
   ```bash
   python src/main.py --period week > report.txt
   ```

5. **Automate**: Add to cron for daily reports
   ```bash
   # Run every day at 9 AM
   0 9 * * * cd /path/to/servicenow-monitor && python src/main.py --period week
   ```

## Troubleshooting

**No data returned:**
- Check your API keys are set
- Verify internet connection
- Check the time period isn't too restrictive

**Rate limiting:**
- NewsAPI free tier: 100 requests/day
- SEC EDGAR: 10 requests/second (automatic rate limiting built-in)

**Missing summaries:**
- Ensure `ANTHROPIC_API_KEY` is set
- Check Claude API quota/credits
- Verify `enabled: true` in config for Claude

## Getting Help

```bash
python src/main.py --help
```

Shows all available options and examples.
