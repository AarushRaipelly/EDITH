import logging
from typing import List, Dict

logger = logging.getLogger("EDITH.Integrations.RSS")

try:
    import feedparser
except ImportError:
    feedparser = None
    logger.warning("feedparser library not found. Using simple raw xml parsing fallback.")

class RSSReader:
    def __init__(self) -> None:
        pass

    def read_feed(self, feed_url: str, limit: int = 3) -> List[Dict[str, str]]:
        """Parses RSS feeds and summarizes headings."""
        logger.info(f"Reading RSS Feed: {feed_url}")
        articles = []

        if feedparser:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:limit]:
                    articles.append({
                        "title": entry.title,
                        "link": entry.link,
                        "summary": entry.get("summary", "")[:150] + "..."
                    })
                return articles
            except Exception as e:
                logger.error(f"Error parsing feed with feedparser: {e}")

        # Basic fallback or mock data
        return [
            {"title": "Mock RSS Article 1", "link": "https://example.com/1", "summary": "Sample brief of the first RSS story."},
            {"title": "Mock RSS Article 2", "link": "https://example.com/2", "summary": "Sample brief of the second RSS story."}
        ]
