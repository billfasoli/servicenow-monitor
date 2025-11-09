"""
SEC EDGAR Fetcher Module

Fetches SEC filings (10-K, 10-Q, 8-K) for ServiceNow using the SEC EDGAR API.
"""

import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SECEdgarFetcher:
    """Fetches SEC filings for a company using the SEC EDGAR API."""

    BASE_URL = "https://data.sec.gov"

    def __init__(self, cik: str, company_name: str = "ServiceNow", email: str = ""):
        """
        Initialize the SEC EDGAR fetcher.

        Args:
            cik: Central Index Key for the company (e.g., "0001373715")
            company_name: Name of the company for the User-Agent
            email: Email address for the User-Agent (SEC requires identifying info)
        """
        self.cik = self._format_cik(cik)
        self.company_name = company_name

        # SEC requires a User-Agent header with contact info
        self.headers = {
            "User-Agent": f"{company_name} Monitor Tool ({email})",
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov"
        }

    def _format_cik(self, cik: str) -> str:
        """Format CIK to 10 digits with leading zeros."""
        return cik.strip().replace("CIK", "").zfill(10)

    def _make_request(self, url: str) -> Optional[Dict]:
        """
        Make a request to the SEC API with rate limiting.

        Args:
            url: The URL to fetch

        Returns:
            JSON response as dict, or None if request fails
        """
        try:
            # SEC rate limits: 10 requests per second
            time.sleep(0.1)

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def get_recent_filings(self,
                          filing_types: List[str] = ["10-K", "10-Q", "8-K"],
                          days_back: int = 90) -> List[Dict]:
        """
        Get recent filings for the company.

        Args:
            filing_types: List of filing types to fetch (e.g., ["10-K", "10-Q"])
            days_back: Number of days to look back for filings

        Returns:
            List of filing dictionaries with metadata
        """
        url = f"{self.BASE_URL}/submissions/CIK{self.cik}.json"

        logger.info(f"Fetching filings from {url}")
        data = self._make_request(url)

        if not data:
            logger.error("Failed to fetch submissions data")
            return []

        # Extract recent filings
        filings = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

        recent_filings = data.get("filings", {}).get("recent", {})

        # The API returns parallel arrays for filing data
        form_types = recent_filings.get("form", [])
        filing_dates = recent_filings.get("filingDate", [])
        accession_numbers = recent_filings.get("accessionNumber", [])
        primary_documents = recent_filings.get("primaryDocument", [])
        descriptions = recent_filings.get("primaryDocDescription", [])

        for i in range(len(form_types)):
            form_type = form_types[i]
            filing_date_str = filing_dates[i]

            # Check if this filing type is requested
            if form_type not in filing_types:
                continue

            # Parse filing date
            filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d")

            # Check if within date range
            if filing_date < cutoff_date:
                continue

            # Build filing URL
            accession = accession_numbers[i].replace("-", "")
            primary_doc = primary_documents[i]
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/{accession}/{primary_doc}"

            filing_info = {
                "form_type": form_type,
                "filing_date": filing_date_str,
                "accession_number": accession_numbers[i],
                "description": descriptions[i] if i < len(descriptions) else "",
                "filing_url": filing_url,
                "company": self.company_name,
                "cik": self.cik
            }

            filings.append(filing_info)

        logger.info(f"Found {len(filings)} recent filings")
        return filings

    def get_filing_details(self, accession_number: str) -> Optional[Dict]:
        """
        Get detailed information about a specific filing.

        Args:
            accession_number: The accession number of the filing

        Returns:
            Dictionary with filing details
        """
        # Remove dashes from accession number for URL
        accession = accession_number.replace("-", "")
        url = f"https://www.sec.gov/cgi-bin/viewer?action=view&cik={self.cik}&accession_number={accession_number}&xbrl_type=v"

        return {
            "accession_number": accession_number,
            "viewer_url": url,
            "company": self.company_name
        }


def main():
    """Test the SEC EDGAR fetcher."""
    # ServiceNow CIK: 0001373715
    fetcher = SECEdgarFetcher(
        cik="0001373715",
        company_name="ServiceNow",
        email="your-email@example.com"  # Replace with your email
    )

    # Get recent 10-K and 10-Q filings from the last 90 days
    filings = fetcher.get_recent_filings(
        filing_types=["10-K", "10-Q", "8-K"],
        days_back=90
    )

    print(f"\nFound {len(filings)} recent filings:\n")
    for filing in filings:
        print(f"{filing['filing_date']} - {filing['form_type']}")
        print(f"  URL: {filing['filing_url']}")
        print()


if __name__ == "__main__":
    main()
