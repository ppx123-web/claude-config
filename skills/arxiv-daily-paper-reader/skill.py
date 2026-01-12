#!/usr/bin/env python3
"""
arXiv Daily Paper Reader Skill Implementation
Main entry point for Claude Skills system
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Add current directory to Python path to import local modules
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from search_module import ArxivSearchClient, SearchQuery
    from arxiv_daily import ArxivDailyPaperReader
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("Please ensure all dependencies are installed:")
    print("  pip install feedparser>=6.0.10")
    sys.exit(1)

def parse_skill_arguments():
    """Parse arguments passed from Claude Skills system."""
    parser = argparse.ArgumentParser(
        description="arXiv Paper Search and Daily Fetching",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Daily fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch yesterday papers')
    fetch_parser.add_argument(
        '--cats', '--categories',
        dest='categories',
        nargs='+',
        default=['cs.OS', 'cs.PL', 'cs.SE', 'cs.AI'],
        help='arXiv categories to fetch'
    )
    fetch_parser.add_argument(
        '--max-papers',
        type=int,
        default=50,
        help='Maximum papers per category'
    )
    fetch_parser.add_argument(
        '--output-format',
        choices=['markdown', 'json', 'both'],
        default='markdown',
        help='Output format'
    )

    # Search command
    search_parser = subparsers.add_parser('search', help='Search arXiv papers')
    search_parser.add_argument(
        '--cats', '--categories',
        dest='categories',
        nargs='+',
        required=True,
        help='arXiv categories to search (required)'
    )
    search_parser.add_argument(
        '--days', '-d',
        type=int,
        default=30,
        help='Search papers from last N days (default: 30)'
    )
    search_parser.add_argument(
        '--max-results',
        type=int,
        default=15,
        help='Maximum results to return (default: 15)'
    )
    search_parser.add_argument(
        '--output-format',
        choices=['markdown', 'json', 'both', 'preview'],
        default='markdown',
        help='Output format (default: markdown)'
    )

    # If no arguments provided, check if we're being called with raw arguments
    if len(sys.argv) == 1:
        # Try to parse from environment or stdin for Claude Skills integration
        return None, None

    return parser.parse_args(), parser

def handle_daily_fetch(args):
    """Handle daily paper fetching."""
    try:
        print("🔍 arXiv Daily Paper Reader")
        print(f"Categories: {', '.join(args.categories)}")
        print("Fetching yesterday's papers...")
        print()

        reader = ArxivDailyPaperReader()
        reader.categories = args.categories

        # Fetch papers
        reader.fetch_all_papers()

        if not reader.papers:
            print("❌ No papers found for yesterday!")
            return {}

        print(f"✅ Found {len(reader.papers)} papers total")

        # Generate output
        result = {
            "type": "daily_fetch",
            "date": datetime.now().isoformat(),
            "categories": args.cats,
            "total_papers": len(reader.papers),
            "papers": []
        }

        if args.output_format in ['markdown', 'both']:
            # Generate markdown report
            current_date = datetime.now().strftime("%Y-%m-%d")
            report_file = f"/tmp/arxiv_daily_report_{current_date}.md"
            report_content = reader.generate_markdown_report(report_file)
            result["markdown_report"] = report_content
            result["markdown_file"] = report_file

        if args.output_format in ['json', 'both']:
            # Save JSON data
            papers_data = []
            for paper in reader.papers:
                papers_data.append({
                    "id": paper.get('id', ''),
                    "title": paper.get('title', ''),
                    "authors": paper.get('authors', []),
                    "summary": paper.get('summary', ''),
                    "published": paper.get('published', ''),
                    "categories": paper.get('categories', []),
                    "link": paper.get('link', ''),
                    "pdf_link": paper.get('pdf_link', '')
                })
            result["papers"] = papers_data

            if args.output_format == 'json':
                current_date = datetime.now().strftime("%Y-%m-%d")
                json_file = f"/tmp/arxiv_papers_{current_date}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                result["json_file"] = json_file

        # Print summary
        papers_by_category = {}
        for paper in reader.papers:
            primary_cat = paper.get('categories', ['Unknown'])[0]
            if primary_cat not in papers_by_category:
                papers_by_category[primary_cat] = 0
            papers_by_category[primary_cat] += 1

        print(f"\n📊 Summary by category:")
        for category, count in sorted(papers_by_category.items()):
            print(f"  {category}: {count} papers")

        return result

    except Exception as e:
        print(f"❌ Error during daily fetch: {e}")
        return {"error": str(e)}

def handle_search(args):
    """Handle paper search."""
    try:
        print("🔍 arXiv Search")

        categories = args.categories
        print(f"Categories: {', '.join(categories)}")

        # Parse date filters
        date_end = datetime.now(timezone.utc)
        date_start = date_end - timedelta(days=args.days)

        # Create SearchQuery
        query = SearchQuery(
            keywords=None,
            categories=categories,
            date_start=date_start,
            date_end=date_end,
            max_results=args.max_results,
            sort_by="submittedDate"
        )

        # Execute search
        print(f"Searching arXiv...")
        client = ArxivSearchClient()
        results = client.search(query)

        if not results.has_results():
            print("❌ No papers found matching your criteria.")
            if 'error' in results.filters_applied:
                print(f"Error: {results.filters_applied['error']}")
            return {"error": "No results found", "filters_applied": results.filters_applied}

        print(f"✅ Found {results.get_result_count()} papers in {results.execution_time:.2f}s")
        print(f"Total available: {results.total_results}")

        # Build result
        result = {
            "type": "search",
            "query": f"Categories: {', '.join(categories)}",
            "categories": categories,
            "total_results": results.total_results,
            "returned_count": results.get_result_count(),
            "execution_time": results.execution_time,
            "papers": []
        }

        # Add paper data
        for paper in results.papers:
            paper_data = {
                "id": paper.id,
                "title": paper.title,
                "authors": paper.authors,
                "summary": paper.summary,
                "published": paper.published.isoformat(),
                "categories": paper.categories,
                "paper_url": paper.get_paper_url(),
                "pdf_url": paper.get_pdf_url()
            }
            result["papers"].append(paper_data)

        # Handle different output formats
        if args.output_format in ['markdown', 'both']:
            # Generate markdown report
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            report_lines = [
                f"# arXiv Search Results",
                f"",
                f"**Categories:** {', '.join(categories)}",
                f"**Days:** {args.days}",
                f"**Total Results:** {results.total_results}",
                f"**Returned:** {results.get_result_count()} papers",
                f"**Execution Time:** {results.execution_time:.2f} seconds",
                f"",
                f"## Papers Found",
                f""
            ]

            for i, paper in enumerate(results.papers, 1):
                report_lines.extend([
                    f"**{i}. {paper.title}**",
                    f"*Authors:* {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}",
                    f"*Published:* {paper.published.strftime('%Y-%m-%d')}",
                    f"*Categories:* {', '.join(paper.categories[:3])}{'...' if len(paper.categories) > 3 else ''}",
                    f"**Summary:** {paper.get_summary_snippet(200)}",
                    f""
                ])

                paper_url = paper.get_paper_url()
                pdf_url = paper.get_pdf_url()
                if paper_url or pdf_url:
                    links = []
                    if paper_url:
                        links.append(f"[Read Paper]({paper_url})")
                    if pdf_url:
                        links.append(f"[PDF]({pdf_url})")
                    report_lines.append(f"*Links:* {' | '.join(links)}")
                report_lines.append("")

            result["markdown_report"] = "\n".join(report_lines)

            if args.output_format == 'markdown':
                report_file = f"/tmp/arxiv_search_results_{current_time}.md"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(result["markdown_report"])
                result["markdown_file"] = report_file

        if args.output_format in ['json', 'both']:
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            json_file = f"/tmp/arxiv_search_results_{current_time}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            result["json_file"] = json_file

        # Print summary
        papers_by_category = results.get_papers_by_category()
        if papers_by_category:
            print(f"\n📊 Results by category:")
            for category, papers in papers_by_category.items():
                print(f"  {category}: {len(papers)} papers")

        # Display suggestions if any
        if 'suggestions' in results.filters_applied and results.filters_applied['suggestions']:
            print(f"\n💡 Suggestions:")
            for suggestion in results.filters_applied['suggestions']:
                print(f"  • {suggestion}")

        return result

    except Exception as e:
        print(f"❌ Error during search: {e}")
        return {"error": str(e)}

def main():
    """Main skill entry point."""
    # Try to parse command line arguments
    args, parser = parse_skill_arguments()

    # If no command line arguments, try to determine intent from sys.argv
    if args is None:
        # Simple intent detection from remaining arguments
        if len(sys.argv) > 1:
            input_text = " ".join(sys.argv[1:])
            input_text = input_text.lower()

            # Determine if this is a search or daily fetch request
            if any(word in input_text for word in ['search', 'find', 'look for', '关键词', '搜索']):
                # Extract keywords from input
                if '--keywords' in input_text or '-k' in input_text:
                    # Try to parse properly
                    try:
                        args, _ = parse_skill_arguments()
                        if args is None:
                            args = parser.parse_args(['search', '--keywords', 'machine learning'])
                    except:
                        args = parser.parse_args(['search', '--keywords', 'machine learning'])
                else:
                    # Extract keywords after command
                    keywords = input_text.replace('search', '').replace('find', '').replace('look for', '').strip()
                    if not keywords:
                        keywords = "machine learning"  # default
                    args = parser.parse_args(['search', '--keywords', keywords])
            else:
                # Default to daily fetch
                args = parser.parse_args(['fetch'])
        else:
            # Default behavior - fetch daily papers
            args = parser.parse_args(['fetch'])

    # Execute the appropriate command
    if args.command == 'fetch':
        result = handle_daily_fetch(args)
    elif args.command == 'search':
        result = handle_search(args)
    else:
        result = {"error": "Unknown command"}

    # Output result as JSON for Claude Skills system
    if result:
        print("\n---CLAUDE_SKILL_RESULT---")
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    return result

if __name__ == "__main__":
    main()