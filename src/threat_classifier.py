"""
Threat categorization logic for Morning Threat Brief.

This module assigns deterministic threat categories to articles based on
keyword matches in the title and summary.
"""

CATEGORY_KEYWORDS = {
    "Vulnerability": [
        "cve",
        "vulnerability",
        "zero-day",
        "0-day",
        "patch",
        "patched",
        "exploit",
        "exploited",
        "rce",
        "remote code execution",
    ],
    "Ransomware": [
        "ransomware",
        "extortion",
        "encryptor",
        "decryptor",
    ],
    "Malware": [
        "malware",
        "trojan",
        "backdoor",
        "loader",
        "botnet",
        "spyware",
        "infostealer",
        "stealer",
    ],
    "Phishing": [
        "phishing",
        "credential theft",
        "credential harvesting",
        "email scam",
        "spoofing",
    ],
    "Data Breach": [
        "data breach",
        "breach",
        "leak",
        "leaked",
        "stolen data",
        "exposed data",
    ],
    "Threat Actor": [
        "apt",
        "threat actor",
        "state-sponsored",
        "nation-state",
        "hacker group",
    ],
}


def classify_article(article: dict) -> dict:
    """
    Assign a threat category to a single article.

    Args:
        article: Article dictionary

    Returns:
        Article dictionary with category field added
    """
    text = " ".join([
        article.get("title", ""),
        article.get("summary", ""),
    ]).lower()

    matched_categories = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                matched_categories.append(category)
                break

    article["categories"] = matched_categories if matched_categories else ["Uncategorized"]

    return article


def classify_articles(articles: list[dict]) -> list[dict]:
    """
    Assign threat categories to a list of articles.
    """
    return [classify_article(article) for article in articles]
