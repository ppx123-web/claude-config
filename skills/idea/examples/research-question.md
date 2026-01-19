# Example 2: Research Question - Academic Investigation

## User Input

```
记录一个研究想法：LLM在长链条推理时错误率太高
```

## AI Response

很好的研究方向！让我帮你记录：

**创建文件**: `idea/2026-01-18-LLM-Long-Reasoning.md`

---

```markdown
# idea: LLM Long-Chain Reasoning

## 核心问题

**当前LLM在长链条推理（10+ steps）时，错误率呈指数级增长，如何保证推理正确性？**

Chain-of-Thought等方法在短推理（3-5步）效果很好，但随着推理链增长，错误累积严重。

---

## 问题分析

### 现状
- 主流方法: Chain-of-Thought, Tree-of-Thought, Graph-of-Thought
- 已知结论: 短推理效果好，长推理容易偏离
- 主要局限: 每一步都可能出错，且错误会累积

### 研究空白
- 如何在推理过程中自我纠错？
- 是否可以分解为多个独立子问题？
- 能否通过验证机制保证正确性？
- 是否需要新的架构而不是prompt engineering？

---

## 延伸思考

1. 人类是如何处理长链条推理的？（会自我验证、回溯）
2. 能否借鉴形式化验证方法？
3. 需要什么样的benchmark来评估长推理能力？
4. 是否可以引入"推理checkpoint"机制？
5. Tree-of-Thought是否能部分解决这个问题？

---

*创建时间: 2026-01-18*
*标签: #idea #research #llm #reasoning #cot*
```

---

**已更新索引**: `idea/Ideas-Index.md`

---

## Follow-up

这是一个很有价值的研究方向。相关的工作可以关注：

- **Self-Consistency** (Wang et al.): 通过多次采样验证
- **Tree-of-Thought** (Yao et al.): 树状搜索探索多条路径
- **Reflexion** (Shinn et al.): 自我反思和纠错

需要我帮你搜索这些论文吗？
