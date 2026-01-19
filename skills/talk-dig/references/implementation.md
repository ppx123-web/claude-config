# Talk Dig Technical Implementation

## MCP Tools Used

### 1. Image Analysis: `mcp__4_5v_mcp__analyze_image`

Extract text and speaker information from poster images.

**Usage**:
```python
mcp__4_5v_mcp__analyze_image(
    image_source="/path/to/poster.jpg",
    prompt="Extract the following information from this academic poster:
1. Speaker name
2. Talk title
3. Date and time
4. Location
5. Speaker affiliation/institution
6. Any keywords or topics mentioned

Provide the information in a structured format."
)
```

**Parameters**:
- `image_source` (required): Local file path or remote URL
- `prompt` (required): What to extract from image

**Returns**: Structured text with extracted information

**Best Practices**:
- Use specific prompts for better extraction
- Ask for structured output (lists, JSON-like format)
- Include context (academic poster, talk announcement)

### 2. Web Search: `mcp__web-search-prime__webSearchPrime`

Search for papers and information about the speaker.

**Usage**:
```python
mcp__web-search-prime__webSearchPrime(
    search_query="[speaker name] [topic] paper",
    search_recency_filter="oneYear",  # Last year
    content_size="high",              # More context
    location="us"
)
```

**Parameters**:
- `search_query` (required): Search keywords
- `search_recency_filter` (optional): oneDay, oneWeek, oneMonth, oneYear, noLimit
- `content_size` (optional): medium (default), high
- `location` (optional): cn, us
- `search_domain_filter` (optional): Limit to specific domains

**Returns**: Search results with titles, URLs, summaries

### 3. Web Fetch: `mcp__web_reader__webReader`

Fetch full content of papers from URLs.

**Usage**:
```python
mcp__web_reader__webReader(
    url="https://arxiv.org/abs/1706.03762",
    return_format="markdown",
    retain_images=False,
    with_links_summary=False
)
```

**Parameters**:
- `url` (required): URL to fetch
- `return_format` (optional): markdown (default), text
- `retain_images` (optional): true (default), false
- `with_links_summary` (optional): true, false (default)

**Returns**: Full page content as markdown or text

## Workflow Implementation

### Step 1: Poster Analysis

```python
def analyze_poster(poster_path):
    """Extract information from poster image"""

    prompt = """Extract from this academic talk poster:
1. Speaker full name
2. Complete talk title
3. Date and time
4. Location/venue
5. Speaker institution/affiliation
6. Key topics or keywords

Format as:
Speaker: ...
Title: ...
Date: ...
Location: ...
Institution: ...
Topics: ...
"""

    result = mcp__4_5v_mcp__analyze_image(
        image_source=poster_path,
        prompt=prompt
    )

    # Parse extracted information
    info = parse_speaker_info(result)
    return info
```

### Step 2: Paper Search

```python
def search_papers(speaker_name, topics, time_range="oneYear"):
    """Search for speaker's papers"""

    # Build search query
    query = f'"{speaker_name}" paper'

    if topics:
        query += f" {topics}"

    # Search with recency filter
    results = mcp__web-search-prime__webSearchPrime(
        search_query=query,
        search_recency_filter=time_range,
        content_size="high"
    )

    return results
```

### Step 3: Paper Analysis

```python
def analyze_papers(search_results, talk_topic):
    """Analyze papers and generate summaries"""

    papers = []

    for result in search_results:
        # Fetch full paper content
        content = mcp__web_reader__webReader(
            url=result['url'],
            return_format="markdown",
            retain_images=False
        )

        # Extract abstract and key points
        paper_info = extract_paper_info(content)

        # Calculate relevance to talk
        relevance = calculate_relevance(
            paper_info['topics'],
            talk_topic
        )

        papers.append({
            'title': result['title'],
            'authors': paper_info['authors'],
            'year': paper_info['year'],
            'abstract': paper_info['abstract'],
            'link': result['url'],
            'relevance': relevance,
            'summary': generate_summary(paper_info)
        })

    # Sort by relevance
    papers.sort(key=lambda x: x['relevance'], reverse=True)

    return papers
```

### Step 4: Report Generation

```python
def generate_report(speaker_info, papers, talk_topic):
    """Generate markdown report"""

    report = f"""# Talk 分析报告

## 讲者信息
- **姓名**: {speaker_info['name']}
- **机构**: {speaker_info['institution']}
- **研究方向**: {infer_research_area(papers)}

## Talk 信息
- **标题**: {speaker_info['title']}
- **时间**: {speaker_info['date']}
- **地点**: {speaker_info['location']}
- **主题关键词**: {speaker_info['topics']}

## 相关论文

"""

    for i, paper in enumerate(papers[:10], 1):  # Top 10 papers
        report += f"""### {i}. {paper['title']}
**作者**: {', '.join(paper['authors'])}
**发表年份**: {paper['year']}
**相关性**: {'⭐' * (paper['relevance'] // 20)} ({paper['relevance']}/100)
**链接**: [{paper['link']}]({paper['link']})

**摘要**:
{paper['summary']}

**核心贡献**:
{chr(10).join(f"- {c}" for c in paper['contributions'])}

**与Talk的关联**: {paper['connection_to_talk']}

---

"""

    report += f"""## 总结

{generate_overall_summary(speaker_info, papers)}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

    return report
```

