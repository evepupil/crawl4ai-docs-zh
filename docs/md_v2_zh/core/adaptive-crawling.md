正在阅读我无法读取《https://scikit-learn.org/stable/》、《https://api.example.com/docs》、《https://github.com/unclecode/crawl4ai/tree/main/docs/examples/adaptive_crawling》文件的内容。其他文件已阅读并为你总结如下：
# 自适应网络爬取

## 简介

传统网络爬虫遵循预定模式，盲目爬取页面而不知何时已收集足够信息。**自适应爬取**通过将智能引入爬取过程改变了这一范式。

想象一下研究过程：当你寻找信息时，不会阅读图书馆里的每一本书。当你找到足够信息回答问题时就会停止。这正是自适应爬取在网络抓取中所做的。

## 核心概念

### 解决的问题

当为特定信息爬取网站时，面临两个挑战：
1. **爬取不足**：过早停止而错过关键信息
2. **过度爬取**：爬取无关页面浪费资源

自适应爬取通过使用三层评分系统确定何时拥有"足够"信息来解决这两个问题。

### 工作原理

AdaptiveCrawler使用三个指标衡量信息充分性：

- **覆盖率**：收集的页面覆盖查询词的程度
- **一致性**：信息在不同页面间是否连贯  
- **饱和度**：检测新页面是否未添加新信息

当这些指标表明已收集足够信息时，爬取自动停止。

## 快速开始

### 基本用法

```python
from crawl4ai import AsyncWebCrawler, AdaptiveCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        # 创建自适应爬虫(配置可选)
        adaptive = AdaptiveCrawler(crawler)
        
        # 使用查询开始爬取
        result = await adaptive.digest(
            start_url="链接1",
            query="async context managers"
        )
        
        # 查看统计信息
        adaptive.print_stats()
        
        # 获取最相关内容
        relevant_pages = adaptive.get_relevant_content(top_k=5)
        for page in relevant_pages:
            print(f"- {page['url']} (score: {page['score']:.2f})")
```

### 配置选项

```python
from crawl4ai import AdaptiveConfig

config = AdaptiveConfig(
    confidence_threshold=0.8,    # 80%置信度时停止(默认:0.7)
    max_pages=30,               # 最大爬取页数(默认:20)
    top_k_links=5,              # 每页跟踪链接数(默认:3)
    min_gain_threshold=0.05     # 继续爬取的最小预期增益(默认:0.1)
)

adaptive = AdaptiveCrawler(crawler, config)
```

## 爬取策略

自适应爬取支持两种不同的信息充分性判定策略：

### 统计策略(默认)

统计策略使用纯信息论和基于术语的分析：

- **快速高效** - 无需API调用或模型加载
- **基于术语的覆盖** - 分析查询词存在和分布
- **无外部依赖** - 离线工作
- **最佳适用**：具有特定术语的明确定义查询

```python
# 默认配置使用统计策略
config = AdaptiveConfig(
    strategy="statistical",  # 这是默认值
    confidence_threshold=0.8
)
```

### 嵌入策略

嵌入策略使用语义嵌入进行更深层次理解：

- **语义理解** - 捕获超出精确术语匹配的含义
- **查询扩展** - 自动生成查询变体
- **基于差距的选择** - 识别知识中的语义差距
- **基于验证的停止** - 使用保留查询验证覆盖范围
- **最佳适用**：复杂查询、模糊主题、概念理解

```python
# 配置嵌入策略
config = AdaptiveConfig(
    strategy="embedding",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",  # 默认
    n_query_variations=10,  # 生成10个查询变体
    embedding_min_confidence_threshold=0.1  # 完全无关时停止
)

# 使用自定义嵌入提供程序(如OpenAI)
config = AdaptiveConfig(
    strategy="embedding",
    embedding_llm_config={
        'provider': 'openai/text-embedding-3-small',
        'api_token': 'your-api-key'
    }
)
```

### 策略比较

| 特性 | 统计策略 | 嵌入策略 |
|---------|------------|-----------|
| **速度** | 非常快 | 中等(API调用) |
| **成本** | 免费 | 取决于提供商 |
| **准确性** | 精确术语效果好 | 概念理解优秀 |
| **依赖项** | 无 | 嵌入模型/API |
| **查询理解** | 字面 | 语义 |
| **最佳用例** | 技术文档、特定术语 | 研究、广泛主题 |

### 嵌入策略配置

嵌入策略通过多个参数提供精细控制：

```python
config = AdaptiveConfig(
    strategy="embedding",
    
    # 模型配置
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    embedding_llm_config=None,  # 用于基于API的嵌入
    
    # 查询扩展
    n_query_variations=10,  # 要生成的查询变体数量
    
    # 覆盖参数
    embedding_coverage_radius=0.2,  # 覆盖距离阈值
    embedding_k_exp=3.0,  # 指数衰减因子(值越高越严格)
    
    # 停止标准
    embedding_min_relative_improvement=0.1,  # 继续的最小改进
    embedding_validation_min_score=0.3,  # 最小验证分数
    embedding_min_confidence_threshold=0.1,  # 低于此值=无关
    
    # 链接选择
    embedding_overlap_threshold=0.85,  # 去重相似度
    
    # 显示置信度映射
    embedding_quality_min_confidence=0.7,  # 最小显示置信度
    embedding_quality_max_confidence=0.95  # 最大显示置信度
)
```

