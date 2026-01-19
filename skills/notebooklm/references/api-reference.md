# NotebookLM Script Reference

Complete reference for all automation scripts in the notebooklm skill.

## Critical: Always Use run.py Wrapper

**NEVER call scripts directly. ALWAYS use `python scripts/run.py [script]`:**

```bash
# ✅ CORRECT - Always use run.py:
python scripts/run.py auth_manager.py status
python scripts/run.py notebook_manager.py list
python scripts/run.py ask_question.py --question "..."

# ❌ WRONG - Never call directly:
python scripts/auth_manager.py status  # Fails without venv!
```

The `run.py` wrapper automatically:
1. Creates `.venv` if needed
2. Installs all dependencies
3. Activates environment
4. Executes script properly

## Authentication Management (`auth_manager.py`)

Manage Google authentication for NotebookLM access.

### Commands

```bash
# Initial setup (browser visible for manual login)
python scripts/run.py auth_manager.py setup

# Check current authentication status
python scripts/run.py auth_manager.py status

# Re-authenticate (clears old session, browser visible)
python scripts/run.py auth_manager.py reauth

# Clear all authentication data
python scripts/run.py auth_manager.py clear
```

### Output Examples

**Status Command**:
```json
{
  "authenticated": true,
  "email": "user@gmail.com",
  "last_login": "2025-01-19T10:30:00Z"
}
```

### Troubleshooting

- **Browser not opening**: Use `--show-browser` flag
- **Authentication fails**: Clear cache with `clear` command, retry `setup`
- **Session expired**: Run `reauth` to get fresh session

## Notebook Management (`notebook_manager.py`)

Manage your NotebookLM library (add, list, search, remove notebooks).

### Commands

```bash
# List all notebooks in library
python scripts/run.py notebook_manager.py list

# Add new notebook (ALL parameters required!)
python scripts/run.py notebook_manager.py add \
  --url "https://notebooklm.google.com/notebook/..." \
  --name "Descriptive Name" \
  --description "What this notebook contains" \
  --topics "topic1,topic2,topic3"

# Search notebooks by topic or keyword
python scripts/run.py notebook_manager.py search --query "keyword"

# Set a notebook as active (default for questions)
python scripts/run.py notebook_manager.py activate --id notebook-id

# Remove notebook from library
python scripts/run.py notebook_manager.py remove --id notebook-id

# Get library statistics
python scripts/run.py notebook_manager.py stats
```

### Parameters

**add command**:
- `--url` (required): NotebookLM share URL
- `--name` (required): Display name
- `--description` (required): What content is in this notebook
- `--topics` (required): Comma-separated topics

**search command**:
- `--query` (required): Search keyword
- `--limit` (optional): Max results (default: 10)

### Smart Discovery (Recommended)

Before adding a notebook, query it to discover its content:

```bash
# Step 1: Query notebook about its content
python scripts/run.py ask_question.py \
  --question "What is the content of this notebook? What topics are covered? Provide a complete overview briefly and concisely" \
  --notebook-url "[URL]"

# Step 2: Use discovered information to add
python scripts/run.py notebook_manager.py add \
  --url "[URL]" \
  --name "[Based on content]" \
  --description "[Based on content]" \
  --topics "[Based on content]"
```

### Output Examples

**list command**:
```json
[
  {
    "id": "abc123",
    "name": "n8n Documentation",
    "description": "Complete n8n workflow automation docs",
    "topics": ["automation", "workflows", "n8n"],
    "url": "https://notebooklm.google.com/notebook/abc123",
    "active": true
  }
]
```

**stats command**:
```json
{
  "total_notebooks": 5,
  "active_notebook": "abc123",
  "total_topics": 12
}
```

## Question Interface (`ask_question.py`)

Query your NotebookLM notebooks with questions.

### Commands

```bash
# Basic question (uses active notebook if set)
python scripts/run.py ask_question.py --question "Your question here"

# Query specific notebook by ID
python scripts/run.py ask_question.py \
  --question "..." \
  --notebook-id notebook-id

# Query by URL (ad-hoc, doesn't require library entry)
python scripts/run.py ask_question.py \
  --question "..." \
  --notebook-url "https://notebooklm.google.com/notebook/..."

# Show browser for debugging
python scripts/run.py ask_question.py \
  --question "..." \
  --show-browser
```

