---
name: arxiv-daily-paper-reader
description: Comprehensive arXiv paper search and retrieval tool with keyword search, category filtering, date range filtering, and daily paper fetching capabilities for academic research tracking without keywords
dependencies: ["feedparser>=6.0.10"]
---

# arXiv Daily Paper Reader Skill

## 概述
这是一个功能强大的arXiv论文搜索和获取工具，支持**关键字搜索**、**分类过滤**、**日期范围过滤**以及**每日论文获取**。既可以获取昨天发布的最新论文，也可以搜索arXiv数据库中的任何历史论文。非常适合研究人员、学者和学生进行学术研究和论文发现。

## 核心功能
- 🔍 **强大搜索功能**: 支持关键字、短语、高级arXiv语法的全文搜索
- 📂 **分类过滤**: 按85+个arXiv分类精确筛选（cs.AI、cs.LG、cs.CV等）
- 📅 **日期范围过滤**: 支持相对日期（最近30天）和绝对日期范围
- 📊 **每日论文获取**: 自动获取昨天发布的arXiv论文（无数量限制）
- 🎯 **智能建议**: 根据搜索结果提供优化建议和冲突检测
- 📝 **多种输出格式**: Markdown报告、JSON数据、控制台预览
- 🔗 **完整链接**: 提供论文原文和PDF的直接链接
- ⚡ **智能限速**: 遵守arXiv API限制，自动重试和错误处理

## 何时使用
当您需要以下情况时使用此Skill：

### 搜索场景

- **文献搜索**: 按关键字搜索特定研究主题的相关论文
- **精准检索**: 使用高级语法在标题、摘要中精确查找
- **领域筛选**: 在特定学科分类中搜索论文
- **时间定位**: 搜索特定时间范围内的研究进展
- **趋势分析**: 获取某个领域在特定时期的发展动态

### 研究场景
- **文献调研**: 快速了解特定领域最新研究进展
- **论文追踪**: 定期获取某个领域的最新论文
- **学术报告**: 为学术会议或研究组生成最新论文综述
- **研究灵感**: 通过浏览最新论文寻找研究灵感

### 具体任务示例

- "搜索机器学习相关的最新论文"
- "查找计算机视觉领域关于GAN的论文"
- "获取2023年AI领域的重要研究"
- "搜索注意力机制在transformer中的应用"
- "给我获取cs.AI领域的最新论文报告"
- "生成cs.PL和cs.SE的最新论文摘要"
- "为我的研究组准备本周的论文报告"

## 支持的arXiv分类

### 默认分类
- **cs.OS**: 操作系统 (Operating Systems)
- **cs.PL**: 编程语言 (Programming Languages)
- **cs.SE**: 软件工程 (Software Engineering)
- **cs.AI**: 人工智能 (Artificial Intelligence)

### 其他可用分类
- cs.LG: 机器学习 (Machine Learning)
- cs.CV: 计算机视觉 (Computer Vision)
- cs.CL: 计算语言学 (Computation and Language)
- cs.DB: 数据库 (Databases)
- cs.DC: 分布式、并行和集群计算
- 以及更多...

## 使用方法

### 基本使用
```
请使用arXiv Daily Reader技能获取最新的cs.AI论文并生成报告
```

### 自定义参数
```
使用arXiv Daily Reader获取以下分类的论文：
- 分类: cs.AI, cs.LG, cs.CV
- 每个分类论文数: 5
- 输出格式: markdown报告 + JSON数据
```

### 生成报告示例
```
我需要一个关于机器学习和人工智能最新进展的论文报告，请使用arXiv Daily Reader技能
```

## 命令行使用

### 直接命令行调用

你也可以直接通过命令行调用skill.py：

```bash
# 基本用法 - 获取昨天的论文（默认分类）
python skill.py fetch

# 指定分类获取论文
python skill.py fetch --cats cs.AI cs.LG cs.CV --max-papers 20

# 搜索论文（简化版 - 仅按分类搜索）
python skill.py search --categories cs.SE --days 7 --max-results 15 --output-format markdown

# 更多示例
python skill.py search --categories cs.AI cs.LG --days 30 --max-results 20
python skill.py search --cats cs.CV --days 14 --max-results 10 --output-format json
```