### 处理无关查询

嵌入策略可以检测查询是否与内容完全无关：

```python
# 这将快速停止并显示低置信度
result = await adaptive.digest(
    start_url="链接1",
    query="how to cook pasta"  # 与Python文档无关
)

# 检查查询是否无关
if result.metrics.get('is_irrelevant', False):
    print("Query is unrelated to the content!")
```

## 使用场景

### 最适合：
- **研究任务**：查找关于主题的全面信息
- **问答**：收集足够上下文回答特定查询
- **知识库构建**：为AI/ML应用创建聚焦数据集
- **竞争情报**：收集特定产品/功能的完整信息

### 不推荐用于：
- **全站归档**：需要所有页面而不管内容时
- **结构化数据提取**：针对特定已知页面模式时
- **实时监控**：需要持续更新时

## 理解输出

### 置信度分数

置信度分数(0-1)表示收集信息的充分程度：
- **0.0-0.3**：信息不足，需要更多爬取
- **0.3-0.6**：部分信息，可能回答基本查询
- **0.6-0.7**：良好覆盖，可回答大多数查询
- **0.7-1.0**：优秀覆盖，全面信息

### 统计信息显示

```python
adaptive.print_stats(detailed=False)  # 摘要表
adaptive.print_stats(detailed=True)   # 详细指标
```

摘要显示：
- 已爬取页面与达到的置信度
- 覆盖率、一致性和饱和度分数
- 爬取效率指标

## 持久化与恢复

### 保存进度

```python
config = AdaptiveConfig(
    save_state=True,
    state_path="my_crawl_state.json"
)

# 爬取将自动保存进度
result = await adaptive.digest(start_url, query)
```

### 恢复爬取

```python
# 从保存状态恢复
result = await adaptive.digest(
    start_url,
    query,
    resume_from="my_crawl_state.json"
)
```

### 导出知识库

```python
# 将收集的页面导出为JSONL
adaptive.export_knowledge_base("knowledge_base.jsonl")

# 导入到另一个会话
new_adaptive = AdaptiveCrawler(crawler)
new_adaptive.import_knowledge_base("knowledge_base.jsonl")
```

## 最佳实践

### 1. 查询制定
- 使用具体、描述性查询
- 包含预期找到的关键词
- 避免过于宽泛的查询

### 2. 阈值调优
- 通用用途从默认值(0.7)开始
- 探索性爬取降至0.5-0.6
- 详尽覆盖升至0.8+

### 3. 性能优化
- 使用适当的`max_pages`限制
- 根据站点结构调整`top_k_links`
- 为重复爬取启用缓存

### 4. 链接选择
- 爬虫基于以下因素优先链接：
  - 与查询的相关性
  - 预期信息增益
  - URL结构和深度

## 示例

### 研究助手

```python
# 收集编程概念信息
result = await adaptive.digest(
    start_url="链接2",
    query="python decorators implementation patterns"
)

# 获取最相关摘录
for doc in adaptive.get_relevant_content(top_k=3):
    print(f"\nFrom: {doc['url']}")
    print(f"Relevance: {doc['score']:.2%}")
    print(doc['content'][:500] + "...")
```

### 知识库构建器

```python
# 构建关于机器学习的聚焦知识库
queries = [
    "supervised learning algorithms",
    "neural network architectures", 
    "model evaluation metrics"
]

for query in queries:
    await adaptive.digest(
        start_url="https://scikit-learn.org/stable/",
        query=query
    )
    
# 导出组合知识库
adaptive.export_knowledge_base("ml_knowledge.jsonl")
```

### API文档爬虫

```python
# 智能爬取API文档
config = AdaptiveConfig(
    confidence_threshold=0.85,  # 更高阈值确保完整性
    max_pages=30
)

adaptive = AdaptiveCrawler(crawler, config)
result = await adaptive.digest(
    start_url="https://api.example.com/docs",
    query="authentication endpoints rate limits"
)
```

## 后续步骤

- 了解[高级自适应策略](../advanced/adaptive-strategies.md)
- 查阅[AdaptiveCrawler API参考](../api/adaptive-crawler.md)
- 查看更多[示例](https://github.com/unclecode/crawl4ai/tree/main/docs/examples/adaptive_crawling)

## 常见问题

**问：这与传统爬取有何不同？**
答：传统爬取遵循固定模式(BFS/DFS)。自适应爬取基于信息增益智能决定跟踪哪些链接以及何时停止。

**问：能否用于JavaScript密集型网站？**
答：可以！AdaptiveCrawler继承了AsyncWebCrawler的所有能力，包括JavaScript执行。

**问：如何处理大型网站？**
答：算法自然将爬取限制在相关部分。使用`max_pages`作为安全限制。

**问：能否自定义评分算法？**
答：高级用户可实现自定义策略。参见[自适应策略](../advanced/adaptive-strategies.md)。