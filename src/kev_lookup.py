"""
CISA KEV catalog integration for Morning Threat Brief.

This module fetches the live CISA Known Exploited Vulnerabilities catalog
and saves a local copy for debugging and audit purposes.
"""

import json
import sys
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


def main() -> None:
    """
    Fetch and save the CISA KEV catalog.
    """
    try:
        catalog = load_kev_catalog()
        vulnerabilities = catalog.get("vulnerabilities", [])
        print(f"Loaded {len(vulnerabilities)} KEV entries")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
