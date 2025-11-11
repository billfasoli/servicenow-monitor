"""
ServiceNow Monitor - Main Orchestrator

Coordinates fetching, summarization, and output of ServiceNow company information.
"""

import os
import sys
import yaml
import logging
import argparse
from datetime import datetime
from typing import Dict, List

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetchers.sec_edgar import SECEdgarFetcher
from fetchers.press_releases import PressReleaseFetcher
from fetchers.news_articles import NewsArticleFetcher
from secrets import SecretsManager

try:
    from summarizers.claude_summarizer import ClaudeSummarizer
    SUMMARIZER_AVAILABLE = True
except ImportError:
    SUMMARIZER_AVAILABLE = False
    logging.warning("Claude summarizer not available - install anthropic package")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceNowMonitor:
    """Main orchestrator for ServiceNow monitoring."""

    def __init__(self, config_path: str = None, use_1password: bool = True):
        """
        Initialize the ServiceNow Monitor.

        Args:
            config_path: Path to the configuration file
            use_1password: Whether to use 1Password CLI for secrets (default: True)
        """
        self.config = self._load_config(config_path)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "sec_filings": [],
            "press_releases": [],
            "news_articles": []
        }

        # Initialize secrets manager
        self.secrets_manager = SecretsManager(use_1password=use_1password)

        # Initialize summarizer if enabled and available
        self.summarizer = None
        if SUMMARIZER_AVAILABLE and self.config.get("claude", {}).get("enabled", False):
            # Try to get API key from 1Password, then config, then env var
            api_key = self.secrets_manager.get_secret(
                secret_name="Claude API Key",
                env_var_name="ANTHROPIC_API_KEY",
                item_name="Anthropic API Key"
            )

            if not api_key:
                api_key = self.config.get("claude", {}).get("api_key")

            if api_key:
                model = self.config.get("claude", {}).get("model", "claude-sonnet-4-5-20250929")
                self.summarizer = ClaudeSummarizer(api_key=api_key, model=model)
                logger.info("Claude summarizer initialized")
            else:
                logger.warning("Claude API key not found - summarization disabled")

    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            # Default config path
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "config",
                "config.yaml"
            )

        if not os.path.exists(config_path):
            logger.warning(f"Config file not found: {config_path}")
            logger.info("Using default configuration")
            return self._get_default_config()

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Return default configuration."""
        return {
            "company": {
                "name": "ServiceNow",
                "ticker": "NOW",
                "cik": "0001373715"
            },
            "sources": {
                "sec_filings": {
                    "enabled": True,
                    "types": ["10-K", "10-Q", "8-K"]
                },
                "press_releases": {
                    "enabled": True
                }
            }
        }

    def fetch_sec_filings(self, days_back: int = 90) -> List[Dict]:
        """
        Fetch SEC filings.

        Args:
            days_back: Number of days to look back

        Returns:
            List of SEC filing dictionaries
        """
        if not self.config.get("sources", {}).get("sec_filings", {}).get("enabled", True):
            logger.info("SEC filings fetching is disabled")
            return []

        logger.info("Fetching SEC filings...")

        company = self.config.get("company", {})
        cik = company.get("cik", "0001373715")
        name = company.get("name", "ServiceNow")

        # Get email from config if available
        email = self.config.get("contact_email", "your-email@example.com")

        fetcher = SECEdgarFetcher(cik=cik, company_name=name, email=email)

        filing_types = self.config.get("sources", {}).get("sec_filings", {}).get("types", ["10-K", "10-Q"])

        filings = fetcher.get_recent_filings(filing_types=filing_types, days_back=days_back)

        # Add summarization if enabled
        if self.summarizer and filings:
            summarize_count = self.config.get("claude", {}).get("summarize_filings_count", 3)
            logger.info(f"Summarizing top {summarize_count} filings...")

            for i, filing in enumerate(filings[:summarize_count]):
                logger.info(f"Fetching content for {filing['form_type']} from {filing['filing_date']}")

                # Fetch filing content
                content = fetcher.fetch_filing_content(filing['filing_url'])

                if content:
                    # Generate summary
                    summary = self.summarizer.summarize(
                        content=content,
                        content_type=filing['form_type'],
                        company_name=name
                    )
                    filing['summary'] = summary
                    filing['content_fetched'] = True
                else:
                    filing['summary'] = "Unable to fetch filing content"
                    filing['content_fetched'] = False

        self.results["sec_filings"] = filings
        return filings

    def fetch_press_releases(self, days_back: int = 30) -> List[Dict]:
        """
        Fetch press releases.

        Args:
            days_back: Number of days to look back

        Returns:
            List of press release dictionaries
        """
        if not self.config.get("sources", {}).get("press_releases", {}).get("enabled", True):
            logger.info("Press release fetching is disabled")
            return []

        logger.info("Fetching press releases...")

        company_name = self.config.get("company", {}).get("name", "ServiceNow")
        fetcher = PressReleaseFetcher(company_name=company_name)

        releases = fetcher.get_recent_press_releases(days_back=days_back)

        # Add summarization if enabled
        if self.summarizer and releases:
            summarize_count = self.config.get("claude", {}).get("summarize_releases_count", 5)
            logger.info(f"Summarizing top {summarize_count} press releases...")

            for i, release in enumerate(releases[:summarize_count]):
                logger.info(f"Fetching content for press release: {release['title']}")

                # Fetch press release content
                content = fetcher.fetch_press_release_content(release['url'])

                if content:
                    # Generate summary
                    content_type = "earnings" if release['category'] == "earnings" else "press_release"
                    summary = self.summarizer.summarize(
                        content=content,
                        content_type=content_type,
                        company_name=company_name
                    )
                    release['summary'] = summary
                    release['content_fetched'] = True
                else:
                    # Use existing summary from RSS if available
                    if not release.get('summary'):
                        release['summary'] = "Unable to fetch press release content"
                    release['content_fetched'] = False

        self.results["press_releases"] = releases
        return releases

    def fetch_news_articles(self, days_back: int = 30) -> List[Dict]:
        """
        Fetch news articles.

        Args:
            days_back: Number of days to look back

        Returns:
            List of news article dictionaries
        """
        if not self.config.get("sources", {}).get("news", {}).get("enabled", False):
            logger.info("News article fetching is disabled")
            return []

        logger.info("Fetching news articles...")

        company_name = self.config.get("company", {}).get("name", "ServiceNow")

        # Try to get API key from 1Password, then config, then env var
        api_key = self.secrets_manager.get_secret(
            secret_name="NewsAPI Key",
            env_var_name="NEWS_API_KEY",
            item_name="NewsAPI"
        )

        if not api_key:
            api_key = self.config.get("sources", {}).get("news", {}).get("api_key")

        if not api_key:
            logger.warning("NewsAPI key not found - news fetching disabled")
            return []

        fetcher = NewsArticleFetcher(api_key=api_key, company_name=company_name)

        # Get keywords from config
        keywords = self.config.get("sources", {}).get("news", {}).get("keywords", [company_name])

        articles = fetcher.get_recent_articles(
            keywords=keywords,
            days_back=days_back,
            sort_by="publishedAt"
        )

        # Add summarization if enabled
        if self.summarizer and articles:
            summarize_count = self.config.get("claude", {}).get("summarize_articles_count", 5)
            logger.info(f"Summarizing top {summarize_count} news articles...")

            for i, article in enumerate(articles[:summarize_count]):
                logger.info(f"Processing article: {article['title']}")

                # Use description and content from NewsAPI
                content = f"{article.get('description', '')}\n\n{article.get('content', '')}"

                if content.strip():
                    # Generate summary
                    summary = self.summarizer.summarize(
                        content=content,
                        content_type="general",
                        company_name=company_name
                    )
                    article['summary'] = summary
                    article['content_fetched'] = True
                else:
                    article['summary'] = article.get('description', 'No summary available')
                    article['content_fetched'] = False

        self.results["news_articles"] = articles
        return articles

    def run(self, days_back: int = None, filings_days: int = None,
            releases_days: int = None, articles_days: int = None):
        """
        Run the complete monitoring cycle.

        Args:
            days_back: Number of days to look back for all sources (overrides individual settings)
            filings_days: Number of days to look back for SEC filings (default: 90)
            releases_days: Number of days to look back for press releases (default: 60)
            articles_days: Number of days to look back for news articles (default: 30)
        """
        # Apply universal days_back if provided
        if days_back is not None:
            filings_days = releases_days = articles_days = days_back

        # Use defaults if not specified
        filings_days = filings_days or 90
        releases_days = releases_days or 60
        articles_days = articles_days or 30

        logger.info("=" * 60)
        logger.info("ServiceNow Monitor - Starting")
        logger.info("=" * 60)
        logger.info(f"Time periods: Filings={filings_days}d, Releases={releases_days}d, Articles={articles_days}d")

        # Fetch SEC filings
        filings = self.fetch_sec_filings(days_back=filings_days)
        logger.info(f"Found {len(filings)} SEC filings")

        # Fetch press releases
        releases = self.fetch_press_releases(days_back=releases_days)
        logger.info(f"Found {len(releases)} press releases")

        # Fetch news articles
        articles = self.fetch_news_articles(days_back=articles_days)
        logger.info(f"Found {len(articles)} news articles")

        # Print summary
        self.print_summary()

        logger.info("=" * 60)
        logger.info("ServiceNow Monitor - Complete")
        logger.info("=" * 60)

    def print_summary(self):
        """Print a summary of fetched data."""
        print("\n" + "=" * 60)
        print("SERVICENOW MONITOR - SUMMARY")
        print("=" * 60)

        # SEC Filings Summary
        print("\n📄 SEC FILINGS")
        print("-" * 60)
        if self.results["sec_filings"]:
            for filing in self.results["sec_filings"][:5]:  # Show top 5
                print(f"\n{filing['filing_date']} - {filing['form_type']}")
                print(f"  {filing['description']}")
                if filing.get('summary'):
                    print(f"\n  AI SUMMARY:")
                    # Indent the summary
                    for line in filing['summary'].split('\n'):
                        if line.strip():
                            print(f"  {line}")
                print(f"\n  {filing['filing_url']}")
        else:
            print("No recent SEC filings found.")

        # Press Releases Summary
        print("\n\n📰 PRESS RELEASES")
        print("-" * 60)
        if self.results["press_releases"]:
            for release in self.results["press_releases"][:5]:  # Show top 5
                print(f"\n{release['date']} - {release['title']}")
                print(f"  Category: {release['category']} | Source: {release['source']}")
                if release.get('summary'):
                    print(f"\n  AI SUMMARY:")
                    # Indent the summary
                    for line in release['summary'].split('\n'):
                        if line.strip():
                            print(f"  {line}")
                print(f"\n  {release['url']}")
        else:
            print("No recent press releases found.")

        # News Articles Summary
        print("\n\n📰 NEWS ARTICLES")
        print("-" * 60)
        if self.results["news_articles"]:
            for article in self.results["news_articles"][:5]:  # Show top 5
                print(f"\n{article['date']} - {article['title']}")
                print(f"  Source: {article['source']} | Author: {article['author']}")
                if article.get('summary'):
                    print(f"\n  AI SUMMARY:")
                    # Indent the summary
                    for line in article['summary'].split('\n'):
                        if line.strip():
                            print(f"  {line}")
                print(f"\n  {article['url']}")
        else:
            print("No recent news articles found.")

        print("\n" + "=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='ServiceNow Monitor - Track SEC filings, press releases, and news articles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get updates from the last week
  python src/main.py --period week

  # Get updates from the last month
  python src/main.py --period month

  # Get updates from the last quarter (90 days)
  python src/main.py --period quarter

  # Custom: last 14 days
  python src/main.py --days 14

  # Custom periods for each source
  python src/main.py --filings-days 30 --articles-days 7

  # Default (no arguments): filings=90d, releases=60d, articles=30d
  python src/main.py
        """
    )

    parser.add_argument(
        '--period',
        choices=['week', 'month', 'quarter', 'year'],
        help='Convenient time period presets (week=7d, month=30d, quarter=90d, year=365d)'
    )

    parser.add_argument(
        '--days',
        type=int,
        help='Number of days to look back for all sources (overrides --period)'
    )

    parser.add_argument(
        '--filings-days',
        type=int,
        help='Number of days to look back for SEC filings (default: 90)'
    )

    parser.add_argument(
        '--releases-days',
        type=int,
        help='Number of days to look back for press releases (default: 60)'
    )

    parser.add_argument(
        '--articles-days',
        type=int,
        help='Number of days to look back for news articles (default: 30)'
    )

    args = parser.parse_args()

    # Convert period to days
    period_map = {
        'week': 7,
        'month': 30,
        'quarter': 90,
        'year': 365
    }

    days_back = None
    if args.period:
        days_back = period_map[args.period]
    elif args.days:
        days_back = args.days

    # Run the monitor
    monitor = ServiceNowMonitor()
    monitor.run(
        days_back=days_back,
        filings_days=args.filings_days,
        releases_days=args.releases_days,
        articles_days=args.articles_days
    )


if __name__ == "__main__":
    main()
