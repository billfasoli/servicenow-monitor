# ServiceNow Monitor

A Python-based monitoring and summarization tool for staying aware of everything happening at ServiceNow.

## Features

- **SEC Filings**: Automatically fetch 10-K, 10-Q, and 8-K reports from SEC EDGAR
- **Press Releases**: Monitor ServiceNow press releases from Business Wire and other sources
- **News Monitoring**: Track news articles about ServiceNow from NewsAPI
  - Real-time news from 150,000+ sources
  - Customizable keywords for targeted monitoring
  - Article images and metadata
- **AI Summarization**: Leverage Claude AI to generate intelligent, contextual summaries
  - Earnings-specific analysis for financial results
  - Strategic insights from 10-K/10-Q filings
  - Concise summaries of press releases and news articles
- **Secure Secrets Management**: 1Password CLI integration for API keys
  - No secrets in code or config files
  - Automatic fallback to environment variables
  - Encrypted storage in 1Password vault
- **Flexible Time Periods**: Query updates by week, month, quarter, or custom days
- **Internal Documents** (Coming soon): Monitor SharePoint and email attachments

## Project Structure

```
servicenow-monitor/
├── config/          # Configuration files
├── src/
│   ├── fetchers/    # Data fetching modules (SEC, press releases, etc.)
│   ├── summarizers/ # AI summarization using Claude
│   ├── outputs/     # Output generators (email, HTML, etc.)
│   ├── templates/   # Flask HTML templates
│   ├── static/      # CSS, JS, images for web dashboard
│   ├── main.py      # CLI orchestrator
│   └── web_app.py   # Flask web dashboard
├── data/            # Local data storage
└── tests/           # Unit tests
```

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/billfasoli/servicenow-monitor.git
cd servicenow-monitor
pip install -r requirements.txt
```

### 2. Configure API Keys (Choose One Method)

#### Option A: 1Password CLI (Recommended) 🔒

Most secure - keys never stored in code or environment:

```bash
# Sign in to 1Password
eval $(op signin)

# Store your API keys in 1Password app:
# - Create item: "Anthropic API Key" with your Claude key
# - Create item: "NewsAPI" with your NewsAPI key

# Test it works
python src/secrets.py
```

See [1PASSWORD_SETUP.md](1PASSWORD_SETUP.md) for detailed instructions.

#### Option B: Environment Variables

```bash
export ANTHROPIC_API_KEY='your-claude-api-key'
export NEWS_API_KEY='your-newsapi-key'  # Optional, for news monitoring
```

Get keys:
- Claude API: [https://console.anthropic.com/](https://console.anthropic.com/)
- NewsAPI: [https://newsapi.org/register](https://newsapi.org/register) (free)

### 3. Run the Monitor

**Quick test - what happened this week:**
```bash
python src/main.py --period week
```

**Web dashboard:**
```bash
python src/web_app.py
# Open http://localhost:5000
```

**Custom time periods:**
```bash
python src/main.py --period month        # Last 30 days
python src/main.py --days 14             # Last 14 days
python src/main.py --help                # See all options
```

See [USAGE.md](USAGE.md) for complete usage guide.

## Web Dashboard

The Flask-based web dashboard provides an interactive interface to view and manage your ServiceNow monitoring data.

**Features:**
- Real-time data refresh with a single click
- Summary statistics for filings, press releases, and news articles
- Tabbed interface for easy navigation between data types
- AI-generated summaries displayed inline
- News articles with images and metadata
- Responsive design that works on mobile and desktop
- Direct links to original SEC filings, press releases, and news articles

**What You'll See:**
- **SEC Filings**: View all filings (10-K, 10-Q, 8-K) with color-coded badges
- **Press Releases**: Categorized as earnings or general news with AI summaries
- **News Articles**: Latest articles with images, source attribution, and AI summaries
- One-click refresh to fetch the latest data from all sources

## CLI Usage Examples

The monitor supports flexible time periods and data source selection:

```bash
# What happened this week?
python src/main.py --period week

# What happened this month?
python src/main.py --period month

# What happened this quarter?
python src/main.py --period quarter

# Custom: last 14 days
python src/main.py --days 14

# Just recent SEC filings (last 30 days)
python src/main.py --filings-days 30 --releases-days 0 --articles-days 0

# Just today's news
python src/main.py --articles-days 1 --filings-days 0 --releases-days 0

# Save output to file
python src/main.py --period week > weekly-report.txt
```

See [USAGE.md](USAGE.md) for more examples and detailed documentation.

## Configuration

The monitor works out-of-the-box with minimal setup. For advanced configuration, create a `config/config.yaml` file:

```bash
cp config/config.yaml.example config/config.yaml
```

Customize:
- **Claude AI**: Model selection, number of items to summarize, token limits
- **Data Sources**: Enable/disable SEC filings, press releases, news articles
- **News Monitoring**: Custom keywords for targeted monitoring
- **Output Settings**: Email digest configuration (coming soon)
- **Microsoft Graph**: Internal document monitoring (coming soon)

See `config/config.yaml.example` for all available options.

## Security

**API Key Management:**

This project supports secure API key storage using 1Password CLI:

✅ **No secrets in code**: API keys never committed to repository
✅ **No environment pollution**: Keys retrieved on-demand from 1Password
✅ **Encrypted storage**: 1Password vault encryption
✅ **Access control**: 1Password manages access permissions
✅ **Audit trail**: 1Password logs all secret access

**Automatic Fallback Chain:**
1. 1Password CLI (if available and signed in)
2. Environment variables (if set)
3. Config file (not recommended for production)

See [1PASSWORD_SETUP.md](1PASSWORD_SETUP.md) for setup instructions.

## Development Roadmap

**Core Features:**
- [x] Project structure
- [x] SEC EDGAR fetcher (10-K, 10-Q, 8-K)
- [x] Press release fetcher (Business Wire)
- [x] News fetcher (NewsAPI - 150,000+ sources)
- [x] Claude AI summarization
  - [x] Context-aware prompts for different content types
  - [x] Earnings-specific analysis
  - [x] SEC filing analysis
  - [x] News article summarization

**User Interface:**
- [x] CLI with flexible time periods
  - [x] Preset periods (week, month, quarter, year)
  - [x] Custom day ranges
  - [x] Per-source time controls
- [x] Flask web dashboard
  - [x] Interactive UI with Bootstrap
  - [x] Real-time data refresh
  - [x] Summary statistics
  - [x] Tabbed interface for all data types
  - [x] Images and rich metadata

**Security & Configuration:**
- [x] 1Password CLI integration
  - [x] Secure secret retrieval
  - [x] Automatic fallback chain
  - [x] No secrets in code
- [x] Comprehensive documentation
  - [x] Setup guides
  - [x] Usage examples
  - [x] Security best practices

**Coming Soon:**
- [ ] Email digest generator
- [ ] Automated scheduling (cron/systemd)
- [ ] Microsoft Graph integration for internal docs
- [ ] Export to PDF/Excel
- [ ] Slack/Teams notifications

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes! ⚡
- **[USAGE.md](USAGE.md)** - Complete usage guide with examples
- **[1PASSWORD_SETUP.md](1PASSWORD_SETUP.md)** - Secure API key management
- **[config.yaml.example](config/config.yaml.example)** - Configuration options

## License

MIT License
