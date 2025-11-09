"""
Press Release Fetcher Module

Fetches ServiceNow press releases from multiple sources:
- ServiceNow's official press room
- Business Wire RSS feed
- Investor Relations pages
"""

import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PressReleaseFetcher:
    """Fetches press releases for ServiceNow from multiple sources."""

    # Business Wire RSS feed for ServiceNow
    BUSINESSWIRE_RSS = "https://www.businesswire.com/portal/site/home/search/?searchType=news&searchTerm=ServiceNow&searchPage=1"

    def __init__(self, company_name: str = "ServiceNow"):
        """
        Initialize the press release fetcher.

        Args:
            company_name: Name of the company to search for
        """
        self.company_name = company_name
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def fetch_from_businesswire(self, days_back: int = 30) -> List[Dict]:
        """
        Fetch press releases from Business Wire RSS feed.

        Args:
            days_back: Number of days to look back for press releases

        Returns:
            List of press release dictionaries
        """
        press_releases = []

        # Business Wire RSS URL for ServiceNow
        rss_url = "https://www.businesswire.com/portal/site/home/template.PAGE/search/?javax.portlet.tpst=1bc8e628b296462093aaf0c12733ba01&javax.portlet.prp_1bc8e628b296462093aaf0c12733ba01=rss%3Dtrue%26topicCategoryId%3D%26topicTypeId%3D%26topicSubjectId%3D%26primarySubjectId%3D%26searchTerm%3DServiceNow%26advancedSearch%3Dfalse%26sortBy%3D1%26"

        try:
            logger.info(f"Fetching Business Wire RSS feed for {self.company_name}")

            # Parse RSS feed
            feed = feedparser.parse(rss_url)

            cutoff_date = datetime.now() - timedelta(days=days_back)

            for entry in feed.entries:
                # Parse the published date
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                except:
                    logger.warning(f"Could not parse date for entry: {entry.get('title', 'Unknown')}")
                    continue

                # Check if within date range
                if pub_date < cutoff_date:
                    continue

                # Extract press release info
                press_release = {
                    "title": entry.get("title", ""),
                    "date": pub_date.strftime("%Y-%m-%d"),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "source": "Business Wire",
                    "company": self.company_name
                }

                # Check if it's an earnings or financial release
                title_lower = press_release["title"].lower()
                if any(keyword in title_lower for keyword in ["earnings", "financial results", "quarter", "q1", "q2", "q3", "q4"]):
                    press_release["category"] = "earnings"
                else:
                    press_release["category"] = "general"

                press_releases.append(press_release)

            logger.info(f"Found {len(press_releases)} press releases from Business Wire")

        except Exception as e:
            logger.error(f"Error fetching Business Wire RSS: {e}")

        return press_releases

    def fetch_from_servicenow_ir(self, days_back: int = 30) -> List[Dict]:
        """
        Fetch press releases from ServiceNow Investor Relations page.

        Args:
            days_back: Number of days to look back for press releases

        Returns:
            List of press release dictionaries
        """
        press_releases = []

        # ServiceNow IR financials page
        ir_url = "https://www.servicenow.com/company/investor-relations/financials.html"

        try:
            logger.info(f"Fetching ServiceNow IR page: {ir_url}")

            response = requests.get(ir_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for links to quarterly results
            # This is a heuristic approach - may need adjustment based on actual page structure
            links = soup.find_all('a', href=re.compile(r'(financial|quarter|earnings)', re.I))

            cutoff_date = datetime.now() - timedelta(days=days_back)

            for link in links:
                href = link.get('href', '')
                title = link.get_text(strip=True)

                if not title or not href:
                    continue

                # Make absolute URL
                if href.startswith('/'):
                    href = f"https://www.servicenow.com{href}"

                # Try to extract date from title or URL
                date_match = re.search(r'(20\d{2})', title)
                if date_match:
                    year = date_match.group(1)
                    # Use current date as fallback
                    date_str = f"{year}-01-01"
                else:
                    date_str = datetime.now().strftime("%Y-%m-%d")

                press_release = {
                    "title": title,
                    "date": date_str,
                    "url": href,
                    "summary": "",
                    "source": "ServiceNow IR",
                    "company": self.company_name,
                    "category": "earnings"
                }

                press_releases.append(press_release)

            logger.info(f"Found {len(press_releases)} press releases from ServiceNow IR")

        except Exception as e:
            logger.error(f"Error fetching ServiceNow IR page: {e}")

        return press_releases

    def get_recent_press_releases(self, days_back: int = 30) -> List[Dict]:
        """
        Get recent press releases from all sources.

        Args:
            days_back: Number of days to look back for press releases

        Returns:
            List of press release dictionaries, sorted by date (newest first)
        """
        all_releases = []

        # Fetch from Business Wire
        all_releases.extend(self.fetch_from_businesswire(days_back))

        # Fetch from ServiceNow IR (commented out by default due to potential blocking)
        # all_releases.extend(self.fetch_from_servicenow_ir(days_back))

        # Remove duplicates based on title
        seen_titles = set()
        unique_releases = []

        for release in all_releases:
            if release["title"] not in seen_titles:
                seen_titles.add(release["title"])
                unique_releases.append(release)

        # Sort by date (newest first)
        unique_releases.sort(key=lambda x: x["date"], reverse=True)

        logger.info(f"Total unique press releases: {len(unique_releases)}")
        return unique_releases


def main():
    """Test the press release fetcher."""
    fetcher = PressReleaseFetcher(company_name="ServiceNow")

    # Get press releases from the last 60 days
    releases = fetcher.get_recent_press_releases(days_back=60)

    print(f"\nFound {len(releases)} recent press releases:\n")
    for release in releases:
        print(f"{release['date']} - {release['title']}")
        print(f"  Source: {release['source']} | Category: {release['category']}")
        print(f"  URL: {release['url']}")
        print()


if __name__ == "__main__":
    main()