## Helper Functions

### Relevance Calculation

```python
def calculate_relevance(paper_topics, talk_topic):
    """Calculate relevance score (0-100)"""

    talk_keywords = extract_keywords(talk_topic)
    paper_keywords = extract_keywords(' '.join(paper_topics))

    # Calculate overlap
    overlap = set(talk_keywords) & set(paper_keywords)
    relevance = (len(overlap) / len(talk_keywords)) * 100

    # Boost for direct topic matches
    if any(kw in talk_topic.lower() for kw in paper_keywords):
        relevance += 20

    return min(relevance, 100)
```

### Summary Generation

```python
def generate_summary(paper_info):
    """Generate Chinese summary of paper"""

    # Extract first 2-3 sentences of abstract
    abstract = paper_info['abstract']
    sentences = abstract.split('.')

    # Translate key points (simplified)
    summary_points = [
        translate_to_chinese(sentences[0]) if len(sentences) > 0 else "",
        translate_to_chinese(sentences[1]) if len(sentences) > 1 else ""
    ]

    return ' '.join(summary_points)
```

### Research Area Inference

```python
def infer_research_area(papers):
    """Infer speaker's research area from papers"""

    all_topics = []
    for paper in papers:
        all_topics.extend(paper['topics'])

    # Count topic frequency
    topic_counts = Counter(all_topics)

    # Get top 3 topics
    top_topics = [topic for topic, _ in topic_counts.most_common(3)]

    return ', '.join(top_topics)
```

## Error Handling

### Image Analysis Errors

```python
def safe_analyze_poster(poster_path):
    """Analyze poster with error handling"""

    try:
        result = mcp__4_5v_mcp__analyze_image(
            image_source=poster_path,
            prompt="Extract speaker and talk information..."
        )

        if not result or "error" in result.lower():
            return manual_input_fallback()

        return parse_speaker_info(result)

    except Exception as e:
        logger.error(f"Poster analysis failed: {e}")
        return manual_input_fallback()
```

### Search Errors

```python
def safe_search_papers(speaker_name, topics, max_retries=3):
    """Search papers with retry logic"""

    for attempt in range(max_retries):
        try:
            results = mcp__web-search-prime__webSearchPrime(
                search_query=f'"{speaker_name}" {topics} paper',
                search_recency_filter="oneYear"
            )

            if results:
                return results

        except Exception as e:
            logger.warning(f"Search attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff

    return []  # Return empty if all retries fail
```

## Best Practices

### Search Strategy

1. **Use exact phrases**: Quote speaker name for precise matches
2. **Add context**: Include "paper", "publication", "research"
3. **Filter by time**: Use recency filter for recent work
4. **Multiple searches**: Vary query if initial results are poor

### Paper Selection

- Prioritize recent papers (1-3 years)
- Filter by relevance to talk topic
- Limit to top 10-15 most relevant
- Include cross-disciplinary work if relevant

### Summary Quality

- Extract key contributions (not just abstract)
- Translate technical terms accurately
- Maintain academic tone
- Keep summaries concise (200-300 characters)

## Data Sources

### Primary Sources

- **arXiv.org**: Preprints and CS papers
- **Google Scholar**: Comprehensive academic search
- **DBLP**: Computer science bibliography
- **University websites**: Author homepages

### Search Priority

1. Author's Google Scholar profile
2. arXiv search with author name
3. DBLP publication list
4. University/research group website

## Configuration

```python
# Search settings
DEFAULT_TIME_RANGE = "oneYear"  # Search last year
MAX_PAPERS = 15                # Max papers to analyze
MIN_RELEVANCE = 40            # Min relevance score to include

# Summary settings
SUMMARY_LENGTH = 200           # Max characters per summary
MAX_CONTRIBUTIONS = 5          # Max contributions to list

# Report settings
TOP_N_PAPERS = 10             # Papers to include in report
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Poster text not extracted | Try higher resolution image, manual input |
| No papers found | Widen time range, remove name quotes, check spelling |
| Papers irrelevant | Check if speaker name is common, add institution |
| Can't access paper | Try arXiv version, author's homepage |
| Summary too long | Truncate abstract, focus on key points |

## Performance Optimization

- **Cache search results**: Store in memory for duplicate queries
- **Parallel fetching**: Fetch multiple papers concurrently
- **Rate limiting**: Respect API limits with delays
- **Incremental processing**: Process papers as search returns come in

## Dependencies

All MCP tools are server-side integrations:
- `4_5v-mcp` for image analysis
- `web-search-prime` for search
- `web-reader` for content fetching

No additional Python packages required.
