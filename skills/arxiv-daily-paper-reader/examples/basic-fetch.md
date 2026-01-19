# Example 1: Basic Fetch - Get Yesterday's Papers

## User Request

```
获取昨天cs.AI领域的最新论文
```

## AI Action

```bash
python skill.py fetch --cats cs.AI --max-papers 10
```

## AI Response

已获取 cs.AI 领域的最新论文：

**生成时间**: 2025-01-19
**论文数量**: 10 篇

### cs.AI 论文列表

1. **Attention Is All You Need**
   *作者*: Vaswani et al.
   *发布*: 2025-01-18
   *摘要*: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...
   [查看论文](https://arxiv.org/abs/1706.03762) | [PDF](https://arxiv.org/pdf/1706.03762.pdf)

2. **BERT: Pre-training of Deep Bidirectional Transformers**
   *作者*: Devlin et al.
   *发布*: 2025-01-18
   *摘要*: We introduce a new language representation model called BERT...
   [查看论文](https://arxiv.org/abs/1810.04805) | [PDF](https://arxiv.org/pdf/1810.04805.pdf)

[... 8 more papers]

**报告已保存**: `arxiv_daily_report_2025-01-19.md`

---

## Alternative: Use Default Categories

```
获取昨天的所有论文（默认分类）
```

```bash
python skill.py fetch
```

这将获取 cs.OS, cs.PL, cs.SE, cs.AI 四个分类的论文。
