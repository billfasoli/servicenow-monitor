"""
ServiceNow Monitor - Main Orchestrator

Coordinates fetching, summarization, and output of ServiceNow company information.
"""

import os
import sys
import yaml
import logging
from datetime import datetime
from typing import Dict, List

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetchers.sec_edgar import SECEdgarFetcher
from fetchers.press_releases import PressReleaseFetcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceNowMonitor:
    """Main orchestrator for ServiceNow monitoring."""

    def __init__(self, config_path: str = None):
        """
        Initialize the ServiceNow Monitor.

        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "sec_filings": [],
            "press_releases": [],
            "news_articles": []
        }

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

        self.results["press_releases"] = releases
        return releases

    def run(self):
        """Run the complete monitoring cycle."""
        logger.info("=" * 60)
        logger.info("ServiceNow Monitor - Starting")
        logger.info("=" * 60)

        # Fetch SEC filings
        filings = self.fetch_sec_filings(days_back=90)
        logger.info(f"Found {len(filings)} SEC filings")

        # Fetch press releases
        releases = self.fetch_press_releases(days_back=60)
        logger.info(f"Found {len(releases)} press releases")

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
                print(f"  {filing['filing_url']}")
        else:
            print("No recent SEC filings found.")

        # Press Releases Summary
        print("\n\n📰 PRESS RELEASES")
        print("-" * 60)
        if self.results["press_releases"]:
            for release in self.results["press_releases"][:5]:  # Show top 5
                print(f"\n{release['date']} - {release['title']}")
                print(f"  Category: {release['category']} | Source: {release['source']}")
                print(f"  {release['url']}")
        else:
            print("No recent press releases found.")

        print("\n" + "=" * 60)


def main():
    """Main entry point."""
    monitor = ServiceNowMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
