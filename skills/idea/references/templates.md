# Idea Templates

This file contains detailed templates for different types of idea notes.

## Technical Problem Template

Use for technical issues, bugs, or implementation problems.

```markdown
# idea: [Technical Topic]

## 核心问题

**[Problem]**

当前技术/方法在[场景]下存在[问题]。

---

## 问题分析

### 现状
- 使用[技术/方法]
- 存在[局限性]
- 导致[后果]

### 为什么是问题
- [影响1]
- [影响2]

---

## 延伸思考

1. 是否有更简单的方式？
2. 这个问题在实际场景中普遍存在吗？
3. 改进的代价是什么？

---

*创建时间: YYYY-MM-DD*
*标签: #idea #technical #[领域]*
```

### Example: Technical Problem

```markdown
# idea: LLM Error Message Context

## 核心问题

**LLM API错误信息缺乏足够的上下文，难以调试和定位问题。**

---

## 问题分析

### 现状
- 当前LLM API只返回简单的错误代码
- 开发者无法知道哪个prompt导致错误
- 缺少请求ID等追踪信息

### 为什么是问题
- 增加调试时间
- 无法快速定位问题prompt
- 难以追踪和复现错误

---

## 延伸思考

1. 是否有行业标准可以参考？
2. 上下文信息是否会暴露敏感数据？
3. 如何平衡详细程度和安全？

---

*创建时间: 2026-01-13*
*标签: #idea #technical #LLM #debugging*
```

## Architecture Design Template

Use for architectural decisions, tradeoffs, and design choices.

```markdown
# idea: [Architecture Topic]

## 核心问题

**[Design Decision/Tradeoff]**

在[场景]下，如何在[A]和[B]之间做出选择？

---

## 问题分析

### 选项 A: [描述]
- 优点: [...]
- 缺点: [...]
- 适用场景: [...]

### 选项 B: [描述]
- 优点: [...]
- 缺点: [...]
- 适用场景: [...]

### 核心矛盾
- [矛盾点1]
- [矛盾点2]

---

## 延伸思考

1. 是否有第三种选择？
2. 这个选择在6个月后还重要吗？
3. 最坏情况是什么？

---

*创建时间: YYYY-MM-DD*
*标签: #idea #architecture #[领域]*
```

### Example: Architecture Tradeoff

```markdown
# idea: Microservices vs Monolith

## 核心问题

**在小型团队（<5人）场景下，应该选择微服务还是单体架构？**

---

## 问题分析

### 选项 A: 微服务
- 优点: 独立部署、技术栈灵活、扩展性好
- 缺点: 运维复杂、分布式事务、调试困难
- 适用场景: 大型团队、复杂业务

### 选项 B: 单体
- 优点: 简单、易于调试、事务简单
- 缺点: 部署耦合、技术栈固定、扩展受限
- 适用场景: 小型团队、简单业务

### 核心矛盾
- 团队规模 < 服务数量
- 运维成本 > 技术收益

---

## 延伸思考

1. 能否从单体开始，按需拆分？
2. 团队是否有足够的运维能力？
3. 业务复杂度是否真的需要微服务？

---

*创建时间: 2026-01-15*
*标签: #idea #architecture #system-design*
```

## Research Question Template

Use for academic research questions, theoretical problems, or exploratory ideas.

```markdown
# idea: [Research Topic]

## 核心问题

**[Research Question]**

当前研究在[方面]存在[gap/limitation]。

---

## 问题分析

### 现状
- 主流方法: [方法A, 方法B]
- 已知结论: [结论1, 结论2]
- 主要局限: [局限1, 局限2]

### 研究空白
- [空白点1]
- [空白点2]

---

## 延伸思考

1. 这个问题值得深入研究吗？
2. 有没有相关的现有工作？
3. 需要什么样的数据和实验？

---

*创建时间: YYYY-MM-DD*
*标签: #idea #research #[领域]*
```

### Example: Research Question

```markdown
# idea: LLM Reasoning at Scale

## 核心问题

**当前LLM在长链条推理（10+ steps）时，错误率呈指数级增长。**

---

## 问题分析

### 现状
- 主流方法: Chain-of-Thought, Tree-of-Thought
- 已知结论: 短推理效果好，长推理容易偏离
- 主要局限: 无法保证每一步都正确

### 研究空白
- 如何在推理过程中自我纠错？
- 是否可以分解为多个独立子问题？
- 能否通过验证机制保证正确性？

---

## 延伸思考

1. 人类是如何处理长链条推理的？
2. 能否借鉴形式化验证方法？
3. 需要什么样的benchmark来评估？

---

*创建时间: 2026-01-20*
*标签: #idea #research #LLM #reasoning*
```

## Template Usage Guidelines

### When to Use Each Template

1. **Technical Problem**: Implementation issues, bugs, performance problems
2. **Architecture Design**: System design, tradeoffs, technology choices
3. **Research Question**: Academic questions, theoretical gaps, open problems

### Template Customization

- Adjust sections based on specific needs
- Add/remove subsections as appropriate
- Keep focus on problems, not solutions
- Include "Linus 视角" verification when relevant

### Template Quality Checklist

- ✅ Problem statement is clear and specific
- ✅ Analysis identifies current state and limitations
- ✅ Follow-up questions encourage deeper thinking
- ✅ Tags are relevant and specific
- ❌ No solution proposals included