### 获取帮助信息

使用 `-h` 或 `--help` 参数获取完整的帮助信息：

```bash
# 获取主命令帮助
python skill.py -h
python skill.py --help

# 获取 fetch 子命令帮助
python skill.py fetch -h
python skill.py fetch --help

# 获取 search 子命令帮助
python skill.py search -h
python skill.py search --help
```

### 帮助输出示例

#### 主命令帮助
```
usage: skill.py [-h] {fetch,search} ...

arXiv Paper Search and Daily Fetching

positional arguments:
  {fetch,search}         Available commands
    fetch                Fetch yesterday papers
    search               Search arXiv papers

options:
  -h, --help            show this help message and exit
```

#### fetch 命令帮助
```
usage: skill.py fetch [-h] [--cats CATEGORIES [CATEGORIES ...]] [--max-papers MAX_PAPERS] [--output-format {markdown,json,both}]

options:
  -h, --help            show this help message and exit
  --cats CATEGORIES [CATEGORIES ...]
                        arXiv categories to fetch
  --max-papers MAX_PAPERS
                        Maximum papers per category
  --output-format {markdown,json,both}
                        Output format
```

#### search 命令帮助
```
usage: skill.py search [-h] --cats CATEGORIES [CATEGORIES ...] [--days DAYS] [--max-results MAX_RESULTS]
                       [--output-format {markdown,json,both,preview}]

options:
  -h, --help            show this help message and exit
  --cats CATEGORIES [CATEGORIES ...], --categories CATEGORIES [CATEGORIES ...]
                        arXiv categories to search (required)
  --days DAYS, -d DAYS  Search papers from last N days (default: 30)
  --max-results MAX_RESULTS
                        Maximum results to return (default: 15)
  --output-format {markdown,json,both,preview}
                        Output format (default: markdown)
```

### 参数说明

#### fetch 命令参数
- `--cats`, `--categories`: arXiv分类列表 (默认: cs.OS, cs.PL, cs.SE, cs.AI)
- `--max-papers`: 每个分类最大论文数 (默认: 50)
- `--output-format`: 输出格式 (markdown|json|both, 默认: markdown)

#### search 命令参数
- `--cats`, `--categories`: arXiv分类列表 (**必需参数**)
- `--days`, `-d`: 最近N天的论文 (默认: 30)
- `--max-results`: 最大结果数 (默认: 15)
- `--output-format`: 输出格式 (markdown|json|both|preview, 默认: markdown)

## 搜索功能使用示例

### 分类搜索
```
获取cs.SE分类最近7天的论文
搜索cs.AI分类最新15篇论文
查找cs.CV和cs.LG分类最近30天的论文研究
```

### 组合搜索示例
```
# 获取多个分类的最新论文
python skill.py search --categories cs.AI cs.LG cs.CV --days 7 --max-results 20

# 获取较长时间范围的论文
python skill.py search --categories cs.SE --days 90 --max-results 50

# 生成JSON格式报告
python skill.py search --categories cs.AI --days 30 --output-format json
```

## 输出格式

### Markdown报告结构
```markdown
# arXiv Daily Paper Report
Generated on: 2025-12-18
Categories: cs.OS, cs.PL, cs.SE, cs.AI
Total Papers: 32

## Summary by Category

### cs.AI (8 papers)
**1. 论文标题**
*Authors:* 作者列表
*Published:* 发布日期
*Categories:* 分类标签
**Summary:** 论文摘要
[Read Paper](链接) | [PDF](PDF链接)
```

### JSON数据结构
```json
{
  "id": "论文ID",
  "title": "论文标题",
  "authors": ["作者列表"],
  "summary": "论文摘要",
  "published": "发布时间",
  "categories": ["分类标签"],
  "link": "论文链接",
  "pdf_link": "PDF链接"
}
```

## 实现细节

