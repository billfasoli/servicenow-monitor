"""
Flask Web Dashboard for ServiceNow Monitor

A web interface to view SEC filings, press releases, and AI-generated summaries.
"""

from flask import Flask, render_template, jsonify
import os
import sys
from datetime import datetime
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import ServiceNowMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variable to cache the monitor data
cached_data = {
    "last_updated": None,
    "sec_filings": [],
    "press_releases": [],
    "news_articles": []
}


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html',
                         last_updated=cached_data.get('last_updated'),
                         has_data=bool(cached_data.get('sec_filings') or cached_data.get('press_releases') or cached_data.get('news_articles')))


@app.route('/api/refresh')
def refresh_data():
    """Refresh data from all sources."""
    try:
        logger.info("Refreshing data...")

        # Create monitor and fetch data
        monitor = ServiceNowMonitor()

        # Fetch SEC filings
        filings = monitor.fetch_sec_filings(days_back=90)

        # Fetch press releases
        releases = monitor.fetch_press_releases(days_back=60)

        # Fetch news articles
        articles = monitor.fetch_news_articles(days_back=30)

        # Update cache
        cached_data['sec_filings'] = filings
        cached_data['press_releases'] = releases
        cached_data['news_articles'] = articles
        cached_data['last_updated'] = datetime.now().isoformat()

        logger.info(f"Refresh complete: {len(filings)} filings, {len(releases)} releases, {len(articles)} articles")

        return jsonify({
            'status': 'success',
            'message': f'Fetched {len(filings)} filings, {len(releases)} press releases, and {len(articles)} news articles',
            'last_updated': cached_data['last_updated']
        })

    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/filings')
def get_filings():
    """Get SEC filings data."""
    return jsonify({
        'filings': cached_data.get('sec_filings', []),
        'last_updated': cached_data.get('last_updated')
    })


@app.route('/api/releases')
def get_releases():
    """Get press releases data."""
    return jsonify({
        'releases': cached_data.get('press_releases', []),
        'last_updated': cached_data.get('last_updated')
    })


@app.route('/api/articles')
def get_articles():
    """Get news articles data."""
    return jsonify({
        'articles': cached_data.get('news_articles', []),
        'last_updated': cached_data.get('last_updated')
    })


@app.route('/api/summary')
def get_summary():
    """Get summary statistics."""
    filings = cached_data.get('sec_filings', [])
    releases = cached_data.get('press_releases', [])
    articles = cached_data.get('news_articles', [])

    # Count items with summaries
    filings_with_summaries = sum(1 for f in filings if f.get('summary'))
    releases_with_summaries = sum(1 for r in releases if r.get('summary'))
    articles_with_summaries = sum(1 for a in articles if a.get('summary'))

    return jsonify({
        'total_filings': len(filings),
        'total_releases': len(releases),
        'total_articles': len(articles),
        'filings_with_summaries': filings_with_summaries,
        'releases_with_summaries': releases_with_summaries,
        'articles_with_summaries': articles_with_summaries,
        'last_updated': cached_data.get('last_updated')
    })


def main():
    """Run the Flask development server."""
    print("\n" + "=" * 60)
    print("ServiceNow Monitor - Web Dashboard")
    print("=" * 60)
    print("\nStarting Flask server...")
    print("Dashboard will be available at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
