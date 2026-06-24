# Morning Threat Brief

Morning Threat Brief is a Python-based threat intelligence collection and reporting pipeline.

The project collects cybersecurity news from multiple RSS feeds, filters and normalizes the data, removes duplicates, and generates a structured Markdown threat brief for analyst review.

## Project Goals

- Learn Python automation and software development
- Explore threat intelligence collection workflows
- Build a cybersecurity portfolio project
- Create a foundation for future AI-assisted analysis and SOC assistant functionality

## Current Status

**Current Version:** v0.4

### Implemented

- RSS feed collection
- Configurable feed sources
- 30-day freshness filtering
- RFC 2822 date parsing and UTC normalization
- Link-based deduplication
- Per-feed collection statistics
- Markdown threat brief generation
- Executive summary sections
- Automated pipeline execution

## Pipeline Workflow

1. Load RSS feeds from configuration
2. Collect articles from security news sources
3. Filter outdated content
4. Deduplicate articles
5. Sort articles newest-first
6. Save normalized article data
7. Generate Markdown threat brief

## Project Structure

```text
config/
    feeds.txt

data/
    articles.json

outputs/
    threat_brief.md

src/
    rss_collector.py
    report_generator.py
    pipeline_runner.py
```

## Usage

Run the complete pipeline:

```bash
python pipeline_runner.py
```

Outputs:

```text
data/articles.json
outputs/threat_brief.md
```

## Example Report Summary

```text
Generated: 2026-06-24
Total Articles: 31
Total Sources: 3

Sources:
- BleepingComputer
- SecurityWeek
- Kyberturvallisuuskeskus

Top Recent Articles:
1. ...
2. ...
3. ...
```

## Roadmap

### Completed

- v0.1 RSS Collection
- v0.2 Filtering & Deduplication
- v0.3 Markdown Report Generation
- v0.4 Pipeline Runner

### Planned

- v0.5 Threat Categorization
- v0.6 Relevance / Risk Scoring
- v0.7 CISA KEV Integration
- v0.8 LLM Summarization

### Future Ideas

- Historical article archive
- Trend analysis
- IOC extraction
- Threat actor tracking
- SOC assistant functionality

## Development Philosophy

- Build incrementally
- Prefer deterministic processing before AI
- Keep solutions simple and maintainable
- Focus on portfolio-friendly milestones
- Add AI only after the underlying pipeline is mature
