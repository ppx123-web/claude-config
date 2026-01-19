<!--
Sync Impact Report:
Version change: 0.0.0 → 1.0.0 (initial ratification)
Modified principles: None (new constitution)
Added sections: All sections added
Removed sections: None
Templates requiring updates:
  ✅ plan-template.md (aligned with Single Project structure)
  ✅ spec-template.md (aligned with functional requirements)
  ✅ tasks-template.md (aligned with CLI and Library task types)
Follow-up TODOs: None
-->

# arXiv Daily Paper Reader Constitution

## Core Principles

### I. Date-First Filtering
All paper fetching MUST filter by yesterday's UTC date range (00:00:00 to 23:59:59 UTC) without imposing arbitrary number restrictions. The system exists to deliver complete academic daily updates, not curated samples.

### II. Interface Architecture
Every core feature MUST be a command-line interface. The CLI provides user-friendly operation.

### III. Server Respect
Rate limiting between category fetches (minimum 1-second delays) is mandatory. All implementations MUST respect arXiv's infrastructure and include proper error handling for network issues.

### IV. Simplicity in Output
Primary output MUST be structured markdown reports organized by category. JSON export is optional but MUST use a consistent, flat data structure without nested complexity.

### V. UTC Time Consistency
All date handling, filtering, and timestamp operations MUST use UTC timezone exclusively. No local time conversions are permitted to ensure consistent behavior across geographic regions.

## Technical Constraints

### Technology Stack
- **Python 3.12+**: Primary language requirement
- **uv Package Manager**: Mandatory for dependency management
- **feedparser**: Required for arXiv RSS/Atom feed parsing
- **requests**: Required for HTTP operations
- **argparse**: For CLI argument parsing
- **pytest**: For testing framework

### Performance Requirements
- **Rate Limiting**: 1-second minimum delay between category fetches
- **Error Handling**: Graceful degradation when arXiv API is unavailable
- **Memory Efficiency**: Stream processing preferred over bulk loading each paper
- **No Artificial Limits**: Fetch ALL qualifying papers of each category, not arbitrary subsets

### File Organization
Single-project structure with clear separation:
- A cli file as the main entry point
- Server sub module for different functionalities
- Tests sub module for unit and integration tests, in tests dir
- Downloaded papers pdf to /tmp directory

## Development Standards

### Testing Requirements
- Functional testing of date filtering logic across UTC boundaries
- Integration testing with live arXiv API (respecting rate limits)
- CLI argument parsing validation

### Code Quality
- All public functions MUST have docstrings and type hints
- Error messages MUST be actionable and user-friendly
- No silent failures - all network/parsing errors MUST be logged or reported
- CLI output MUST include progress indicators and completion summaries, including report file path.

### Configuration Management
- CLI has powerful and clean arguments options.

## Governance

### Constitution Supremacy
This constitution supersedes all other project documentation and practices. All code changes, feature additions, and architectural decisions MUST comply with these principles.

### Amendment Process
- **Minor Changes**: Updates for clarification or non-behavioral changes increment PATCH version
- **New Features**: Adding new capabilities while maintaining existing principles increments MINOR version
- **Principle Changes**: Any modification to Core Principles requires MAJOR version increment
- All amendments MUST update this file and version according to semantic versioning

### Compliance Review
- All pull requests MUST reference relevant constitution sections
- New features MUST be validated against the date-first.
- Regular reviews to ensure continued compliance with server respect and simplicity requirements
- Documentation (README.md, CLAUDE.md) MUST remain synchronized with constitutional requirements

**Version**: 1.0.0 | **Ratified**: 2025-12-19 | **Last Amended**: 2025-12-19