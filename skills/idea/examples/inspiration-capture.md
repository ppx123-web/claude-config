# Example 1: Inspiration Capture - Sudden Thought

## User Input

```
突然想到，为什么错误信息不能包含更多上下文？
```

## AI Response

明白了，这是一个关于错误处理改进的想法。让我记录下来：

**创建文件**: `idea/2026-01-13-LLM-Error-Messages.md`

---

```markdown
# idea: LLM Error Message Context

## 核心问题

**LLM API的错误信息缺乏足够的上下文，难以快速调试和定位问题。**

当前大多数LLM API只返回简单的错误代码（如"invalid_request"），没有说明是哪个prompt、哪个参数导致的错误。

---

## 问题分析

### 现状
- 错误信息只有错误代码，无详细说明
- 开发者无法知道具体哪个请求出错
- 缺少请求ID等追踪信息
- 没有推荐解决方案

### 为什么是问题
- 增加调试时间和成本
- 无法快速定位问题prompt
- 难以追踪和复现错误
- 降低开发效率

---

## 延伸思考

1. HTTP API是否有标准可以参考？
2. 上下文信息是否会暴露敏感数据？
3. 如何平衡详细程度和安全性？
4. 是否需要可配置的错误详细级别？

---

*创建时间: 2026-01-13*
*标签: #idea #llm #api #debugging #error-handling*
```

---

**已更新索引**: `idea/Ideas-Index.md`

---

## Verification

这个想法值得记录吗？

✅ **问题清晰**: 错误信息不足是真实问题
✅ **有影响**: 影响开发效率和调试体验
✅ **可探索**: 有多个维度值得深入思考

已成功记录！你可以在 Obsidian 中查看完整内容。
