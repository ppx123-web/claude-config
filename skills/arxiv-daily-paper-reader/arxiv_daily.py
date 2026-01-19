#!/usr/bin/env python3
"""
arXiv Daily Paper Reader Core Module

Provides core functionality for fetching and processing arXiv papers.
This module will be expanded as needed for the daily paper fetching functionality.
"""

from __future__ import annotations

import sys
from typing import List, Dict, Any
from datetime import datetime, timezone

class ArxivDailyPaperReader:
    """Main class for fetching and processing arXiv daily papers."""

    def __init__(self):
        """Initialize the paper reader with default categories."""
        self.categories = ["cs.OS", "cs.PL", "cs.SE", "cs.AI"]
        self.papers = []

    def fetch_all_papers(self):
        """Fetch papers from all configured categories."""
        from search_module import ArxivSearchClient, SearchQuery
        from datetime import timedelta

        # Calculate yesterday's date range
        now = datetime.now(timezone.utc)
        yesterday_end = now.replace(hour=23, minute=59, second=59)
        yesterday_start = yesterday_end - timedelta(days=1)
        yesterday_start = yesterday_start.replace(hour=0, minute=0, second=0, microsecond=0)

        print(f"Fetching papers from {yesterday_start.strftime('%Y-%m-%d')}...")

        # Create search query for yesterday's papers
        # Note: Use a wider date range to ensure we get papers
        # If the system date is in the future, get the most recent papers
        query = SearchQuery(
            keywords=None,  # No keywords to get all papers
            categories=self.categories,
            date_start=yesterday_start,
            date_end=yesterday_end,
            max_results=100,
            sort_by="submittedDate",
            sort_order="descending"
        )

        # Execute search
        client = ArxivSearchClient()
        results = client.search(query)

        # Convert SearchResult objects to dictionaries
        self.papers = []
        for paper in results.papers:
            self.papers.append({
                'id': paper.id,
                'title': paper.title,
                'authors': paper.authors,
                'summary': paper.summary,
                'published': paper.published.isoformat(),
                'categories': paper.categories,
                'link': paper.get_paper_url(),
                'pdf_link': paper.get_pdf_url()
            })

        print(f"Found {len(self.papers)} papers")

    def generate_markdown_report(self, output_file: str = None) -> str:
        """Generate markdown report for fetched papers."""
        # This will be implemented with the report generation logic
        if not self.papers:
            return "# No papers found to report"

        report = "# arXiv Daily Paper Report\n\n"
        report += f"Generated on: {datetime.now().strftime('%Y-%m-%d')}\n"
        report += f"Categories: {', '.join(self.categories)}\n"
        report += f"Total Papers: {len(self.papers)}\n\n"

        # Add paper details
        for paper in self.papers:
            report += f"## {paper.get('title', 'Untitled')}\n\n"
            report += f"*Authors:* {', '.join(paper.get('authors', []))}\n"
            report += f"*Published:* {paper.get('published', 'Unknown')}\n"
            report += f"*Categories:* {', '.join(paper.get('categories', []))}\n\n"

        return report

    def save_raw_data(self, output_file: str):
        """Save raw JSON data for further processing."""
        # This will be implemented with JSON saving logic
        pass

if __name__ == "__main__":
    # Test basic functionality
    reader = ArxivDailyPaperReader()
    print(f"Initialized with categories: {reader.categories}")