### 技术栈
- **Python**: 主要编程语言 (3.12+)
- **feedparser**: RSS/Atom feed解析 (>=6.0.10)
- **urllib**: HTTP请求处理 (内置库)
- **xml.etree.ElementTree**: XML解析 (内置库)
- **argparse**: 命令行参数解析 (内置库)
- **json**: JSON数据处理 (内置库)
- **dataclasses**: 数据结构定义 (内置库)
- **typing**: 类型注解支持 (内置库)
- **uv**: 包管理和虚拟环境

### 核心算法

#### 每日论文获取算法

1. **时间计算**: 自动计算昨天的时间范围（UTC）
2. **API查询**: 通过arXiv API按分类和时间范围获取最新论文
3. **摘要提取**: 提取论文摘要的前两句话作为简洁摘要
4. **数据组织**: 按类别和时间组织论文数据
5. **报告生成**: 生成结构化的markdown报告

#### 搜索功能算法

1. **查询构建**: 支持关键字搜索和高级arXiv查询语法
2. **过滤器应用**: 应用分类、日期范围、结果数量等过滤器
3. **API请求**: 使用arXiv Query API执行搜索并处理分页
4. **结果排序**: 按相关性或提交日期排序搜索结果
5. **智能建议**: 提供搜索优化建议和冲突检测
6. **结果格式化**: 支持markdown报告、JSON数据和控制台预览

### 性能优化
- 请求间隔控制，避免对arXiv服务器造成压力
- 分批处理，提高大批量数据处理效率
- 缓存机制，避免重复获取相同数据

## 配置选项

### 可配置参数
- **max_papers_per_category**: 每个分类获取的最大论文数 (默认: 10)
- **categories**: 要获取的arXiv分类列表
- **output_format**: 输出格式 (markdown, json, both)
- **summary_length**: 摘要长度 (句子数，默认: 2)

### 自定义示例
```python
# 自定义配置示例
config = {
    "categories": ["cs.AI", "cs.LG", "cs.RO"],
    "max_papers_per_category": 15,
    "output_format": "both",
    "summary_length": 3
}
```

## 最佳实践

### 使用建议
1. **定期使用**: 建议每周或每两周使用一次以跟踪最新进展
2. **分类选择**: 根据研究兴趣选择合适的分类组合
3. **批量处理**: 可以一次性获取多个相关分类的论文
4. **数据管理**: 定期清理旧的报告文件，管理存储空间

### 研究工作流集成
1. **文献管理**: 将生成的报告集成到文献管理系统
2. **论文筛选**: 使用摘要快速筛选感兴趣的论文
3. **研究计划**: 基于最新论文动态调整研究计划
4. **学术交流**: 使用生成的报告与同事分享最新进展

## 故障排除

### 常见问题
1. **网络连接**: 确保网络连接正常，可以访问arXiv
2. **API限制**: 避免过于频繁的请求，遵守arXiv的使用条款
3. **格式解析**: 某些论文可能有特殊格式，系统会自动处理

### 错误处理
- 网络错误时自动重试
- 解析错误时跳过有问题的论文
- 提供详细的错误日志

## 扩展功能

### 未来可能的增强
- **语义搜索**: 基于论文内容进行语义相似度搜索
- **作者追踪**: 追踪特定作者的最新论文
- **引用分析**: 分析论文的引用关系
- **趋势分析**: 分析研究趋势和热点
- **个性化推荐**: 基于用户兴趣推荐相关论文

### 集成可能性
- 与文献管理软件集成 (Zotero, Mendeley)
- 与学术社交网络集成 (ResearchGate, Google Scholar)
- 与AI助手集成进行深度分析

## 伦理和使用准则

### 学术伦理
- 遵守arXiv的使用条款和API限制
- 尊重论文作者的知识产权
- 正确引用和标注来源

### 数据隐私
- 不会收集或存储用户个人信息
- 所有数据仅用于论文检索和分析
- 遵守数据保护相关法规

---

**注意**: 此Skill仅用于学术研究目的，请确保遵守相关的学术伦理和使用条款。