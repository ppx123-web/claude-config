# Todo 与其他工具集成

## Obsidian Tasks 插件（可选）

如果安装了 [Obsidian Tasks 插件](https://github.com/obsidian-tasks-group/obsidian-tasks)，可以使用更高级的语法：

### 优先级标记

```markdown
- [ ] 高优先级任务 ⏫
- [ ] 中优先级任务 🔼
- [ ] 低优先级任务 🔽
```

### 截止日期

```markdown
- [ ] 有截止日期的任务 📅 2026-01-20
- [ ] 无截止日期的任务 ❌ 📅
```

### 标签

```markdown
- [ ] 带标签的任务 #project/important
- [ ] 多个标签 #work #urgent
```

### 重复任务

```markdown
- [ ] 每天重复的任务 🔁 每天
- [ ] 每周重复的任务 🔁 每周
```

**注意**: 这些高级功能需要安装 Tasks 插件，但不影响基础功能使用。

## Dataview 插件（可选）

也可以使用 Dataview 插件查询任务：

### 基础查询

```markdown
```dataview
TASK
where file = "todo.md"
where !completed
```
```

### 带排序的查询

```markdown
```dataview
TASK
where file = "todo.md"
where !completed
sort importance desc
```
```

### 按优先级分组

```markdown
```dataview
TASK
where file = "todo.md"
where !completed
group by importance
```
```

## 查询代码块

如果使用 Tasks 插件，可以用代码块查询：

```markdown
\```tasks
not done
path includes {{todo.md}}
sort by urgency
\```
```

---

**重要**: 此 Skill 使用标准 Markdown 格式，无需额外插件即可工作。可选的 Tasks 和 Dataview 插件提供更强大的查询和过滤功能。
