# arXiv Daily Paper Reader - Implementation Details

## Technical Stack

### Core Technologies

- **Python**: 3.12+
- **feedparser**: >=6.0.10 (RSS/Atom feed parsing)
- **urllib**: Built-in HTTP request handling
- **xml.etree.ElementTree**: Built-in XML parsing
- **argparse**: Built-in command-line argument parsing
- **json**: Built-in JSON data handling
- **dataclasses**: Built-in data structure definitions
- **typing**: Built-in type annotations
- **uv**: Package management and virtual environment

## Architecture

### Core Modules

```
arxiv-daily-paper-reader/
├── skill.py              # Main CLI entry point
├── arxiv_daily.py        # Daily fetch functionality
├── search_module.py      # Search functionality
├── pyproject.toml        # Project dependencies
└── setup.sh              # Environment setup script
```

### Module Responsibilities

#### skill.py
- Command-line interface
- Argument parsing
- Command routing (fetch/search)
- Output formatting

#### arxiv_daily.py
- Fetch yesterday's papers
- Parse RSS feeds
- Extract paper metadata
- Generate daily reports

#### search_module.py
- Search arXiv database
- Apply filters (category, date)
- Handle pagination
- Sort and rank results

## Core Algorithms

### Daily Fetch Algorithm

1. **Time Calculation**
   ```python
   yesterday = datetime.now() - timedelta(days=1)
   start_date = yesterday.replace(hour=0, minute=0, second=0)
   end_date = yesterday.replace(hour=23, minute=59, second=59)
   ```

2. **RSS Feed Query**
   ```python
   feed_url = f"http://export.arxiv.org/api/query?"
   f"search_query=cat:{category}+AND+submittedDate:[{start_date}TO{end_date}]"
   ```

3. **Metadata Extraction**
   - Paper ID
   - Title
   - Authors
   - Summary (first 2 sentences)
   - Publication date
   - Categories
   - Links (abstract, PDF)

4. **Data Organization**
   - Group by category
   - Sort by publication date
   - Limit per category (max_papers)

5. **Report Generation**
   - Markdown format with structured sections
   - JSON format for programmatic access
   - Include statistics and metadata

### Search Algorithm

1. **Query Construction**
   ```python
   query = f"cat:{category}+AND+submittedDate:[{start_date}TO{end_date}]"
   ```

2. **API Request**
   ```python
   base_url = "http://export.arxiv.org/api/query?"
   params = {
       "search_query": query,
       "start": 0,
       "max_results": max_results
   }
   ```

3. **Pagination Handling**
   - arXiv returns results in batches
   - Handle multiple pages if needed
   - Respect API rate limits

4. **Result Processing**
   - Parse XML response
   - Extract paper metadata
   - Apply filters (date, category)
   - Sort by relevance or date

5. **Output Formatting**
   - Markdown report
   - JSON data
   - Console preview

## Data Structures

### Paper Data (dataclass)

```python
@dataclass
class ArxivPaper:
    id: str
    title: str
    authors: List[str]
    summary: str
    published: str
    categories: List[str]
    link: str
    pdf_link: str
```

### Report Metadata

```python
@dataclass
class ReportMetadata:
    generated_date: str
    categories: List[str]
    total_papers: int
    papers_by_category: Dict[str, int]
```

## Performance Optimization

### Request Management

- **Rate Limiting**: Respect arXiv API limits (1 request per 3 seconds)
- **Automatic Retry**: Retry failed requests with exponential backoff
- **Batch Processing**: Process multiple categories in parallel

### Caching Strategy

- Cache RSS feed responses
- Cache parsed paper data
- Invalidate cache after 24 hours

### Memory Management

- Stream large responses
- Process papers incrementally
- Limit memory footprint for large result sets

## Error Handling

### Network Errors

```python
try:
    response = urllib.request.urlopen(url, timeout=30)
except urllib.error.URLError as e:
    logger.error(f"Network error: {e}")
    # Retry with backoff
    time.sleep(5)
    # Retry logic...
```

### Parse Errors

```python
try:
    feed = feedparser.parse(feed_url)
except Exception as e:
    logger.error(f"Parse error: {e}")
    # Skip problematic entry, continue processing
```

### API Rate Limits

- Detect 429 (Too Many Requests) responses
- Automatic delay before retry
- Exponential backoff strategy

## Date Handling

### Date Formats

- **arXiv Format**: `2025-01-19T10:30:00Z`
- **Report Format**: `2025-01-19`
- **Range Format**: `[20250119000000 TO 20250119235959]`

### Timezone Handling

- All dates in UTC
- Convert to local time for display
- Handle daylight saving time

## Output Generation

### Markdown Report

```python
def generate_markdown_report(papers: List[ArxivPaper], metadata: ReportMetadata) -> str:
    """Generate formatted Markdown report"""
    report = []
    report.append("# arXiv Daily Paper Report")
    report.append(f"Generated on: {metadata.generated_date}")
    report.append(f"Categories: {', '.join(metadata.categories)}")
    report.append(f"Total Papers: {metadata.total_papers}")

    for category, category_papers in group_by_category(papers):
        report.append(f"\n## {category}")
        for paper in category_papers:
            report.append(format_paper_entry(paper))

    return "\n".join(report)
```

### JSON Output

```python
def generate_json_output(papers: List[ArxivPaper], metadata: ReportMetadata) -> str:
    """Generate JSON data"""
    data = {
        "metadata": asdict(metadata),
        "papers": [asdict(paper) for paper in papers]
    }
    return json.dumps(data, indent=2)
```

## Configuration

### Environment Variables

```bash
# Optional: Custom arXiv API endpoint
ARXIV_API_URL="http://export.arxiv.org/api/query"

# Optional: Request timeout in seconds
ARXIV_TIMEOUT=30

# Optional: Maximum retry attempts
ARXIV_MAX_RETRIES=3
```

### Default Settings

```python
DEFAULT_CATEGORIES = ["cs.OS", "cs.PL", "cs.SE", "cs.AI"]
DEFAULT_MAX_PAPERS = 50
DEFAULT_SUMMARY_LENGTH = 2  # sentences
DEFAULT_DAYS = 30
```

## Testing

### Unit Tests

```bash
# Run tests (if available)
python -m pytest tests/
```

### Manual Testing

```bash
# Test fetch
python skill.py fetch --cats cs.AI --max-papers 5

# Test search
python skill.py search --categories cs.SE --days 7 --max-results 10

# Test output formats
python skill.py fetch --output-format json
python skill.py fetch --output-format both
```

## Dependencies Management

### Using uv (Recommended)

```bash
# Install dependencies
uv pip install feedparser>=6.0.10

# Update dependencies
uv pip install --upgrade feedparser
```

### Using pip

```bash
# Install requirements
pip install -r requirements.txt

# Or install directly
pip install feedparser>=6.0.10
```

## Logging

### Log Levels

- INFO: Normal operations
- WARNING: API rate limits, retries
- ERROR: Network failures, parse errors

### Log Format

```
2025-01-19 10:30:00 INFO Fetching papers for cs.AI
2025-01-19 10:30:05 WARNING Rate limit reached, retrying...
2025-01-19 10:30:10 INFO Fetched 15 papers for cs.AI
```

## Future Enhancements

Consider these potential improvements:

- **Semantic Search**: Use embeddings for paper similarity
- **Author Tracking**: Follow specific authors' publications
- **Citation Analysis**: Track paper citations and impact
- **Trend Analysis**: Identify research trends over time
- **Personalization**: Learn user preferences and recommend papers

Note: Only implement if there's a real user need. Avoid premature optimization.
