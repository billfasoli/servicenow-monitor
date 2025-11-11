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

4. (Optional) Set your NewsAPI key for news monitoring:
```bash
export NEWS_API_KEY='your-newsapi-key-here'
```
Get a free API key at [https://newsapi.org/register](https://newsapi.org/register)

5. (Optional) Configure your settings:
```bash
cp config/config.yaml.example config/config.yaml
# Edit config.yaml to customize behavior
```

6. Run the monitor:

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

## Configuration

The monitor works out-of-the-box with just the `ANTHROPIC_API_KEY` environment variable set.

For advanced configuration, create a `config/config.yaml` file with:
- **Claude AI**: API key, model selection, number of items to summarize
- **Data Sources**: Enable/disable SEC filings, press releases, news articles
- **News Monitoring**: NewsAPI key, custom keywords for monitoring
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
  - [x] Tabbed interface for filings, releases, and news
- [x] News fetcher (NewsAPI integration)
  - [x] Fetch articles from 150,000+ sources
  - [x] Customizable keywords
  - [x] AI summarization
  - [x] Images and metadata support
- [ ] Email digest generator
- [ ] Microsoft Graph integration for internal docs
- [ ] Scheduling and automation

## License

MIT License
