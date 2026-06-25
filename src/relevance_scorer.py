"""
Explainable relevance scoring for Morning Threat Brief.

This module assigns deterministic relevance scores to articles using their
threat categories and keyword matches in the title and summary.
"""

import re


CATEGORY_SCORES = {
    "Ransomware": 4,
    "Vulnerability": 3,
    "Malware": 3,
    "Data Breach": 3,
    "Phishing": 2,
    "Threat Actor": 2,
    "Uncategorized": 0,
}

KEYWORD_SCORES = {
    "actively exploited": (4, "Actively exploited mentioned"),
    "zero-day": (4, "Zero-day mentioned"),
    "0-day": (4, "0-day mentioned"),
    "rce": (3, "RCE mentioned"),
    "remote code execution": (3, "Remote code execution mentioned"),
    "cve-": (2, "CVE mentioned"),
    "exploit": (2, "Exploit mentioned"),
    "critical": (2, "Critical mentioned"),
    "emergency patch": (2, "Emergency patch mentioned"),
    "ransomware": (2, "Ransomware mentioned"),
}

MAX_RELEVANCE_SCORE = 10


def score_article(article: dict) -> dict:
    """
    Assign an explainable relevance score to a single article.

    Args:
        article: Article dictionary

    Returns:
        Article dictionary with relevance_score and relevance_reasons added
    """
    score = 0
    reasons = []

    categories = article.get("categories", ["Uncategorized"])
    for category in categories:
        category_score = CATEGORY_SCORES.get(category, 0)
        if category_score:
            score += category_score
            reasons.append(f"{category} category")

    text = " ".join([
        article.get("title", ""),
        article.get("summary", ""),
    ]).lower()

    for keyword, (keyword_score, reason) in KEYWORD_SCORES.items():
        if keyword == "rce":
            keyword_found = re.search(r"\brce\b", text) is not None
        else:
            keyword_found = keyword in text

        if keyword_found:
            score += keyword_score
            reasons.append(reason)

    article["relevance_score"] = min(score, MAX_RELEVANCE_SCORE)
    article["relevance_reasons"] = reasons

    return article


def score_articles(articles: list[dict]) -> list[dict]:
    """
    Assign relevance scores to a list of articles.
    """
    return [score_article(article) for article in articles]
