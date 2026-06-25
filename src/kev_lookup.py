"""
CISA KEV catalog integration for Morning Threat Brief.

This module fetches the live CISA Known Exploited Vulnerabilities catalog
and saves a local copy for debugging and audit purposes.
"""

import json
import sys
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_KEV_OUTPUT = PROJECT_ROOT / "data" / "kev.json"

CISA_KEV_URL = (
    "https://www.cisa.gov/sites/default/files/feeds/"
    "known_exploited_vulnerabilities.json"
)


def fetch_kev_catalog(url: str = CISA_KEV_URL) -> dict:
    """
    Fetch the live CISA KEV catalog as JSON.

    Args:
        url: CISA KEV JSON feed URL

    Returns:
        Parsed KEV catalog dictionary

    Raises:
        RuntimeError: If the catalog cannot be fetched or parsed
    """
    try:
        with urlopen(url, timeout=30) as response:
            return json.load(response)

    except HTTPError as e:
        raise RuntimeError(f"HTTP error fetching KEV catalog: {e.code}") from e

    except URLError as e:
        raise RuntimeError(f"Network error fetching KEV catalog: {e.reason}") from e

    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse KEV catalog JSON: {e}") from e


def validate_kev_catalog(catalog: dict) -> None:
    """
    Validate that the KEV catalog has the expected structure.

    Args:
        catalog: Parsed KEV catalog dictionary

    Raises:
        ValueError: If the catalog structure is invalid
    """
    if not isinstance(catalog, dict):
        raise ValueError("KEV catalog must be a dictionary")

    vulnerabilities = catalog.get("vulnerabilities")

    if not isinstance(vulnerabilities, list):
        raise ValueError("KEV catalog missing vulnerabilities list")


def save_kev_catalog(
    catalog: dict,
    output_path: Path = DEFAULT_KEV_OUTPUT,
) -> None:
    """
    Save the KEV catalog locally for debugging and audit purposes.

    Args:
        catalog: Parsed KEV catalog dictionary
        output_path: Path where the catalog should be saved
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"Saved KEV catalog to {output_path}")


def load_kev_catalog() -> dict:
    """
    Fetch, validate, and save the live CISA KEV catalog.

    Returns:
        Parsed KEV catalog dictionary
    """
    catalog = fetch_kev_catalog()
    validate_kev_catalog(catalog)
    save_kev_catalog(catalog)

    return catalog


CVE_PATTERN = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)


def extract_cves_from_text(text: str) -> list[str]:
    """
    Extract CVE identifiers from text.

    Args:
        text: Text to search

    Returns:
        Sorted list of unique CVE IDs in uppercase
    """
    if not text:
        return []

    matches = CVE_PATTERN.findall(text)
    unique_cves = {match.upper() for match in matches}

    return sorted(unique_cves)


def extract_article_cves(article: dict) -> dict:
    """
    Extract CVE identifiers from a single article.

    Args:
        article: Article dictionary

    Returns:
        Article dictionary with cves field added
    """
    text = " ".join([
        article.get("title", ""),
        article.get("summary", ""),
    ])

    article["cves"] = extract_cves_from_text(text)

    return article


def extract_articles_cves(articles: list[dict]) -> list[dict]:
    """
    Extract CVE identifiers from a list of articles.
    """
    return [extract_article_cves(article) for article in articles]

def build_kev_lookup(catalog: dict) -> dict:
    """
    Build a CVE-to-KEV-entry lookup dictionary.

    Args:
        catalog: Parsed KEV catalog dictionary

    Returns:
        Dictionary mapping CVE IDs to KEV entries
    """
    vulnerabilities = catalog.get("vulnerabilities", [])
    lookup = {}

    for vuln in vulnerabilities:
        cve_id = vuln.get("cveID", "").upper()
        if cve_id:
            lookup[cve_id] = vuln

    return lookup


def enrich_article_with_kev(article: dict, kev_lookup: dict) -> dict:
    """
    Add KEV match information to a single article.

    Args:
        article: Article dictionary with cves field
        kev_lookup: Dictionary mapping CVE IDs to KEV entries

    Returns:
        Article dictionary with kev and kev_matches fields added
    """
    cves = article.get("cves", [])
    matches = []

    for cve in cves:
        kev_entry = kev_lookup.get(cve)
        if kev_entry:
            matches.append(kev_entry)

    article["kev"] = bool(matches)
    article["kev_matches"] = matches

    return article


def enrich_articles_with_kev(articles: list[dict], kev_lookup: dict) -> list[dict]:
    """
    Add KEV match information to a list of articles.
    """
    return [enrich_article_with_kev(article, kev_lookup) for article in articles]


def main() -> None:
    """
    Fetch, save, and test the CISA KEV catalog integration.
    """
    try:
        catalog = load_kev_catalog()
        vulnerabilities = catalog.get("vulnerabilities", [])
        print(f"Loaded {len(vulnerabilities)} KEV entries")

        kev_lookup = build_kev_lookup(catalog)
        print(f"Built KEV lookup with {len(kev_lookup)} CVE entries")

        sample_article = {
            "title": "Example article mentioning CVE-2024-12345",
            "summary": "This article also mentions CVE-2023-9999.",
        }

        sample_article = extract_article_cves(sample_article)
        sample_article = enrich_article_with_kev(sample_article, kev_lookup)

        print(f"Sample CVEs: {sample_article['cves']}")
        print(f"Sample KEV match: {sample_article['kev']}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
