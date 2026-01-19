# Example 3: Follow-Up Questions - Deep Dive

## User Request

```
React Query中怎么处理缓存失效（cache invalidation）？
```

## AI Action

```bash
# First question
python scripts/run.py ask_question.py \
  --question "How does React Query handle cache invalidation? What are the different strategies?" \
  --notebook-id react-query-docs
```

## First Response (NotebookLM)

**Cache Invalidation Strategies in React Query**:

1. **Automatic Invalidation**
   - Time-based: `staleTime` and `cacheTime`
   - Window refocus refetch
   - Interval refetch with `refetchInterval`

2. **Manual Invalidation**
   ```javascript
   // Invalidate specific query
   queryClient.invalidateQueries('todos')

   // Invalidate with filters
   queryClient.invalidateQueries({
     predicate: (query) => query.key.includes('todo')
   })
   ```

3. **Mutation-based Invalidation**
   ```javascript
   useMutation({
     mutationFn: updateTodo,
     onSuccess: () => {
       queryClient.invalidateQueries(['todos'])
     }
   })
   ```

---

**EXTREMELY IMPORTANT: Is that ALL you need to know?**

## AI Analysis

The answer covers basic strategies, but user might need:
- ✅ Code examples for each strategy
- ❌ Real-world usage patterns
- ❌ Common pitfalls
- ❌ Performance implications

## AI Action (Follow-Up)

```bash
# Follow-up question for deeper understanding
python scripts/run.py ask_question.py \
  --question "Can you show real-world examples of cache invalidation patterns? What are common mistakes developers make with invalidation?" \
  --session-id <previous-session-id>
```

## Second Response (NotebookLM)

**Real-World Invalidation Patterns**:

1. **Optimistic Updates**
   ```javascript
   // Update cache immediately, rollback on error
   useMutation({
     mutationFn: updateTodo,
     onMutate: async (newTodo) => {
       await queryClient.cancelQueries(['todos'])
       const previous = queryClient.getQueryData(['todos'])
       queryClient.setQueryData(['todos'], old => [...old, newTodo])
       return { previous }
     },
     onError: (err, newTodo, context) => {
       queryClient.setQueryData(['todos'], context.previous)
     }
   })
   ```

2. **Granular Invalidation**
   ```javascript
   // Only invalidate affected items
   queryClient.invalidateQueries({
     queryKey: ['todos', { status: 'completed' }]
   })
   ```

**Common Mistakes**:
- ❌ Over-invalidation: Invalidating entire cache when only one item changed
- ❌ Missing invalidation: Forgetting to invalidate after mutations
- ❌ Race conditions: Not canceling pending queries before mutations

---

**EXTREMELY IMPORTANT: Is that ALL you need to know?**

## AI Final Synthesis

Now I have complete information. Let me synthesize for the user:

## AI Response to User

根据React Query文档，缓存失效有以下几种策略：

### 1. 自动失效
- **基于时间**: `staleTime`（多久后过期）和 `cacheTime`（多久后删除）
- **窗口聚焦**: 重新获得焦点时自动重新获取
- **定时刷新**: 使用 `refetchInterval` 定期更新

### 2. 手动失效
```javascript
// 失效特定查询
queryClient.invalidateQueries('todos')

// 精确失效
queryClient.invalidateQueries({
  queryKey: ['todos', { status: 'completed' }]
})
```

### 3. 变更后失效
```javascript
useMutation({
  mutationFn: updateTodo,
  onSuccess: () => {
    queryClient.invalidateQueries(['todos'])
  }
})
```

### 实际最佳实践

**乐观更新（推荐）**：
```javascript
useMutation({
  mutationFn: updateTodo,
  onMutate: async (newTodo) => {
    // 取消待处理查询
    await queryClient.cancelQueries(['todos'])

    // 保存当前数据
    const previous = queryClient.getQueryData(['todos'])

    // 立即更新缓存
    queryClient.setQueryData(['todos'], old => [...old, newTodo])

    return { previous }
  },
  onError: (err, newTodo, context) => {
    // 出错时回滚
    queryClient.setQueryData(['todos'], context.previous)
  },
  onSettled: () => {
    // 无论成功失败都重新获取
    queryClient.invalidateQueries(['todos'])
  }
})
```

### 常见错误

❌ **过度失效**: 整个缓存失效而不是精确失效
❌ **忘记失效**: mutation后不更新缓存
❌ **竞态条件**: mutation前不取消pending查询

需要我详细解释某个策略的使用场景吗？
