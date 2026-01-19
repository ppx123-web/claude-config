# Example 2: Category Search - Search Specific Categories

## User Request

```
搜索cs.SE（软件工程）和cs.PL（编程语言）最近7天的论文
```

## AI Action

```bash
python skill.py search --categories cs.SE cs.PL --days 7 --max-results 20
```

## AI Response

已搜索 cs.SE 和 cs.PL 最近7天的论文：

### 搜索结果统计

- **时间范围**: 2025-01-12 至 2025-01-19
- **分类**: cs.SE, cs.PL
- **找到论文**: 18 篇

### cs.SE (12 papers)

1. **Automated Testing of Large Language Models**
   *作者*: Smith et al.
   *发布*: 2025-01-17
   *摘要*: Presents a comprehensive framework for testing LLMs...
   **相关性**: ⭐⭐⭐⭐⭐

2. **Static Analysis for Microservices**
   *作者*: Johnson et al.
   *发布*: 2025-01-15
   *摘要*: Introduces static analysis techniques for microservice architectures...
   **相关性**: ⭐⭐⭐⭐

[... 10 more papers]

### cs.PL (6 papers)

1. **Type Systems for Modern JavaScript**
   *作者*: Lee et al.
   *发布*: 2025-01-16
   *摘要*: Proposes an enhanced type system for JavaScript...
   **相关性**: ⭐⭐⭐⭐⭐

2. **Compiler Optimization Techniques for Rust**
   *作者*: Wang et al.
   *发布*: 2025-01-14
   *摘要*: Investigates optimization techniques for Rust compilers...
   **相关性**: ⭐⭐⭐⭐

[... 4 more papers]

**报告已保存**: `arxiv_search_report_2025-01-19.md`

---

## Tips

- 可以同时搜索多个分类，用空格分隔
- 使用 `--days` 参数指定时间范围
- 使用 `--max-results` 限制返回数量
