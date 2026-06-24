import feedparser
import json
import sys
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "articles.json"
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "feeds.txt"

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

        # Normalize all datetimes to UTC for consistent sorting
        if dt.tzinfo is None:
            # If timezone-naive, assume UTC
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            # If timezone-aware, convert to UTC
            dt = dt.astimezone(timezone.utc)

        return dt
    except (TypeError, ValueError):
        return None


def load_feed_urls(config_path: Path = DEFAULT_CONFIG) -> list[str]:
    """
    Load feed URLs from configuration file with fallback to defaults.

    Reads config_path, ignoring blank lines and lines starting with #.
    Returns list of valid URLs; if config doesn't exist or has no URLs,
    falls back to DEFAULT_FEEDS.

    Args:
        config_path: Path to feeds.txt configuration file

    Returns:
        List of feed URL strings
    """
    if config_path.exists():
        try:
            with config_path.open("r", encoding="utf-8") as f:
                urls = []
                for line in f:
                    line = line.strip()
                    # Skip blank lines and comments
                    if line and not line.startswith("#"):
                        urls.append(line)
                if urls:
                    return urls
        except Exception as e:
            print(f"Warning: Could not read {config_path}: {e}", file=sys.stderr)

    return DEFAULT_FEEDS



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


def sort_articles(articles: list[dict]) -> list[dict]:
    """
    Sort articles newest-first by published date.

    Uses ISO 8601 datetime strings for sorting.

    Args:
        articles: List of article dictionaries

    Returns:
        Sorted list with newest articles first
    """
    return sorted(
        articles,
        key=lambda a: a.get("published", ""),
        reverse=True,
    )


def print_feed_stats(stats: dict) -> None:
    """
    Print per-feed statistics summary to stdout.

    Args:
        stats: Dict of feed_url -> stats dict
    """
    print("\n=== Feed Statistics ===")
    total_fetched = 0
    total_kept = 0

    for feed_url, feed_stat in stats.items():
        total_fetched += feed_stat["fetched"]
        total_kept += feed_stat["kept"]
        source = feed_stat.get("source", "Unknown")
        print(
            f"{source}: {feed_stat['kept']}/{feed_stat['fetched']} "
            f"(skipped: {feed_stat['skipped_old']} old, "
            f"{feed_stat['skipped_no_date']} no date)"
        )

    print(f"\nTotal: {total_kept} articles kept from {total_fetched} fetched")



def fetch_articles(feed_urls: list[str]) -> tuple[list[dict], dict]:
    """
    Fetch and parse articles from RSS feeds with filtering.

    - Parses published dates with timezone handling
    - Filters articles older than 30 days
    - Discards articles with unparseable dates
    - Tracks per-feed statistics

    Returns:
        (articles, stats) tuple where stats is a dict of feed URL -> stats dict
    """
    articles = []
    stats = {}

    for feed_url in feed_urls:
        feed_stats = {
            "feed_url": feed_url,
            "source": None,
            "fetched": 0,
            "kept": 0,
            "skipped_old": 0,
            "skipped_no_date": 0,
        }

        try:
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                print(f"Warning: Feed {feed_url} has parsing issues", file=sys.stderr)

            source_name = feed.feed.get("title", feed_url)
            feed_stats["source"] = source_name

            for entry in feed.entries:
                feed_stats["fetched"] += 1

                # Get date string from either 'published' or 'updated' field
                date_string = entry.get("published") or entry.get("updated", "")

                # Parse the date string to datetime object
                published_date = parse_published_date(date_string)

                # Skip articles with unparseable dates
                if published_date is None:
                    feed_stats["skipped_no_date"] += 1
                    continue

                # Skip articles older than 30 days
                if not is_recent_article(published_date):
                    feed_stats["skipped_old"] += 1
                    continue

                feed_stats["kept"] += 1
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": published_date.isoformat(),
                    "source": source_name,
                    "summary": entry.get("summary") or entry.get("description", ""),
                    "feed_url": feed_url,
                })

        except Exception as e:
            print(f"Error processing feed {feed_url}: {e}", file=sys.stderr)

        stats[feed_url] = feed_stats

    return articles, stats


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
    Main function: fetch, filter, deduplicate, sort, and save articles.
    """
    # Use provided URLs, or load from config, or use defaults
    if feed_urls:
        urls = feed_urls
    else:
        urls = load_feed_urls()

    if not urls:
        print("No feed URLs provided", file=sys.stderr)
        sys.exit(1)

    # Fetch articles with freshness filtering and per-feed statistics
    articles, stats = fetch_articles(urls)

    # Deduplicate by link
    articles = deduplicate_articles(articles)

    # Sort newest-first
    articles = sort_articles(articles)

    # Save to JSON
    save_articles(articles)

    # Print feed statistics
    print_feed_stats(stats)



if __name__ == "__main__":
    main(sys.argv[1:] if len(sys.argv) > 1 else None)
