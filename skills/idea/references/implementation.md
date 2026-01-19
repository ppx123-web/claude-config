# Idea Technical Implementation

## MCP Tools Used

The idea skill uses Obsidian MCP tools for all file operations.

### 1. obsidian_append_content

**Purpose**: Create new files or append content to existing files.

**Usage**:
```python
obsidian_append_content(
    filepath="idea/YYYY-MM-DD-title.md",
    content="# Full note content here..."
)
```

**Parameters**:
- `filepath` (str): Relative path from vault root
- `content` (str): Markdown content to append

**Behavior**:
- Creates file if it doesn't exist
- Appends to existing file if it exists
- Automatically creates parent directories

### 2. obsidian_get_file_contents

**Purpose**: Read existing file contents.

**Usage**:
```python
content = obsidian_get_file_contents(
    filepath="idea/Ideas-Index.md"
)
```

**Parameters**:
- `filepath` (str): Relative path from vault root

**Returns**: Full file content as string

**Use Cases**:
- Check if idea already exists
- Read current index before updating
- Parse existing tags or metadata

### 3. obsidian_delete_file

**Purpose**: Delete files from vault (rarely used).

**Usage**:
```python
obsidian_delete_file(
    filepath="idea/old-draft.md",
    confirm=True
)
```

**Parameters**:
- `filepath` (str): Relative path from vault root
- `confirm` (bool): Must be True to delete

**Use Cases**:
- Remove duplicate ideas
- Clean up incorrectly created files

### 4. obsidian_list_files_in_vault

**Purpose**: List all files in vault or specific directory.

**Usage**:
```python
files = obsidian_list_files_in_vault()
```

**Returns**: List of file paths

**Use Cases**:
- Find all existing ideas
- Check for duplicate titles
- Generate statistics

## File Structure

### Directory Layout

```
Obsidian Vault/
└── idea/
    ├── Ideas-Index.md           # Master index of all ideas
    ├── 2026-01-13-LLM-Error.md  # Individual idea notes
    ├── 2026-01-15-Cache.md
    └── 2026-01-20-API-Design.md
```

### Index File Structure

```markdown
# Ideas Index

## 2026-01

### 2026-01-20 - [[idea/2026-01-20-API-Design]]
**主题**: API design consistency
**核心问题**: How to maintain API consistency across services?
**标签**: #api #design

### 2026-01-15 - [[idea/2026-01-15-Cache-Strategy]]
**主题**: Cache invalidation strategy
**核心问题**: When to invalidate cache after data update?
**标签**: #cache #performance

[... more entries ...]
```

## Workflow Implementation

### Creating a New Idea

```python
# Step 1: Generate filename
date = datetime.now().strftime("%Y-%m-%d")
slug = "llm-error-context"  # Extracted from user input
filename = f"idea/{date}-{slug}.md"

# Step 2: Format content
content = format_idea_template(
    title="LLM Error Context",
    problem="LLM errors lack context",
    analysis=[...],
    tags=["#idea", "#llm", "#debugging"]
)

# Step 3: Create file
obsidian_append_content(filepath=filename, content=content)

# Step 4: Update index
index_entry = format_index_entry(filename, problem, tags)
append_to_index("idea/Ideas-Index.md", index_entry)
```

### Updating Index

```python
def append_to_index(index_path, entry):
    """Append new entry to index file"""
    # Read existing index
    current_index = obsidian_get_file_contents(index_path)

    # Find or create month section
    month_header = f"## {date.strftime('%Y-%m')}"
    if month_header not in current_index:
        # Add month section
        new_section = f"\n{month_header}\n\n{entry}\n"
        obsidian_append_content(filepath=index_path, content=new_section)
    else:
        # Append to existing month
        obsidian_append_content(filepath=index_path, content=entry)
```

## Content Generation

### Template Formatting

```python
def format_idea_template(title, problem, analysis, tags):
    """Generate idea note from template"""
    return f"""# idea: {title}

## 核心问题

**{problem['statement']}**

{problem['description']}

---

## 问题分析

### 现状
{chr(10).join(f"- {point}" for point in analysis['current'])}

### 疑问
{chr(10).join(f"- {q}" for q in analysis['questions'])}

---

## 延伸思考

{chr(10).join(f"{i+1}. {thought}" for i, thought in enumerate(analysis['thoughts']))}

---

*创建时间: {datetime.now().strftime('%Y-%m-%d')}*
*标签: {' '.join(tags)}*
"""
```

### Slug Generation

```python
import re

def generate_slug(title):
    """Convert title to URL-friendly slug"""
    # Remove special characters
    slug = re.sub(r'[^\w\s-]', '', title)
    # Convert to lowercase and hyphenate
    slug = slug.lower().strip()
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:50]  # Limit length
```

## Tag Management

### Auto-Tagging Logic

```python
def auto_tag_content(problem_text, analysis):
    """Generate relevant tags based on content"""
    tags = ['#idea']

    # Keyword to tag mapping
    tag_keywords = {
        '#llm': ['llm', 'gpt', 'transformer', 'language model'],
        '#performance': ['performance', 'optimization', 'slow', 'latency'],
        '#architecture': ['architecture', 'design', 'structure', 'system'],
        '#debugging': ['debug', 'error', 'bug', 'issue'],
        '#api': ['api', 'endpoint', 'rest', 'graphql'],
    }

    text = f"{problem_text} {' '.join(analysis)}".lower()

    for tag, keywords in tag_keywords.items():
        if any(keyword in text for keyword in keywords):
            tags.append(tag)

    return list(set(tags))  # Remove duplicates
```

## Error Handling

### File Creation Errors

```python
try:
    obsidian_append_content(filepath=filename, content=content)
except Exception as e:
    logger.error(f"Failed to create idea note: {e}")
    return f"创建失败: {str(e)}"
```

### Index Update Errors

```python
try:
    append_to_index("idea/Ideas-Index.md", index_entry)
except Exception as e:
    logger.warning(f"Failed to update index: {e}")
    # Continue anyway - note was created successfully
```

## Best Practices

### Performance

- Batch file operations when possible
- Cache index content to avoid repeated reads
- Use incremental updates for large indices

### Data Integrity

- Always validate filenames before creating
- Check for duplicates before adding new ideas
- Maintain consistent formatting across all notes

### User Experience

- Provide clear feedback on success/failure
- Show created file path
- Offer to open in Obsidian if available
