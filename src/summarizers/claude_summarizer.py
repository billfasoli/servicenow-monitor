"""
Claude AI Summarizer Module

Uses Anthropic's Claude API to generate intelligent summaries of:
- SEC filings (10-K, 10-Q, 8-K)
- Press releases
- News articles
"""

import os
from typing import Dict, List, Optional
import logging

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None
    logging.warning("anthropic package not installed. Install with: pip install anthropic")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeSummarizer:
    """Generates intelligent summaries using Claude AI."""

    # Prompt templates for different content types
    PROMPTS = {
        "10-K": """You are analyzing a 10-K annual report for {company}.

Please provide a concise executive summary (3-5 bullet points) covering:
- Key financial highlights (revenue, earnings, growth)
- Major business developments or strategic initiatives
- Significant risks or challenges mentioned
- Forward-looking statements or guidance

Content to summarize:
{content}

Format your response as clear, actionable bullet points.""",

        "10-Q": """You are analyzing a 10-Q quarterly report for {company}.

Please provide a concise summary (3-5 bullet points) covering:
- Quarterly financial performance (revenue, earnings, YoY/QoQ growth)
- Key business developments this quarter
- Notable risks or challenges
- Any guidance or forward-looking statements

Content to summarize:
{content}

Format your response as clear, actionable bullet points.""",

        "8-K": """You are analyzing an 8-K current report for {company}.

Please provide a concise summary (2-4 bullet points) of:
- The main event or announcement
- Financial impact (if disclosed)
- Strategic significance
- Key implications for the company

Content to summarize:
{content}

Format your response as clear, actionable bullet points.""",

        "press_release": """You are analyzing a press release from {company}.

Please provide a concise summary (2-4 bullet points) covering:
- Main announcement or news
- Key figures or metrics (if any)
- Strategic importance
- Implications for the company's business

Content to summarize:
{content}

Format your response as clear, actionable bullet points.""",

        "earnings": """You are analyzing an earnings announcement for {company}.

Please provide a concise summary (4-6 bullet points) covering:
- Revenue and earnings results vs. expectations
- YoY and QoQ growth rates
- Key business metrics and highlights
- Forward guidance
- Management commentary on outlook
- Notable concerns or risks

Content to summarize:
{content}

Format your response as clear, actionable bullet points.""",

        "general": """You are analyzing content about {company}.

Please provide a concise summary (3-5 bullet points) of the key information and its significance.

Content to summarize:
{content}

Format your response as clear, actionable bullet points."""
    }

    def __init__(self, api_key: str = None, model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize the Claude summarizer.

        Args:
            api_key: Anthropic API key (if not provided, reads from ANTHROPIC_API_KEY env var)
            model: Claude model to use
        """
        if Anthropic is None:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided. Set ANTHROPIC_API_KEY or pass api_key parameter")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        logger.info(f"Initialized Claude summarizer with model: {model}")

    def _get_prompt_template(self, content_type: str) -> str:
        """Get the appropriate prompt template for content type."""
        content_type = content_type.upper().replace("-", "_")

        # Map content types to prompt templates
        if content_type in ["10-K", "10_K"]:
            return self.PROMPTS["10-K"]
        elif content_type in ["10-Q", "10_Q"]:
            return self.PROMPTS["10-Q"]
        elif content_type in ["8-K", "8_K"]:
            return self.PROMPTS["8-K"]
        elif "EARNING" in content_type:
            return self.PROMPTS["earnings"]
        elif "PRESS" in content_type or "RELEASE" in content_type:
            return self.PROMPTS["press_release"]
        else:
            return self.PROMPTS["general"]

    def summarize(self,
                  content: str,
                  content_type: str = "general",
                  company_name: str = "ServiceNow",
                  max_tokens: int = 1000) -> str:
        """
        Generate a summary of the content.

        Args:
            content: The content to summarize
            content_type: Type of content (10-K, 10-Q, 8-K, press_release, earnings, etc.)
            company_name: Name of the company
            max_tokens: Maximum tokens for the response

        Returns:
            Summary text
        """
        # Truncate content if too long (keep first ~50k chars to stay within context limits)
        if len(content) > 50000:
            logger.warning(f"Content too long ({len(content)} chars), truncating to 50000 chars")
            content = content[:50000] + "\n\n[Content truncated...]"

        # Get appropriate prompt template
        template = self._get_prompt_template(content_type)
        prompt = template.format(company=company_name, content=content)

        try:
            logger.info(f"Generating summary for {content_type} ({len(content)} chars)")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            summary = response.content[0].text
            logger.info(f"Generated summary ({len(summary)} chars)")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"

    def summarize_batch(self,
                       items: List[Dict],
                       content_key: str = "content",
                       type_key: str = "type") -> List[Dict]:
        """
        Summarize multiple items in batch.

        Args:
            items: List of dictionaries containing content to summarize
            content_key: Key in dict containing the content
            type_key: Key in dict containing the content type

        Returns:
            List of items with added 'summary' key
        """
        results = []

        for i, item in enumerate(items):
            logger.info(f"Summarizing item {i+1}/{len(items)}")

            content = item.get(content_key, "")
            content_type = item.get(type_key, "general")

            if not content:
                logger.warning(f"Item {i+1} has no content, skipping")
                item["summary"] = "No content available for summarization"
                results.append(item)
                continue

            summary = self.summarize(
                content=content,
                content_type=content_type,
                company_name=item.get("company", "ServiceNow")
            )

            item["summary"] = summary
            results.append(item)

        return results


def main():
    """Test the Claude summarizer."""
    import sys

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-api-key'")
        sys.exit(1)

    summarizer = ClaudeSummarizer(api_key=api_key)

    # Test with a sample press release
    test_content = """
    ServiceNow Reports Second Quarter 2025 Financial Results

    Subscription revenues of $2.6 billion, representing 24% year-over-year growth
    Subscription billings of $2.9 billion, representing 25% year-over-year growth
    Current remaining performance obligations (cRPO) of approximately $9.4 billion,
    representing 23% year-over-year growth

    SANTA CLARA, Calif., July 24, 2025 — ServiceNow (NYSE: NOW), the AI platform for
    business transformation, today reported financial results for its second quarter
    ended June 30, 2025.

    "We delivered another outstanding quarter with strong subscription revenue growth
    and robust demand for our AI-powered platform," said Bill McDermott, president and
    chief executive officer.
    """

    print("Testing Claude Summarizer...")
    print("=" * 60)

    summary = summarizer.summarize(
        content=test_content,
        content_type="earnings",
        company_name="ServiceNow"
    )

    print("\nSummary:")
    print(summary)
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
