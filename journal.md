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
