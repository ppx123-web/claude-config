# arXiv Daily Paper Reader - CLI Usage Guide

## Complete Command Reference

### Main Command Structure

```bash
python skill.py [-h] {fetch,search} ...
```

## fetch Command

Get yesterday's papers from arXiv.

### Syntax

```bash
python skill.py fetch [-h] [--cats CATEGORIES [CATEGORIES ...]]
                      [--max-papers MAX_PAPERS]
                      [--output-format {markdown,json,both}]
```

### Parameters

| Parameter | Short | Type | Default | Description |
|-----------|-------|------|---------|-------------|
| `--cats` | `--categories` | list | cs.OS, cs.PL, cs.SE, cs.AI | arXiv categories to fetch |
| `--max-papers` | | int | 50 | Maximum papers per category |
| `--output-format` | | choice | markdown | Output format: markdown, json, both |
| `-h` | `--help` | | | Show help message |

### Examples

```bash
# Default: Fetch yesterday's papers from default categories
python skill.py fetch

# Fetch specific categories
python skill.py fetch --cats cs.AI cs.LG cs.CV

# Limit papers per category
python skill.py fetch --cats cs.AI --max-papers 20

# Output both markdown and JSON
python skill.py fetch --output-format both

# Multiple categories with custom limit
python skill.py fetch --cats cs.AI cs.LG cs.CV cs.CL --max-papers 15
```

## search Command

Search arXiv papers by category and date range.

### Syntax

```bash
python skill.py search [-h] --cats CATEGORIES [CATEGORIES ...]
                       [--days DAYS]
                       [--max-results MAX_RESULTS]
                       [--output-format {markdown,json,both,preview}]
```

### Parameters

| Parameter | Short | Type | Default | Description |
|-----------|-------|------|---------|-------------|
| `--cats` | `--categories` | list | **Required** | arXiv categories to search |
| `--days` | `-d` | int | 30 | Search last N days |
| `--max-results` | | int | 15 | Maximum results to return |
| `--output-format` | | choice | markdown | Output format |
| `-h` | `--help` | | | Show help message |

### Examples

```bash
# Search cs.SE papers from last 7 days
python skill.py search --categories cs.SE --days 7

# Search multiple categories, last 30 days
python skill.py search --cats cs.AI cs.LG --days 30

# Get JSON output
python skill.py search --cats cs.CV --days 14 --output-format json

# Preview in console (no file output)
python skill.py search --cats cs.AI --days 7 --output-format preview

# Maximum results from longer time range
python skill.py search --cats cs.SE --days 90 --max-results 50
```

## Getting Help

```bash
# Main command help
python skill.py -h
python skill.py --help

# fetch command help
python skill.py fetch -h
python skill.py fetch --help

# search command help
python skill.py search -h
python skill.py search --help
```

## Output Formats

### markdown
Generates a formatted Markdown report file.

**File:** `arxiv_daily_report_YYYY-MM-DD.md`

### json
Generates a JSON data file.

**File:** `arxiv_papers_YYYY-MM-DD.json`

### both
Generates both Markdown and JSON files.

### preview
Displays results in console only, no file output.

## Output File Locations

Files are created in the current working directory:

```
arxiv_daily_report_2025-01-19.md
arxiv_papers_2025-01-19.json
```

## Category Codes

Complete list of arXiv categories:

### Computer Science (cs.*
- cs.AI - Artificial Intelligence
- cs.CL - Computation and Language
- cs.CV - Computer Vision
- cs.DB - Databases
- cs.DC - Distributed, Parallel, and Cluster Computing
- cs.DL - Digital Libraries
- cs.DM - Discrete Mathematics
- cs.DS - Data Structures and Algorithms
- cs.ET - Emerging Technologies
- cs.FL - Formal Languages and Automata Theory
- cs.GL - General Literature
- cs.GR - Graphics
- cs.AR - Hardware Architecture
- cs.HC - Human-Computer Interaction
- cs.IR - Information Retrieval
- cs.LG - Machine Learning
- cs.LO - Logic in Computer Science
- cs.MA - Multiagent Systems
- cs.MM - Multimedia
- cs.NI - Networking and Internet Architecture
- cs.NE - Neural and Evolutionary Computing
- cs.OS - Operating Systems
- cs.OH - Other Computer Science
- cs.PF - Performance
- cs.PL - Programming Languages
- cs.RO - Robotics
- cs.SC - Symbolic Computation
- cs.SD - Sound
- cs.SE - Software Engineering
- cs.SI - Social and Information Networks

### Other Categories
- math.MG - Magnitude
- math.OC - Optimization and Control
- physics.comp-ph - Computational Physics
- stat.ML - Machine Learning (Statistics)

## Troubleshooting

### Common Issues

**Problem**: `ModuleNotFoundError: No module named 'feedparser'`
```
Solution: Install dependencies
pip install feedparser>=6.0.10
```

**Problem**: Network timeout or connection error
```
Solution: Check internet connection, retry after a few seconds
The system has automatic retry logic.
```

**Problem**: API rate limit exceeded
```
Solution: arXiv API has rate limits. Wait before retrying.
The system respects API limits automatically.
```

**Problem**: No papers found
```
Solution: Check if category code is correct
Verify date range is appropriate
Use --days 1 for yesterday only
```

**Problem**: File write permission error
```
Solution: Check write permissions in current directory
Or specify absolute path for output
```

## Advanced Usage

### Combining with Shell Commands

```bash
# Fetch and pipe to less
python skill.py fetch --cats cs.AI | less

# Count papers in JSON output
python skill.py fetch --output-format json && \
  jq '.papers | length' arxiv_papers_*.json

# Grep for specific topics in markdown
python skill.py fetch --cats cs.SE && \
  grep -i "testing" arxiv_daily_report_*.md
```

### Automation

```bash
# Add to crontab for daily fetching
# Runs every day at 8:00 AM
0 8 * * * cd /path/to/skill && python skill.py fetch
```

### Batch Processing

```bash
# Fetch multiple categories in parallel
for cat in cs.AI cs.LG cs.CV cs.SE; do
    python skill.py fetch --cats $cat --max-papers 20 &
done
wait
```
