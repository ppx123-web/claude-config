# Quick Start: Search Function

**Date**: 2025-12-19
**Purpose**: Quick start guide for using the new search functionality

## Overview

The search functionality extends the arXiv Daily Paper Reader with powerful search capabilities while maintaining the same CLI interface and output format. Users can search by keywords, filter by categories, and specify date ranges to find relevant research papers.

## Prerequisites

- Python 3.12+ installed
- uv package manager (per project constitution)
- Dependencies installed: `uv sync`
- Existing arXiv Daily Paper Reader setup

## Installation

No additional installation required. Search functionality is integrated into existing CLI.

## Basic Usage

### Simple Keyword Search
```bash
# Search for papers about machine learning
arxiv_cli.py search --keywords "machine learning"

# Search for exact phrase
arxiv_cli.py search --query '"deep neural networks"'

# Search in titles only
arxiv_cli.py search --query "ti:attention mechanisms"
```

### Category Filtering
```bash
# Search in specific category
arxiv_cli.py search --keywords "transformers" --categories cs.AI

# Search in multiple categories
arxiv_cli.py search --keywords "object detection" --categories cs.CV cs.AI cs.LG

# Default categories (from existing config)
arxiv_cli.py search --keywords "operating systems"
```

### Date Range Filtering
```bash
# Search papers from last 30 days
arxiv_cli.py search --keywords "quantum" --days 30

# Search specific date range
arxiv_cli.py search --query "neural networks" --start-date 2024-11-01 --end-date 2024-11-30

# Search recent papers in AI
arxiv_cli.py search --keywords "attention" --categories cs.AI --days 7
```

### Advanced Search Examples
```bash
# Complex query with all filters
arxiv_cli.py search \
  --query "cat:cs.CV AND ti:object detection" \
  --days 60 \
  --max-results 50

# Search for author + topic
arxiv_cli.py search --query "au:lecun AND ti:convolutional"

# Multiple keywords with boolean logic
arxiv_cli.py search --query "machine AND learning ANDNOT supervised"
```

## Command Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--query` | `-q` | Full search query with arXiv syntax | `--query "ti:attention AND abs:transformer"` |
| `--keywords` | `-k` | Simple keyword search | `--keywords "machine learning"` |
| `--categories` | `-c` | ArXiv categories to filter | `--categories cs.AI cs.LG` |
| `--days` | `-d` | Papers from last N days | `--days 30` |
| `--start-date` | `-s` | Start date for date range | `--start-date 2024-11-01` |
| `--end-date` | `-e` | End date for date range | `--end-date 2024-11-30` |
| `--max-results` | `-m` | Maximum results to return | `--max-results 100` |
| `--sort-by` | None | Sort order (relevance, submittedDate, lastUpdatedDate) | `--sort-by relevance` |
| `--output` | `-o` | Output file path | `--output search_results.md` |
| `--preview-only` | None | Preview without saving | `--preview-only` |

## Search Syntax

### Field-Specific Search
- `ti:text` - Search in titles
- `abs:text` - Search in abstracts
- `all:text` - Search in all fields (default)
- `au:name` - Search by author
- `cat:code` - Filter by category

### Boolean Operators
- `AND` - Intersection (default)
- `OR` - Union
- `NOT` / `ANDNOT` - Exclusion
- `()` - Grouping

### Examples
```bash
# Title and abstract search
arxiv_cli.py search --query "ti:attention AND abs:transformer"

# Multiple categories
arxiv_cli.py search --query "(cat:cs.AI OR cat:cs.LG) AND neural"

# Exclude categories
arxiv_cli.py search --query "cat:cs.AI ANDNOT cat:cs.LG"

# Exact phrase matching
arxiv_cli.py search --query 'abs:"deep learning"'
```

## Available Categories

### Computer Science (Primary)
- `cs.AI` - Artificial Intelligence
- `cs.LG` - Machine Learning
- `cs.CV` - Computer Vision
- `cs.CL` - Computation and Language
- `cs.OS` - Operating Systems
- `cs.PL` - Programming Languages
- `cs.SE` - Software Engineering
- `cs.IR` - Information Retrieval
- `cs.CR` - Cryptography and Security
- `cs.DB` - Databases

### Other Categories
- `math.*` - Mathematics (e.g., math.AG, math.ST)
- `physics.*` - Physics (e.g., physics.comp-ph, physics.quant-ph)
- `q-bio.*` - Quantitative Biology
- `q-fin.*` - Quantitative Finance
- `stat.*` - Statistics

## Output Format

Search results use the same format as existing daily reports:

```markdown
# arXiv Search Results
Query: "attention mechanisms" in cs.AI
Date Range: 2024-11-01 to 2024-11-30
Total Results: 47 papers

## Summary by Category

### cs.AI (47 papers)

**1. Paper Title**
*Authors:* John Doe, Jane Smith
*Published:* 2024-11-15
*Categories:* cs.AI, cs.LG
**Summary:** Paper abstract text here...
[Read Paper](http://arxiv.org/abs/...) | [PDF](http://arxiv.org/pdf/...)
```

## Performance Tips

### Speed Up Searches
- Use specific categories to reduce API calls
- Limit date ranges for faster results
- Use `--max-results` to avoid large downloads
- Search in titles only with `ti:` prefix

### Rate Limiting
- Built-in 3-second delays between API calls
- Large searches may take several minutes
- Use `--preview-only` to test queries before full execution

## Troubleshooting

### Common Issues

**No Results Found**
- Try broader search terms
- Check category codes (cs.AI vs cs.AI.LG)
- Verify date ranges are reasonable

**Rate Limit Errors**
- Wait a few minutes between searches
- Reduce number of categories in search
- Use more specific queries to reduce result size

**Invalid Categories**
- Use official arXiv category codes
- Check the category taxonomy documentation
- Use `cs.AI` format, not "Artificial Intelligence"

**Network Errors**
- Check internet connection
- Verify arXiv API is accessible
- Try again after a few minutes

### Getting Help

```bash
# Show help for search command
arxiv_cli.py search --help

# Test query without saving
arxiv_cli.py search --keywords "test" --preview-only --max-results 5
```

## Integration with Existing Workflow

### Daily Research Routine
```bash
# 1. Get yesterday's papers (existing functionality)
arxiv_cli.py

# 2. Search for specific topics of interest
arxiv_cli.py search --keywords "your research topic" --days 7

# 3. Search specific categories
arxiv_cli.py search --categories cs.AI cs.LG --days 30
```

### Research Project Workflow
```bash
# Initial literature search
arxiv_cli.py search --query "your research area" --days 90 --output initial_search.md

# Follow-up searches for specific aspects
arxiv_cli.py search --query "specific technique" --categories cs.CV --days 30

# Recent developments
arxiv_cli.py search --keywords "latest developments" --days 14
```

This search functionality seamlessly extends your existing arXiv Daily Paper Reader workflow while maintaining the same command-line interface and output format you're already familiar with.