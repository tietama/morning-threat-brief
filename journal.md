# Project Journal

## 2026-06-23

### Environment Setup

Created Ubuntu development VR

Configuration:
- 4 vCPUs
- 6 GM RAM
- 60 GB dynamically allocated disk
- 1920x1080 resolution

Installed:
- Git
- Python tooling
- VS Code

Created:
- README.md
- journal.md

Initial GIT repository.

### Notes

Chose Ubuntu instead of Kali because the project is primarily a development and automation environment rather than a penetration testing platform.

### Next Steps

- Define threat intelligence sources
- Build first RSS feed collector

## 2026-06-23

Updated RSS collector:
- Removed ENISA feed due to parsing issues
- Added 30-day freshness filtering
- Added link-based deduplication
- Fixed stable output path to project_root/data/articles.json
- Collector now returns 31 recent articles

## 2026-06-24

Updated RSS collector to v0.2.3:
- Added newest-first sorting using parsed publication dates
- Normalized published dates to ISO 8601
- Added per-feed collection statistics
- Moded default RSS feeds to config/feeds.txt with fallback behavior

## 2026-06-24

Updated report generator to v0.3.2

Changes:
- Added total article count to report metadata
- Added total source count to report metadata
- Added source summary section with per-source article counts
- Added Top Recent Articles section showing the five newest articles
- Improved report readability and executive-level overview

Result:
- Repots now provide an immediate summary of collected intelligence before detailed source-by-source review

## 2026-06-24

Updated report generator to v0.3.3

Changes:

- Added report metadata including total article count and total source count
- Added source summary section with per-source article counts
- Added Top Recent Articles section highlighting the five newest articles
- Added summary cleanup and formatting
- Removed HTML tags from RSS summaries
- Decoded HTML entities
- Normalized whitespace
- Added summary truncation for improved readability

Result:

- Generated reports now provide both an executive overview and detailed source-by-source coverage
- Report readability improved significantly through summary cleanup and formatting
- Markdown output is now suitable for portfolio demonstration and future pipeline automation

## 2026-06-24

Updated project to v0.4

Changes:

- Added pipeline_runner.py
- Added one-command execution of the complete workflow
- Pipeline now:
	- Loads RSS feeds from configuration
	- Collects and filters recent articles
	- Deduplicates articles
	- Sorts articles newest-first
	- Saves articles to data/articles.json
	- Generates outputs/threat_brief.md
- Added execution timing
- Added pipeline progress messages
- Added centralized pipeline error handling

Result:

- Morning Threat Brief can now be executed with a single command
- Collection and report generation are now automated
- Project now functions as a complete end-to-end threat intelligence pipeline
- Foundation prepared for future LLM summarization features

## 2026-06-25

Updated project to v0.5

Changes:

- Added deterministic threat categorization
- Implemented keyword-based article classification
- Added support for multiple threat categories per article
- Integrated categorization into the pipeline
- Categories are now store in data/articles.json
- Added threat category display for individual articles in the report
- Added Threat Categories summary section with per-category article counts

Result:

- Morning Threat Brief now performs deterministic threat classification in addition to collecting news
- Reports provide an executive overview of the current threat landscape by category
- Foundation prepared for future relevance scoring and CISA KEV integration

## 2026-06-25

Updated project to v0.6

Changes:

- Added deterministic relevance scoring
- Created explainable scoring using threat categories and keyword matches
- Added human-readable relevance reasons for every scored article
- Integrated relevance scoring into the pipeline
- Store relevance scores and reasons in data/articles.json
- Added relevance score and scoring reasons to individual article entries in the report
- Added Highest Relevance Articles summary section highlighting the five highest-scoring articles

Result:

- Morning Threat Brief now prioritizes collected intelligence using deterministic and explainable relevance scoring
- Reports now highlight the most important articles alongside the latest articles
- Foundation prepared for future CISA KEV enrichment and AI-assisted summarization
