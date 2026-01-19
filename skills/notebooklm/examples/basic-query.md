# Example 1: Basic Query - Ask Documentation Question

## User Request

```
我有一个NotebookLM笔记本，里面有n8n的文档，帮我查一下n8n怎么配置webhook
```

## AI Action

```bash
# Step 1: Check authentication
python scripts/run.py auth_manager.py status

# Step 2: List notebooks to find n8n docs
python scripts/run.py notebook_manager.py list

# Step 3: Activate n8n notebook (or query directly)
python scripts/run.py ask_question.py \
  --question "How do I configure webhooks in n8n? Show me the setup steps and best practices." \
  --notebook-id n8n-docs-id
```

## AI Response

根据n8n文档，webhook配置步骤如下：

### Webhook Setup in n8n

**1. Create Webhook Node**
- Add "Webhook" node to your workflow
- Choose HTTP method (GET/POST/PUT/PATCH)
- Set webhook path (e.g., `/my-webhook`)

**2. Configure Settings**
- Response Mode: Select "last node", "first node", or "custom"
- Response Headers: Optional custom headers
- Authentication: None, Basic Auth, or Header Auth

**3. Get Webhook URL**
- Click "Listen for Test Event"
- Copy the generated URL (format: `https://your-instance.webhook.n8n.cloud/...`)

**4. Test Webhook**
- Send test request to the URL
- Verify data appears in n8n
- Activate workflow

**Best Practices**:
- Use descriptive webhook paths
- Enable authentication for production
- Add error handling nodes after webhook
- Consider rate limiting

---

需要更详细的某个步骤说明吗？
