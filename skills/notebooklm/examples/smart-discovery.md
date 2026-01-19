# Example 2: Smart Discovery - Add New Notebook

## User Request

```
我想添加这个NotebookLM笔记本：https://notebooklm.google.com/notebook/abc123def456
```

## AI Action (Smart Discovery Approach)

```bash
# Step 1: Query the notebook to discover its content
python scripts/run.py ask_question.py \
  --question "What is the content of this notebook? What topics are covered? Provide a complete overview briefly and concisely" \
  --notebook-url "https://notebooklm.google.com/notebook/abc123def456"
```

## NotebookLM Response

This notebook contains comprehensive documentation about **React Query** (TanStack Query), a powerful data synchronization library for React. It covers:

**Main Topics**:
- Data fetching and caching
- Mutation and invalidation
- Pagination and infinite queries
- Error handling and retries
- Performance optimization
- Best practices and patterns

**Target Audience**: React developers building data-driven applications

## AI Action (Now Add with Discovered Info)

```bash
# Step 2: Add notebook with discovered metadata
python scripts/run.py notebook_manager.py add \
  --url "https://notebooklm.google.com/notebook/abc123def456" \
  --name "React Query Documentation" \
  --description "Complete React Query (TanStack Query) documentation: data fetching, caching, mutations, pagination, error handling, and performance optimization patterns" \
  --topics "react,query,data-fetching,caching,performance"
```

## AI Response

✅ **已添加笔记本**

**名称**: React Query Documentation
**ID**: abc123def456
**主题**: react, query, data-fetching, caching, performance

**描述**: Complete React Query (TanStack Query) documentation covering data fetching, caching, mutations, pagination, error handling, and performance optimization patterns.

现在可以通过ID或名称查询这个笔记本了。需要我帮你查询React Query的某个具体功能吗？
