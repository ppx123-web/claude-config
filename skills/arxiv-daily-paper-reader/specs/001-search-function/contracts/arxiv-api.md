# arXiv API Contracts

**Date**: 2025-12-19
**Purpose**: Define API contracts for arXiv search functionality

## Base API Contract

### Endpoint
```
GET http://export.arxiv.org/api/query
```

### Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| search_query | string | No | Search query with field prefixes | "ti:attention AND abs:transformer" |
| id_list | string | No | Comma-separated arXiv IDs | "cs.AI/2312.12345,cs.LG/2312.54321" |
| start | integer | No | Starting index for pagination | 0 |
| max_results | integer | No | Number of results (max 2000) | 100 |
| sortBy | string | No | Sort field | "relevance", "submittedDate", "lastUpdatedDate" |
| sortOrder | string | No | Sort direction | "ascending", "descending" |

### Response Format
```xml
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>ArXiv Query: search_query=...</title>
  <id>http://arxiv.org/api/...</id>
  <updated>2024-12-19T00:00:00Z</updated>
  <opensearch:totalResults>1234</opensearch:totalResults>
  <opensearch:startIndex>0</opensearch:startIndex>
  <opensearch:itemsPerPage>100</opensearch:itemsPerPage>
  <entry>
    <!-- Paper details -->
  </entry>
</feed>
```

## Search Query Contract

### Field Prefixes
| Prefix | Target | Description | Example |
|--------|--------|-------------|---------|
| ti: | Title | Search in paper titles only | "ti:machine learning" |
| abs: | Abstract | Search in paper abstracts only | "abs:\"deep neural networks\"" |
| all: | All Fields | Search in all metadata fields (default) | "all:quantum computing" |
| au: | Author | Search by author name | "au:John Doe" |
| cat: | Category | Filter by arXiv category | "cat:cs.AI" |
| id: | Paper ID | Search by arXiv ID | "id:cs.AI/2312.12345" |

### Boolean Operators
| Operator | Description | Example |
|----------|-------------|---------|
| AND | Intersection | "ti:attention AND abs:transformer" |
| OR | Union | "cat:cs.AI OR cat:cs.LG" |
| NOT | Exclusion | "cat:cs.AI ANDNOT cat:cs.LG" |
| ( ) | Grouping | "(cat:cs.AI OR cat:cs.LG) AND ti:network" |

### Phrase Matching
| Syntax | Description | Example |
|--------|-------------|---------|
| "text" | Exact phrase match | 'abs:"machine learning"' |
| word* | Prefix wildcard | "ti:neural*" |

## Date Filter Contract

### Submitted Date Syntax
```
submittedDate:[YYYYMMDDHHMM TO YYYYMMDDHHMM]
```

### Examples
| Description | Query |
|-------------|-------|
| Papers from specific day | "submittedDate:[202412010000 TO 202412012359]" |
| Papers from date range | "submittedDate:[202412010000 TO 202412312359]" |
| Papers since specific date | "submittedDate:[202412010000 TO 299912312359]" |

## Rate Limiting Contract

### Requirements
- **Minimum delay**: 3 seconds between consecutive requests
- **Single thread**: No parallel API requests
- **Retry logic**: Exponential backoff on rate limit errors (HTTP 429)

### Error Handling
| HTTP Code | Action | Retry Strategy |
|-----------|--------|----------------|
| 200 | Success | N/A |
| 400 | Bad Request | Don't retry (user error) |
| 429 | Too Many Requests | Exponential backoff: 3s, 9s, 27s |
| 500 | Server Error | Retry with 3s delay |
| 503 | Service Unavailable | Retry with 3s delay |

## Search Result Contract

### Paper Entry Structure
```xml
<entry>
  <id>http://arxiv.org/abs/cs.AI/2312.12345</id>
  <updated>2024-12-18T15:30:00Z</updated>
  <published>2024-12-18T00:00:00Z</published>
  <title>Paper Title</title>
  <summary>Abstract text...</summary>
  <author><name>Author Name</name></author>
  <category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
  <link rel="alternate" type="text/html" href="http://arxiv.org/abs/cs.AI/2312.12345"/>
  <link rel="related" type="application/pdf" href="http://arxiv.org/pdf/cs.AI/2312.12345.pdf"/>
</entry>
```

### Required Fields
| XML Path | Description | Type |
|----------|-------------|------|
| entry/id | arXiv URL/ID | string |
| entry/title | Paper title | string |
| entry/summary | Paper abstract | string |
| entry/published | Publication date | datetime (UTC) |
| entry/updated | Last updated date | datetime (UTC) |
| entry/author/name | Author name | string |
| entry/category/@term | Category code | string |
| entry/link[@rel="alternate"]/@href | Paper URL | string |
| entry/link[@rel="related"]/@href | PDF URL | string |

## Integration Contract

### Existing CLI Extension
```bash
# New search command
arxiv_cli.py search --keywords "machine learning" --categories cs.AI cs.LG --days 30

# Search with date range
arxiv_cli.py search --query "attention mechanisms" --start-date 2024-12-01 --end-date 2024-12-31

# Phrase search
arxiv_cli.py search --query '"deep neural networks"' --categories cs.CV
```

### Output Contract
- **Format**: Markdown (same as existing reports)
- **Structure**: Papers grouped by category
- **Metadata**: Total count, search filters used, execution time
- **Links**: Paper and PDF URLs for each result

### Error Contract
| Error Type | User Message | Action |
|------------|--------------|--------|
| Invalid category | "Invalid arXiv category: XXX" | Suggest valid categories |
| Network timeout | "arXiv API unavailable, please try again" | Retry with backoff |
| No results | "No papers found matching your criteria" | Suggest broader search |
| Rate limit exceeded | "Too many requests, please wait" | Implement rate limiting