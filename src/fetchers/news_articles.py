"""
News Articles Fetcher Module

Fetches news articles about ServiceNow from NewsAPI.org
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsArticleFetcher:
    """Fetches news articles about a company from NewsAPI."""

    BASE_URL = "https://newsapi.org/v2/everything"

    def __init__(self, api_key: str = None, company_name: str = "ServiceNow"):
        """
        Initialize the news article fetcher.

        Args:
            api_key: NewsAPI API key (if not provided, reads from NEWS_API_KEY env var)
            company_name: Name of the company to search for
        """
        self.api_key = api_key or os.environ.get("NEWS_API_KEY")
        if not self.api_key:
            logger.warning("No NewsAPI key provided. Set NEWS_API_KEY env var or pass api_key parameter")

        self.company_name = company_name

    def get_recent_articles(self,
                          keywords: List[str] = None,
                          days_back: int = 30,
                          language: str = "en",
                          sort_by: str = "publishedAt",
                          page_size: int = 50) -> List[Dict]:
        """
        Get recent news articles about the company.

        Args:
            keywords: List of keywords to search for (defaults to company name)
            days_back: Number of days to look back for articles
            language: Language code (default: "en")
            sort_by: Sort order: "publishedAt", "relevancy", or "popularity"
            page_size: Number of results per page (max 100)

        Returns:
            List of article dictionaries
        """
        if not self.api_key:
            logger.error("No API key available for NewsAPI")
            return []

        if keywords is None:
            keywords = [self.company_name]

        # Build search query (OR between keywords)
        query = " OR ".join(keywords)

        # Calculate date range
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        to_date = datetime.now().strftime("%Y-%m-%d")

        # Build request parameters
        params = {
            "q": query,
            "from": from_date,
            "to": to_date,
            "language": language,
            "sortBy": sort_by,
            "pageSize": min(page_size, 100),  # API max is 100
            "apiKey": self.api_key
        }

        try:
            logger.info(f"Fetching news articles for '{query}' from {from_date} to {to_date}")

            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get("status") != "ok":
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []

            articles = data.get("articles", [])

            # Transform to our standard format
            formatted_articles = []
            for article in articles:
                formatted = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "author": article.get("author", "Unknown"),
                    "published_at": article.get("publishedAt", ""),
                    "url_to_image": article.get("urlToImage", ""),
                    "company": self.company_name
                }

                # Parse published date for sorting
                try:
                    formatted["date"] = datetime.fromisoformat(
                        formatted["published_at"].replace("Z", "+00:00")
                    ).strftime("%Y-%m-%d")
                except:
                    formatted["date"] = formatted["published_at"][:10] if formatted["published_at"] else ""

                formatted_articles.append(formatted)

            logger.info(f"Found {len(formatted_articles)} news articles")
            return formatted_articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news articles: {e}")
            return []

    def fetch_article_content(self, url: str) -> Optional[str]:
        """
        Fetch the full content of an article from its URL.

        Note: NewsAPI provides limited content in the API response.
        For full content, you may need to scrape the article page.

        Args:
            url: URL of the article

        Returns:
            Article content text, or None if fetch fails
        """
        try:
            from bs4 import BeautifulSoup

            logger.info(f"Fetching article content from {url}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Try to find article content
            # This is a generic approach - may need customization per site
            article_body = soup.find('article') or soup.find('main') or soup.find('body')

            if article_body:
                text = article_body.get_text()

                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)

                logger.info(f"Fetched {len(text)} characters of content")
                return text
            else:
                logger.warning("Could not find article content in page")
                return None

        except Exception as e:
            logger.error(f"Error fetching article content: {e}")
            return None


def main():
    """Test the news article fetcher."""
    import sys

    # Check for API key
    api_key = os.environ.get("NEWS_API_KEY")
    if not api_key:
        print("Error: NEWS_API_KEY environment variable not set")
        print("Get a free API key from: https://newsapi.org/register")
        print("Then set it with: export NEWS_API_KEY='your-api-key'")
        sys.exit(1)

    fetcher = NewsArticleFetcher(api_key=api_key, company_name="ServiceNow")

    # Get articles from the last 30 days
    articles = fetcher.get_recent_articles(
        keywords=["ServiceNow", "NOW stock"],
        days_back=30,
        sort_by="publishedAt"
    )

    print(f"\nFound {len(articles)} recent news articles:\n")
    for article in articles[:10]:  # Show top 10
        print(f"{article['date']} - {article['title']}")
        print(f"  Source: {article['source']} | Author: {article['author']}")
        print(f"  {article['url']}")
        print()


if __name__ == "__main__":
    main()
