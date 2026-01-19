#!/usr/bin/env python3
"""
arXiv Search Module

Provides search functionality for arXiv papers with category and date filtering.
Integrates with arXiv API while respecting rate limiting and constitutional requirements.
"""

from __future__ import annotations

import time
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
import re
import feedparser

# Constants
ARXIV_API_BASE_URL = "http://export.arxiv.org/api/query"
RATE_LIMIT_DELAY = 3.0  # Conservative 3-second delay per research findings
MAX_RESULTS_PER_REQUEST = 2000
NAMESPACE = {'atom': 'http://www.w3.org/2005/Atom', 'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'}

@dataclass
class SearchQuery:
    """Represents user's search request with all filters and parameters."""
    keywords: Optional[str] = None
    categories: List[str] = None
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    max_results: int = 100
    sort_by: str = "relevance"
    sort_order: str = "descending"

    def __post_init__(self):
        if self.categories is None:
            self.categories = []
        self.validate()

    def validate(self):
        """Validate SearchQuery parameters."""
        # Validate max_results
        if not 1 <= self.max_results <= MAX_RESULTS_PER_REQUEST:
            raise ValueError(f"max_results must be between 1 and {MAX_RESULTS_PER_REQUEST}")

        # Validate sort_by
        valid_sort_options = ["relevance", "submittedDate", "lastUpdatedDate"]
        if self.sort_by not in valid_sort_options:
            raise ValueError(f"sort_by must be one of: {valid_sort_options}")

        # Validate sort_order
        if self.sort_order not in ["ascending", "descending"]:
            raise ValueError("sort_order must be 'ascending' or 'descending'")

        # Validate date range
        if self.date_start and self.date_end:
            if self.date_start > self.date_end:
                raise ValueError("date_start must be <= date_end")

        # Validate categories (basic check, full validation in ArxivSearchClient)
        for category in self.categories:
            if not isinstance(category, str) or not category.strip():
                raise ValueError(f"Invalid category: {category}")

        # Validate keywords
        if self.keywords is not None and not isinstance(self.keywords, str):
            raise ValueError("keywords must be a string")

    def has_keywords(self) -> bool:
        """Check if query has meaningful keywords."""
        return bool(self.keywords is not None and self.keywords.strip())

    def has_categories(self) -> bool:
        """Check if query has category filters."""
        return bool(self.categories)

    def has_date_filter(self) -> bool:
        """Check if query has date range filter."""
        return bool(self.date_start or self.date_end)

@dataclass
class SearchResult:
    """Represents individual paper matching search criteria."""
    id: str
    title: str
    authors: List[str]
    summary: str
    published: datetime
    updated: datetime
    categories: List[str]
    links: Dict[str, str]
    relevance_score: Optional[float] = None

    def get_arxiv_id(self) -> str:
        """Extract arXiv ID from full ID string."""
        # Extract ID like "cs.AI/2312.12345" from full URL
        if '/abs/' in self.id:
            return self.id.split('/abs/')[-1]
        elif self.id.startswith('http://arxiv.org/abs/'):
            return self.id.replace('http://arxiv.org/abs/', '')
        return self.id

    def get_paper_url(self) -> Optional[str]:
        """Get paper URL."""
        return self.links.get('paper')

    def get_pdf_url(self) -> Optional[str]:
        """Get PDF URL."""
        return self.links.get('pdf')

    def get_primary_category(self) -> Optional[str]:
        """Get the primary category (first one listed)."""
        return self.categories[0] if self.categories else None

    def get_summary_snippet(self, max_length: int = 200) -> str:
        """Get a shortened version of the summary."""
        if len(self.summary) <= max_length:
            return self.summary
        return self.summary[:max_length-3] + "..."

