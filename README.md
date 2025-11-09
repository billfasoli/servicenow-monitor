# ServiceNow Monitor

A Python-based monitoring and summarization tool for staying aware of everything happening at ServiceNow.

## Features

- **SEC Filings**: Automatically fetch and summarize 10-K and 10-Q reports
- **News Monitoring**: Track news articles about ServiceNow from multiple sources
- **Press Releases**: Monitor official ServiceNow press releases
- **AI Summarization**: Leverage Claude AI to generate concise summaries
- **Internal Documents** (Coming soon): Monitor SharePoint and email attachments

## Project Structure

```
servicenow-monitor/
├── config/          # Configuration files
├── src/
│   ├── fetchers/    # Data fetching modules (SEC, news, etc.)
│   ├── summarizers/ # AI summarization using Claude
│   ├── outputs/     # Output generators (email, HTML, etc.)
│   └── main.py      # Main orchestrator
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

3. Configure your settings:
```bash
cp config/config.yaml.example config/config.yaml
# Edit config.yaml with your API keys and preferences
```

4. Run the monitor:
```bash
python src/main.py
```

## Configuration

Create a `config/config.yaml` file with your settings:
- Claude API key for summarization
- News API credentials
- Email settings for digest delivery
- Microsoft Graph API credentials (for internal documents)

## Development Roadmap

- [x] Project structure
- [ ] SEC EDGAR fetcher
- [ ] News fetcher
- [ ] Press release fetcher
- [ ] Claude AI summarization
- [ ] Email digest generator
- [ ] HTML dashboard
- [ ] Microsoft Graph integration for internal docs
- [ ] Scheduling and automation

## License

MIT License