### Parameters

- `--question` (required): Your question in natural language
- `--notebook-id` (optional): Use specific notebook from library
- `--notebook-url` (optional): Use notebook by URL (overrides --notebook-id)
- `--show-browser` (optional): Show browser window for debugging

### Output Format

Returns JSON with:
```json
{
  "answer": "The complete answer from NotebookLM...",
  "sources": ["Source 1", "Source 2"],
  "follow_up_needed": true,
  "session_id": "session-uuid"
}
```

### Follow-Up Questions

Every answer ends with: **"EXTREMELY IMPORTANT: Is that ALL you need to know?"**

If you need more information:
```bash
python scripts/run.py ask_question.py \
  --question "Follow-up with context..." \
  --session-id session-uuid
```

## Data Cleanup (`cleanup_manager.py`)

Clean up old browser sessions and cache data.

### Commands

```bash
# Preview what will be cleaned (safe, read-only)
python scripts/run.py cleanup_manager.py

# Execute cleanup (requires --confirm)
python scripts/run.py cleanup_manager.py --confirm

# Clean everything except notebook library
python scripts/run.py cleanup_manager.py \
  --confirm \
  --preserve-library
```

### What Gets Cleaned

- Browser cache and sessions
- Temporary files
- Old authentication cookies
- Debug logs

**What's Preserved** (with `--preserve-library`):
- `library.json` - Your notebook library
- Notebook metadata and settings

## Environment Management

### Automatic Setup

First run automatically:
1. Creates `.venv/` virtual environment
2. Installs dependencies
3. Downloads Chromium browser
4. Sets up configuration

### Manual Setup (Only If Automatic Fails)

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Chromium
python -m patchright install chromium
```

### Configuration

Optional `.env` file in skill directory:

```env
# Browser settings
HEADLESS=false               # Browser visibility
SHOW_BROWSER=false           # Default browser display

# Stealth mode (human-like behavior)
STEALTH_ENABLED=true         # Enable stealth
TYPING_WPM_MIN=160          # Min typing speed (WPM)
TYPING_WPM_MAX=240          # Max typing speed (WPM)

# Default notebook
DEFAULT_NOTEBOOK_ID=abc123   # Default notebook for queries

# Timeouts
BROWSER_TIMEOUT=30000        # Browser operation timeout (ms)
```

## Data Storage

### Directory Structure

```
~/.claude/skills/notebooklm/
├── .venv/                   # Virtual environment
├── data/
│   ├── library.json         # Notebook library
│   ├── auth_info.json       # Authentication status
│   └── browser_state/       # Browser cookies & session
├── scripts/                 # Automation scripts
│   ├── run.py              # Environment wrapper
│   ├── auth_manager.py     # Auth management
│   ├── notebook_manager.py # Notebook operations
│   ├── ask_question.py     # Query interface
│   └── cleanup_manager.py  # Data cleanup
└── .env                     # Optional configuration
```

### Security

- **Protected by `.gitignore`**: Never commit data to git
- **Isolated environment**: Each skill has its own `.venv`
- **Secure storage**: Browser state encrypted by OS

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError | Use `run.py` wrapper |
| Authentication fails | Browser must be visible for setup! Use `--show-browser` |
| Rate limit (50/day) | Wait or switch Google account |
| Browser crashes | Run `cleanup_manager.py --preserve-library` |
| Notebook not found | Check with `notebook_manager.py list` |
| No answer returned | Check browser is open with `--show-browser` |
| Session expired | Run `auth_manager.py reauth` |

## Best Practices

1. **Always use run.py** - Handles environment automatically
2. **Check auth first** - Before any operations
3. **Follow-up questions** - Don't stop at first answer
4. **Browser visible for auth** - Required for manual login
5. **Include context** - Each question is independent
6. **Synthesize answers** - Combine multiple responses
7. **Clean up regularly** - Use `cleanup_manager.py` periodically