@dataclass
class SearchResultSet:
    """Container for all papers matching a search query with metadata."""
    query: SearchQuery
    total_results: int
    papers: List[SearchResult]
    execution_time: float
    filters_applied: Dict[str, Any]

    def get_papers_by_category(self) -> Dict[str, List[SearchResult]]:
        """Group papers by their primary category."""
        papers_by_category = {}
        for paper in self.papers:
            primary_cat = paper.get_primary_category()
            if primary_cat:
                if primary_cat not in papers_by_category:
                    papers_by_category[primary_cat] = []
                papers_by_category[primary_cat].append(paper)
        return papers_by_category

    def has_results(self) -> bool:
        """Check if search returned any results."""
        return len(self.papers) > 0

    def get_result_count(self) -> int:
        """Get number of papers returned."""
        return len(self.papers)

class ArxivSearchClient:
    """Main search client for arXiv API with rate limiting and error handling."""

    def __init__(self, rate_limit_delay: float = RATE_LIMIT_DELAY):
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0.0

    def _rate_limit_delay(self):
        """Implement rate limiting between API calls."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_api_request(self, url: str, max_retries: int = 3) -> bytes:
        """Make API request with rate limiting and retry logic."""
        for attempt in range(max_retries):
            try:
                self._rate_limit_delay()

                with urllib.request.urlopen(url, timeout=30) as response:
                    if response.status == 200:
                        return response.read()
                    else:
                        raise urllib.error.HTTPError(url, response.status, response.reason, response.headers, None)

            except urllib.error.HTTPError as e:
                if e.code == 429:  # Too Many Requests
                    if attempt < max_retries - 1:
                        wait_time = self.rate_limit_delay * (2 ** attempt)  # Exponential backoff
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception("Rate limit exceeded after multiple retries")
                else:
                    raise e
            except urllib.error.URLError as e:
                if attempt < max_retries - 1:
                    time.sleep(self.rate_limit_delay)
                    continue
                else:
                    raise Exception(f"Network error after {max_retries} attempts: {e}")

        raise Exception(f"Failed to complete API request after {max_retries} attempts")

    def _build_search_query(self, query: SearchQuery) -> str:
        """Build arXiv API search query string from SearchQuery object."""
        query_parts = []

        # Add keyword search (only if keywords are provided)
        if query.has_keywords():
            # Handle exact phrase matching with quotes
            processed_keywords = query.keywords.strip()
            if processed_keywords.startswith('"') and processed_keywords.endswith('"'):
                # Exact phrase search
                query_parts.append(f'all:{processed_keywords}')
            else:
                # Regular keyword search (default to title and abstract)
                if ' ' in processed_keywords:
                    # Multiple keywords - use AND logic
                    keywords = processed_keywords.split()
                    keyword_parts = []
                    for keyword in keywords:
                        if keyword.startswith('"') and keyword.endswith('"'):
                            keyword_parts.append(f'all:{keyword}')
                        else:
                            keyword_parts.append(f'all:"{keyword}"')
                    query_parts.append('(' + ' AND '.join(keyword_parts) + ')')
                else:
                    # Single keyword
                    query_parts.append(f'all:"{processed_keywords}"')

        # Add category filters
        if query.categories:
            category_parts = []
            for category in self._validate_categories(query.categories):
                category_parts.append(f'cat:{category}')

            if len(category_parts) == 1:
                query_parts.append(category_parts[0])
            else:
                query_parts.append('(' + ' OR '.join(category_parts) + ')')

        # Add date range filter
        if query.date_start or query.date_end:
            date_filter = self._build_date_filter(query.date_start, query.date_end)
            if date_filter:
                query_parts.append(date_filter)

        return ' AND '.join(query_parts) if query_parts else 'all:*'

    def _build_date_filter(self, date_start: Optional[datetime], date_end: Optional[datetime]) -> Optional[str]:
        """Build date range filter for arXiv API."""
        # arXiv only supports submittedDate filtering
        if not date_start and not date_end:
            return None

        # Format dates for arXiv API (YYYYMMDDHHMM)
        if date_start:
            start_str = date_start.strftime('%Y%m%d%H%M')
        else:
            # Use a very early date if no start date specified
            start_str = '199001010000'

        if date_end:
            end_str = date_end.strftime('%Y%m%d%H%M')
        else:
            # Use current date/time if no end date specified
            end_str = datetime.now(timezone.utc).strftime('%Y%m%d%H%M')

        return f'submittedDate:[{start_str} TO {end_str}]'

    def _parse_arxiv_response(self, xml_data: bytes) -> SearchResultSet:
        """Parse XML response from arXiv API into SearchResultSet."""
        try:
            # Parse XML using ElementTree
            root = ET.fromstring(xml_data)

            # Extract total results
            total_results_elem = root.find('.//opensearch:totalResults', NAMESPACE)
            total_results = int(total_results_elem.text) if total_results_elem is not None else 0

            # Parse individual paper entries
            papers = []
            for entry in root.findall('.//atom:entry', NAMESPACE):
                paper = self._parse_paper_entry(entry)
                papers.append(paper)

            # Create SearchResultSet (this will be updated with actual query later)
            return SearchResultSet(
                query=None,  # Will be set by calling method
                total_results=total_results,
                papers=papers,
                execution_time=0.0,  # Will be set by calling method
                filters_applied={}
            )

        except ET.ParseError as e:
            raise Exception(f"Failed to parse arXiv XML response: {e}")
        except Exception as e:
            raise Exception(f"Error processing arXiv response: {e}")

    def _parse_paper_entry(self, entry) -> SearchResult:
        """Parse individual paper entry from XML."""
        try:
            # Extract paper ID
            id_elem = entry.find('atom:id', NAMESPACE)
            paper_id = id_elem.text if id_elem is not None else ""

            # Extract title
            title_elem = entry.find('atom:title', NAMESPACE)
            title = title_elem.text if title_elem is not None else ""

            # Extract summary (abstract)
            summary_elem = entry.find('atom:summary', NAMESPACE)
            summary = summary_elem.text if summary_elem is not None else ""

            # Extract published and updated dates
            published_elem = entry.find('atom:published', NAMESPACE)
            published = datetime.fromisoformat(published_elem.text.replace('Z', '+00:00')) if published_elem is not None else datetime.now(timezone.utc)

            updated_elem = entry.find('atom:updated', NAMESPACE)
            updated = datetime.fromisoformat(updated_elem.text.replace('Z', '+00:00')) if updated_elem is not None else published

            # Extract authors
            authors = []
            for author_elem in entry.findall('atom:author', NAMESPACE):
                name_elem = author_elem.find('atom:name', NAMESPACE)
                if name_elem is not None:
                    authors.append(name_elem.text)

            # Extract categories
            categories = []
            for category_elem in entry.findall('atom:category', NAMESPACE):
                category = category_elem.get('term')
                if category:
                    categories.append(category)

            # Extract links
            links = {}
            for link_elem in entry.findall('atom:link', NAMESPACE):
                rel = link_elem.get('rel')
                href = link_elem.get('href')
                if rel and href:
                    if rel == 'alternate':
                        links['paper'] = href
                    elif rel == 'related' and href.endswith('.pdf'):
                        links['pdf'] = href

            return SearchResult(
                id=paper_id,
                title=title,
                authors=authors,
                summary=summary,
                published=published,
                updated=updated,
                categories=categories,
                links=links
            )

        except Exception as e:
            raise Exception(f"Error parsing paper entry: {e}")

    def _validate_categories(self, categories: List[str]) -> List[str]:
        """Validate and normalize category codes against arXiv taxonomy."""
        # Define valid arXiv categories (focusing on computer science for now)
        VALID_CATEGORIES = {
            # Computer Science
            'cs.AI', 'cs.AR', 'cs.CC', 'cs.CE', 'cs.CG', 'cs.CL', 'cs.CR', 'cs.CV',
            'cs.CY', 'cs.DB', 'cs.DC', 'cs.DL', 'cs.DM', 'cs.DS', 'cs.ET', 'cs.FL',
            'cs.GL', 'cs.GR', 'cs.GT', 'cs.HC', 'cs.IR', 'cs.LG', 'cs.LO', 'cs.MA',
            'cs.MM', 'cs.MS', 'cs.NA', 'cs.NE', 'cs.NI', 'cs.OH', 'cs.OS', 'cs.PF',
            'cs.PL', 'cs.RO', 'cs.SC', 'cs.SD', 'cs.SE', 'cs.SI', 'cs.SY',
            # Mathematics (selected)
            'math.AG', 'math.AT', 'math.CA', 'math.CO', 'math.CT', 'math.CV',
            'math.DG', 'math.DS', 'math.FA', 'math.GM', 'math.GN', 'math.GR',
            'math.GT', 'math.HO', 'math.IT', 'math.KT', 'math.LO', 'math.MP',
            'math.NA', 'math.NT', 'math.OA', 'math.OC', 'math.PR', 'math.QA',
            'math.RA', 'math.RT', 'math.SG', 'math.SP', 'math.ST',
            # Physics (selected)
            'physics.ao-ph', 'physics.atom-ph', 'physics.atm-clus', 'physics.bio-ph',
            'physics.comp-ph', 'physics.data-an', 'physics.flu-dyn', 'physics.gen-ph',
            'physics.geo-ph', 'physics.hist-ph', 'physics.ins-det', 'physics.med-ph',
            'physics.optics', 'physics.plasm-ph', 'physics.pop-ph', 'physics.soc-ph',
            'physics.space-ph'
        }

        validated_categories = []
        for category in categories:
            normalized_category = category.strip()
            if normalized_category in VALID_CATEGORIES:
                validated_categories.append(normalized_category)
            else:
                raise ValueError(f"Invalid arXiv category: {category}. "
                               f"Valid categories include: {sorted(VALID_CATEGORIES)[:5]}... "
                               f"See arXiv category taxonomy for complete list.")

        return validated_categories

    def _detect_filter_conflicts(self, query: SearchQuery) -> List[str]:
        """Detect potential conflicts or issues with search filters."""
        warnings = []

        # Check for overly restrictive date ranges
        if query.date_start and query.date_end:
            date_range_days = (query.date_end - query.date_start).days
            if date_range_days < 1:
                warnings.append("Date range is less than 1 day - consider using a wider range")
            elif date_range_days > 365:
                warnings.append("Date range is very wide - results may be numerous")

        # Check for future dates
        now = datetime.now(timezone.utc)
        if query.date_end and query.date_end > now:
            warnings.append("End date is in the future - limiting to current date")
            query.date_end = now

        # Check for very old dates
        if query.date_start and query.date_start < datetime(1990, 1, 1, tzinfo=timezone.utc):
            warnings.append("Start date is before 1990 - arXiv was founded in 1991")

        # Check for too many categories
        if len(query.categories) > 10:
            warnings.append("Many categories specified - consider narrowing your focus")

        # Check for empty keywords with only filters
        if not query.has_keywords() and not query.has_categories() and not query.has_date_filter():
            warnings.append("No search criteria provided - will return recent papers")

        # Check for empty keywords with categories and date (this is OK for daily fetch)
        if not query.has_keywords() and query.has_categories() and query.has_date_filter():
            pass  # This is a valid use case (e.g., fetch all papers from categories for a date range)

        return warnings

    def _generate_smart_suggestions(self, query: SearchQuery, result_count: int) -> List[str]:
        """Generate suggestions for improving search results."""
        suggestions = []

        if result_count == 0:
            # No results - provide broadening suggestions
            if query.has_keywords():
                suggestions.append("Try using different or more general keywords")
                suggestions.append("Consider using exact phrases with quotes for specific terms")

            if query.has_categories():
                suggestions.append("Try removing some category filters")
                suggestions.append("Consider broader categories (e.g., cs.AI instead of cs.LG)")

            if query.has_date_filter():
                suggestions.append("Try expanding the date range")

            suggestions.append("Use the --query flag for advanced arXiv syntax")

        elif result_count < 5:
            # Very few results - suggest expanding search
            if query.has_keywords():
                suggestions.append("Consider using more general keywords")

            if len(query.categories) > 1:
                suggestions.append("Try using fewer categories")

            if query.has_date_filter():
                suggestions.append("Consider widening the date range")

        elif result_count > 500:
            # Many results - suggest narrowing search
            suggestions.append("Consider adding more specific keywords")
            suggestions.append("Try adding category filters to focus on relevant fields")
            suggestions.append("Use date range filtering for recent papers")
            suggestions.append("Try using exact phrases with quotes")

        return suggestions

    def search(self, query: SearchQuery) -> SearchResultSet:
        """Execute search query and return results."""
        start_time = time.time()

        try:
            # Validate categories if provided
            if query.categories:
                validated_categories = self._validate_categories(query.categories)
                query.categories = validated_categories

            # Detect filter conflicts and issues
            warnings = self._detect_filter_conflicts(query)

            # Build search query string
            search_query = self._build_search_query(query)

            # Build API URL
            url_params = {
                'search_query': search_query,
                'max_results': str(min(query.max_results, MAX_RESULTS_PER_REQUEST)),
                'sortBy': query.sort_by,
                'sortOrder': query.sort_order
            }

            url = f"{ARXIV_API_BASE_URL}?{urllib.parse.urlencode(url_params)}"

            # Make API request
            xml_data = self._make_api_request(url)

            # Parse response
            result_set = self._parse_arxiv_response(xml_data)

            # Update result set with query metadata
            result_set.query = query
            result_set.execution_time = time.time() - start_time

            # Generate smart suggestions based on results
            suggestions = self._generate_smart_suggestions(query, len(result_set.papers))

            result_set.filters_applied = {
                'keywords': query.keywords,
                'categories': query.categories,
                'date_start': query.date_start.isoformat() if query.date_start else None,
                'date_end': query.date_end.isoformat() if query.date_end else None,
                'max_results': query.max_results,
                'sort_by': query.sort_by,
                'sort_order': query.sort_order,
                'warnings': warnings,
                'suggestions': suggestions
            }

            return result_set

        except urllib.error.HTTPError as e:
            # Handle specific HTTP errors gracefully
            if e.code == 503:
                # Service unavailable - provide helpful message
                return SearchResultSet(
                    query=query,
                    total_results=0,
                    papers=[],
                    execution_time=time.time() - start_time,
                    filters_applied={
                        'error': 'arXiv API is temporarily unavailable (503). Please try again in a few minutes.',
                        'service_unavailable': True,
                        'retry_suggested': True
                    }
                )
            elif e.code == 429:
                # Rate limit exceeded
                return SearchResultSet(
                    query=query,
                    total_results=0,
                    papers=[],
                    execution_time=time.time() - start_time,
                    filters_applied={
                        'error': 'arXiv API rate limit exceeded (429). Please wait longer between requests.',
                        'rate_limit_exceeded': True,
                        'retry_suggested': True
                    }
                )
            else:
                return SearchResultSet(
                    query=query,
                    total_results=0,
                    papers=[],
                    execution_time=time.time() - start_time,
                    filters_applied={'error': f'HTTP {e.code}: {e.reason}'}
                )
        except urllib.error.URLError as e:
            # Network-related errors
            return SearchResultSet(
                query=query,
                total_results=0,
                papers=[],
                execution_time=time.time() - start_time,
                filters_applied={
                    'error': f'Network error: Unable to connect to arXiv API. Check your internet connection.',
                    'network_error': True,
                    'retry_suggested': True
                }
            )
        except Exception as e:
            # Create empty result set with error information
            return SearchResultSet(
                query=query,
                total_results=0,
                papers=[],
                execution_time=time.time() - start_time,
                filters_applied={'error': str(e)}
            )