import feedparser
import json
import sys
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "articles.json"

# Security-focused RSS feeds (ENISA feed removed due to parsing issues)
DEFAULT_FEEDS = [
    "https://www.kyberturvallisuuskeskus.fi/feed/rss/fi",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.securityweek.com/feed/",
]

# Articles older than 30 days are filtered out
DAYS_TO_KEEP = 30


def parse_published_date(date_string: str) -> Optional[datetime]:
    """
    Parse RSS article date string to datetime object.

    Handles both timezone-aware and timezone-naive dates safely.
    Returns None if date cannot be parsed.

    Args:
        date_string: RFC 2822 formatted date string from RSS feed

    Returns:
        datetime object with UTC timezone, or None if parsing fails
    """
    if not date_string:
        return None

    try:
        # Try parsing RFC 2822 format (standard RSS format)
        dt = parsedate_to_datetime(date_string)

        # Ensure datetime is timezone-aware by converting to UTC
        if dt.tzinfo is None:
            # If timezone-naive, assume UTC
            dt = dt.replace(tzinfo=timezone.utc)

        return dt
    except (TypeError, ValueError):
        return None


def is_recent_article(published_date: Optional[datetime]) -> bool:
    """
    Check if article is recent (published within DAYS_TO_KEEP).

    Args:
        published_date: datetime object or None

    Returns:
        True if article is within 30 days, False otherwise
    """
    if published_date is None:
        return False

    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(days=DAYS_TO_KEEP)

    return published_date >= cutoff_date


def deduplicate_articles(articles: list[dict]) -> list[dict]:
    """
    Remove duplicate articles based on link.

    Keeps first occurrence of each link, discards duplicates.

    Args:
        articles: List of article dictionaries

    Returns:
        List of articles with duplicates removed
    """
    seen_links = set()
    unique_articles = []

    for article in articles:
        link = article.get("link", "")

        # Only add if link hasn't been seen before
        if link and link not in seen_links:
            seen_links.add(link)
            unique_articles.append(article)

    return unique_articles


def fetch_articles(feed_urls: list[str]) -> list[dict]:
    """
    Fetch and parse articles from RSS feeds with filtering.

    - Parses published dates with timezone handling
    - Filters articles older than 30 days
    - Discards articles with unparseable dates
    """
    articles = []

    for feed_url in feed_urls:
        try:
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                print(f"Warning: Feed {feed_url} has parsing issues", file=sys.stderr)

            source_name = feed.feed.get("title", feed_url)

            for entry in feed.entries:
                # Get date string from either 'published' or 'updated' field
                date_string = entry.get("published") or entry.get("updated", "")

                # Parse the date string to datetime object
                published_date = parse_published_date(date_string)

                # Skip articles with unparseable dates
                if published_date is None:
                    continue

                # Skip articles older than 30 days
                if not is_recent_article(published_date):
                    continue

                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": date_string,
                    "source": source_name,
                    "summary": entry.get("summary") or entry.get("description", ""),
                    "feed_url": feed_url,
                })

        except Exception as e:
            print(f"Error processing feed {feed_url}: {e}", file=sys.stderr)

    return articles


def save_articles(articles: list[dict], output_path: Path = DEFAULT_OUTPUT) -> None:
    """
    Save articles to JSON file.

    Creates output directory if needed. Always saves to project root relative path.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(articles)} articles to {output_path}")


def main(feed_urls: Optional[list[str]] = None) -> None:
    """
    Main function: fetch, filter, deduplicate, and save articles.
    """
    urls = feed_urls or DEFAULT_FEEDS

    if not urls:
        print("No feed URLs provided", file=sys.stderr)
        sys.exit(1)

    # Fetch articles with freshness filtering
    articles = fetch_articles(urls)

    # Deduplicate by link
    articles = deduplicate_articles(articles)

    # Save to JSON
    save_articles(articles)


if __name__ == "__main__":
    main(sys.argv[1:] if len(sys.argv) > 1 else None)
