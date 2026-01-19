# Data Model: Search Function

**Date**: 2025-12-19
**Purpose**: Define data structures for search functionality

## Core Entities

### SearchQuery
Represents user's search request with all filters and parameters.

**Fields**:
- `keywords` (str): Search terms and phrases
- `categories` (List[str]): List of arXiv categories to filter by
- `date_start` (datetime, optional): Start date for date range filtering (UTC)
- `date_end` (datetime, optional): End date for date range filtering (UTC)
- `max_results` (int): Maximum number of results to return
- `sort_by` (str): Sort order ("relevance", "submittedDate", "lastUpdatedDate")
- `sort_order` (str): Sort direction ("ascending", "descending")

**Validation Rules**:
- `categories` must be valid arXiv category codes
- `date_start` must be <= `date_end` if both provided
- `max_results` must be between 1 and 2000 (API limit)
- `sort_by` must be one of allowed values

### SearchResult
Represents individual paper matching search criteria.

**Fields**:
- `id` (str): arXiv paper ID (e.g., "cs.AI/2312.12345")
- `title` (str): Paper title
- `authors` (List[str]): List of author names
- `summary` (str): Paper abstract
- `published` (datetime): Publication date (UTC)
- `updated` (datetime): Last updated date (UTC)
- `categories` (List[str]): List of arXiv categories
- `links` (Dict[str, str]): URLs to paper and PDF
- `relevance_score` (float, optional): Search relevance score if available

**Relationships**:
- Belongs to one `SearchResultSet`
- Has many `Category` entities

### SearchResultSet
Container for all papers matching a search query with metadata.

**Fields**:
- `query` (SearchQuery): Original search request
- `total_results` (int): Total number of papers found
- `papers` (List[SearchResult]): List of matching papers
- `execution_time` (float): Time taken to execute search (seconds)
- `filters_applied` (Dict[str, any]): Active filters used in search

**State Transitions**:
- `empty` → `loading` → `complete` OR `error`
- `complete` → `paginated` (if more results available)

### Filter
Represents individual search constraints.

**Types**:
- `KeywordFilter`: Search terms and phrase matching
- `CategoryFilter`: Category inclusion/exclusion
- `DateRangeFilter`: Date range constraints
- `SortFilter`: Result ordering preferences

### Category
Valid arXiv category with metadata.

**Fields**:
- `code` (str): Category code (e.g., "cs.AI")
- `name` (str): Full category name
- `description` (str): Category description

**Examples**:
- `cs.AI`: Artificial Intelligence
- `cs.LG`: Machine Learning
- `cs.CV`: Computer Vision
- `cs.OS`: Operating Systems

## Data Flow

```
User Input → SearchQuery → API Request → XML Response → SearchResultSet → SearchResult
```

1. **Input Processing**: User provides search terms and optional filters
2. **Query Construction**: SearchQuery built with validation
3. **API Communication**: Query sent to arXiv API with rate limiting
4. **Response Parsing**: XML response parsed into SearchResult entities
5. **Result Assembly**: SearchResultSet created with metadata
6. **Output Generation**: Results formatted for CLI display

## Validation Rules

### Category Validation
- Must match official arXiv category taxonomy
- Case-sensitive category codes
- Primary categories only (no secondary categories)

### Date Validation
- All dates in UTC timezone
- Date range must be reasonable (not future dates)
- Submitted date format: YYYYMMDDHHMM

### Keyword Validation
- Supports boolean operators: AND, OR, NOT
- Phrase matching with quotes: "exact phrase"
- Field-specific searches: ti:, abs:, all:

## Integration with Existing Code

### Compatibility
- Reuses existing paper data structures from `arxiv_daily.py`
- Maintains same output format (markdown reports)
- Compatible with existing CLI argument parsing

### Extensions
- New search-specific methods added to existing classes
- Search results use same formatting functions
- Error handling follows existing patterns

### Migration
- Existing daily paper functionality unchanged
- Search added as additional CLI subcommand
- No breaking changes to current API