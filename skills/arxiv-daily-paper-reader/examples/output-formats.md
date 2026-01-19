# Example 3: Output Formats - Markdown, JSON, Both

## User Request (Markdown)

```
生成cs.CV（计算机视觉）的论文报告，使用Markdown格式
```

## AI Action

```bash
python skill.py fetch --cats cs.CV --output-format markdown
```

## Output: arxiv_daily_report_2025-01-19.md

```markdown
# arXiv Daily Paper Report
Generated on: 2025-01-19
Categories: cs.CV
Total Papers: 15

## cs.CV (15 papers)

### 1. Improved Training of Wasserstein GANs
**Authors:** Gulrajani et al.
**Published:** 2025-01-18
**Categories:** cs.CV, cs.LG

**Summary:**
We propose a new method for training Wasserstein GANs that addresses the training instability problem. Our method uses a gradient penalty that constrains the gradient norm of the critic to be close to 1...

[Read Paper](https://arxiv.org/abs/1704.00028) | [PDF](https://arxiv.org/pdf/1704.00028.pdf)
```

---

## User Request (JSON)

```
获取cs.LG的论文，用JSON格式输出
```

## AI Action

```bash
python skill.py fetch --cats cs.LG --output-format json
```

## Output: arxiv_papers_2025-01-19.json

```json
{
  "metadata": {
    "generated_date": "2025-01-19",
    "categories": ["cs.LG"],
    "total_papers": 20,
    "papers_by_category": {
      "cs.LG": 20
    }
  },
  "papers": [
    {
      "id": "1706.03762",
      "title": "Attention Is All You Need",
      "authors": ["Vaswani, Ashish", "Shazeer, Noam", "Parmar, Niki"],
      "summary": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
      "published": "2025-01-18",
      "categories": ["cs.LG", "cs.AI"],
      "link": "https://arxiv.org/abs/1706.03762",
      "pdf_link": "https://arxiv.org/pdf/1706.03762.pdf"
    }
  ]
}
```

---

## User Request (Both)

```
获取cs.AI论文，同时生成Markdown和JSON格式
```

## AI Action

```bash
python skill.py fetch --cats cs.AI --output-format both
```

## Output: Both Files Generated

✅ **Markdown**: `arxiv_daily_report_2025-01-19.md`
✅ **JSON**: `arxiv_papers_2025-01-19.json`

两个文件都已生成，可以使用不同的工具查看：
- Markdown: 适合人类阅读
- JSON: 适合程序处理、数据分析
