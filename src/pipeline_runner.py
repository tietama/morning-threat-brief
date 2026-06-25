import sys
import time

from rss_collector import (
    load_feed_urls, 
    fetch_articles, 
    deduplicate_articles, 
    sort_articles, 
    save_articles, 
    print_feed_stats
)
from report_generator import load_articles, generate_report

from kev_lookup import (
    load_kev_catalog,
    build_kev_lookup,
    extract_articles_cves,
    enrich_articles_with_kev,
)
from relevance_scorer import score_articles
from threat_classifier import classify_articles

def run_pipeline() -> None:
    """
    Execute the complete Morning Threat Brief pipeline:
    1. Collect and filter articles from RSS feeds
    2. Generate threat brief report
    """
    print("\n=== Morning Threat Brief ===\n")
    start_time = time.time()

    try:
        # Stage 1: Collect articles
        print("[1/2] Collecting articles...")
        feed_urls = load_feed_urls()
        articles, stats = fetch_articles(feed_urls)
        articles = deduplicate_articles(articles)
        articles = sort_articles(articles)
        articles = classify_articles(articles)
        articles = score_articles(articles)
        kev_catalog = load_kev_catalog()
        kev_lookup = build_kev_lookup(kev_catalog)
        articles = extract_articles_cves(articles)
        articles = enrich_articles_with_kev(articles, kev_lookup)
        save_articles(articles)
        print_feed_stats(stats)

        # Stage 2: Generate report
        print("\n[2/2] Generating report...")
        articles = load_articles()
        generate_report(articles)

        elapsed = time.time() - start_time
        print(f"\nPipeline completed successfully in {elapsed:.1f} seconds.\n")

    except Exception as e:
        print(f"\nError: Pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
