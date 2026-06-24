import json
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROJECT_ROOT / "data" / "articles.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "threat_brief.md"


def load_articles(input_path: Path = DEFAULT_INPUT) -> list[dict]:
    """
    Load articles from JSON file.

    Args:
        input_path: Path to articles.json

    Returns:
        List of article dictionaries, empty list if file not found
    """
    if not input_path.exists():
        print(f"Warning: Article file not found at {input_path}", file=sys.stderr)
        return []

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
        return articles if isinstance(articles, list) else []
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON from {input_path}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error: Failed to read {input_path}: {e}", file=sys.stderr)
        return []


def group_articles_by_source(articles: list[dict]) -> dict[str, list[dict]]:
    """
    Group articles by their source feed.

    Args:
        articles: List of article dictionaries

    Returns:
        Dictionary with source names as keys and article lists as values
    """
    grouped = defaultdict(list)

    for article in articles:
        source = article.get("source", "Unknown Source")
        grouped[source].append(article)

    return dict(grouped)


def format_article(article: dict) -> str:
    """
    Format a single article as Markdown.

    Handles missing fields gracefully with fallback text.

    Args:
        article: Dictionary containing article data

    Returns:
        Formatted Markdown string for the article
    """
    title = article.get("title", "Untitled")
    link = article.get("link", "")
    source = article.get("source", "Unknown Source")
    published = article.get("published", "Date unknown")
    summary = article.get("summary", "No summary available")

    # Create linked title if link available, plain title otherwise
    if link:
        title_line = f"**[{title}]({link})**"
    else:
        title_line = f"**{title}**"

    # Build article markdown with consistent formatting
    markdown = f"""
{title_line}

- **Source:** {source}
- **Published:** {published}
- **Summary:** {summary}
"""
    return markdown.strip()


def calculate_source_counts(grouped: dict[str, list[dict]]) -> list[tuple[str, int]]:
    """
    Calculate article counts per source and sort by count descending.

    Args:
        grouped: Dictionary with source names as keys and article lists as values

    Returns:
        List of (source_name, count) tuples sorted by count descending
    """
    source_counts = [(source, len(articles)) for source, articles in grouped.items()]
    return sorted(source_counts, key=lambda x: x[1], reverse=True)


def format_source_summary(source_counts: list[tuple[str, int]]) -> str:
    """
    Format source summary section for the report.

    Args:
        source_counts: List of (source_name, count) tuples

    Returns:
        Formatted Markdown string for the sources section
    """
    lines = ["## Sources", ""]
    for source, count in source_counts:
        lines.append(f"- **{source}:** {count} article{'s' if count != 1 else ''}")
    return "\n".join(lines)


def format_top_articles(articles: list[dict], limit: int = 5) -> str:
    """
    Format top recent articles section for the report.

    Assumes articles are already sorted newest-first.

    Args:
        articles: List of article dictionaries
        limit: Maximum number of articles to include (default: 5)

    Returns:
        Formatted Markdown string for the top articles section
    """
    top_articles = articles[:limit]
    lines = ["## Top Recent Articles", ""]

    for i, article in enumerate(top_articles, start=1):
        title = article.get("title", "Untitled")
        link = article.get("link", "")
        source = article.get("source", "Unknown Source")
        published = article.get("published", "Date unknown")

        # Create linked title or plain bold title
        if link:
            title_text = f"**[{title}]({link})**"
        else:
            title_text = f"**{title}**"

        # Format published date to be more readable (extract just the date part)
        date_part = published.split("T")[0] if "T" in published else published

        lines.append(f"{i}. {title_text} — {source}, {date_part}")

    return "\n".join(lines)




def generate_report(
    articles: list[dict],
    output_path: Path = DEFAULT_OUTPUT,
) -> None:
    """
    Generate Markdown threat brief from articles.

    Includes title, generation date, article count, source count, source summary,
    top recent articles, and articles grouped by source.

    Args:
        articles: List of article dictionaries
        output_path: Path where to save the report
    """
    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate report header with metadata
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines = [
        "# Morning Threat Brief",
        "",
        f"**Generated:** {now}",
        f"**Total Articles:** {len(articles)}",
    ]

    # Handle empty article list
    if not articles:
        report_lines.append("")
        report_lines.append("No articles available for this report.")
    else:
        # Group articles by source for organized report
        grouped = group_articles_by_source(articles)

        # Add total sources to header
        report_lines.append(f"**Total Sources:** {len(grouped)}")
        report_lines.append("")

        # Add source summary section
        source_counts = calculate_source_counts(grouped)
        report_lines.append(format_source_summary(source_counts))
        report_lines.append("")

        # Add top recent articles section
        report_lines.append(format_top_articles(articles))
        report_lines.append("")

        # Add section for each source (sorted alphabetically)
        for source in sorted(grouped.keys()):
            source_articles = grouped[source]
            report_lines.append(f"## {source}")
            report_lines.append(f"*{len(source_articles)} article(s)*")
            report_lines.append("")

            # Add each article in this source
            for article in source_articles:
                report_lines.append(format_article(article))
                report_lines.append("")

    # Write report to file
    report_text = "\n".join(report_lines)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"Report generated: {output_path}")
    except Exception as e:
        print(f"Error: Failed to write report to {output_path}: {e}", file=sys.stderr)
        sys.exit(1)




def main() -> None:
    """
    Main function: load articles and generate threat brief report.
    """
    articles = load_articles()
    generate_report(articles)


if __name__ == "__main__":
    main()
