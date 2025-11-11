# ServiceNow Monitor

A Python-based monitoring and summarization tool for staying aware of everything happening at ServiceNow.

## Features

- **SEC Filings**: Automatically fetch 10-K, 10-Q, and 8-K reports from SEC EDGAR
- **Press Releases**: Monitor ServiceNow press releases from Business Wire and other sources
- **AI Summarization**: Leverage Claude AI to generate intelligent, contextual summaries
  - Earnings-specific analysis for financial results
  - Strategic insights from 10-K/10-Q filings
  - Concise summaries of press releases and announcements
- **News Monitoring** (Coming soon): Track news articles about ServiceNow
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

## Setup

1. Clone the repository:
```bash
git clone https://github.com/billfasoli/servicenow-monitor.git
cd servicenow-monitor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your Claude API key:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

4. (Optional) Configure your settings:
```bash
cp config/config.yaml.example config/config.yaml
# Edit config.yaml to customize behavior
```

5. Run the monitor:

**Command Line (CLI)**:
```bash
python src/main.py
```

**Web Dashboard**:
```bash
python src/web_app.py
```
Then open your browser to `http://localhost:5000`

## Web Dashboard

The Flask-based web dashboard provides an interactive interface to view and manage your ServiceNow monitoring data.

**Features:**
- Real-time data refresh with a single click
- Summary statistics for filings and press releases
- Tabbed interface for easy navigation
- AI-generated summaries displayed inline
- Responsive design that works on mobile and desktop
- Direct links to original SEC filings and press releases

**Screenshots:**
- View all SEC filings (10-K, 10-Q, 8-K) with color-coded badges
- See press releases categorized as earnings or general news
- AI summaries displayed in an easy-to-read format
- One-click refresh to fetch the latest data

## Configuration

The monitor works out-of-the-box with just the `ANTHROPIC_API_KEY` environment variable set.

For advanced configuration, create a `config/config.yaml` file with:
- **Claude AI**: API key, model selection, number of items to summarize
- **Data Sources**: Enable/disable SEC filings, press releases, news
- **Output Settings**: Email digest, HTML dashboard
- **Microsoft Graph**: Credentials for internal document monitoring (future feature)

See `config/config.yaml.example` for all available options.

## Development Roadmap

- [x] Project structure
- [x] SEC EDGAR fetcher (10-K, 10-Q, 8-K)
- [x] Press release fetcher (Business Wire)
- [x] Claude AI summarization
  - [x] Context-aware prompts for different content types
  - [x] Earnings-specific analysis
  - [x] SEC filing analysis
- [x] Flask web dashboard
  - [x] Interactive UI with Bootstrap
  - [x] Real-time data refresh
  - [x] Summary statistics
  - [x] Tabbed interface for filings and releases
- [ ] News fetcher (NewsAPI integration)
- [ ] Email digest generator
- [ ] Microsoft Graph integration for internal docs
- [ ] Scheduling and automation

## License

MIT License
