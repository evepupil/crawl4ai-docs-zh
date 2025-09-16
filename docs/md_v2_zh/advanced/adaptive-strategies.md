# 高级自适应策略

## 概述

虽然默认的自适应爬取配置适用于大多数用例，但理解底层策略和评分机制可以让您针对特定领域和需求微调爬虫。

## 三层评分系统

### 1. 覆盖率分数

覆盖率衡量您的知识库对查询词和相关概念的覆盖全面程度。

#### 数学基础

```python
Coverage(K, Q) = Σ(t ∈ Q) score(t, K) / |Q|

where score(t, K) = doc_coverage(t) × (1 + freq_boost(t))
```

#### 组成部分

- **文档覆盖率**：包含该术语的文档百分比
- **频率提升**：对术语频率的对数奖励
- **查询分解**：智能处理多词查询

#### 调整覆盖率

```python
# 对于包含特定术语的技术文档
config = AdaptiveConfig(
    confidence_threshold=0.85,  # 要求高覆盖率
    top_k_links=5              # 撒更大的网
)

# 对于包含同义词的通用主题
config = AdaptiveConfig(
    confidence_threshold=0.6,   # 较低阈值
    top_k_links=2              # 更聚焦
)
```

### 2. 一致性分数

一致性评估跨页面的信息是否连贯且无矛盾。

#### 工作原理

1. 从每个文档中提取关键陈述
2. 跨文档比较陈述
3. 衡量一致性与矛盾
4. 返回归一化分数 (0-1)

#### 实际影响

- **高一致性 (>0.8)**：信息可靠且连贯
- **中等一致性 (0.5-0.8)**：存在一些变化，但总体一致
- **低一致性 (<0.5)**：信息冲突，需要更多来源

### 3. 饱和分数

饱和度检测新页面何时停止提供新信息。

#### 检测算法

```python
# 跟踪每页的新独特术语
new_terms_page_1 = 50
new_terms_page_2 = 30  # 第一个的60%
new_terms_page_3 = 15  # 第二个的50%
new_terms_page_4 = 5   # 第三个的33%
# 检测到饱和：收益快速递减
```

#### 配置

```python
config = AdaptiveConfig(
    min_gain_threshold=0.1  # 如果新信息<10%则停止
)
```

## 链接排名算法

### 预期信息增益

每个未爬取的链接根据以下因素评分：

```python
ExpectedGain(link) = Relevance × Novelty × Authority
```

#### 1. 相关性评分

在链接预览文本上使用 BM25 算法：

```python
relevance = BM25(link.preview_text, query)
```

因素：
- 预览中的术语频率
- 逆文档频率
- 预览长度归一化

#### 2. 新颖性估计

衡量链接与已爬取内容的差异程度：

```python
novelty = 1 - max_similarity(preview, knowledge_base)
```

防止爬取重复或高度相似的页面。

#### 3. 权威性计算

URL 结构和域名分析：

```python
authority = f(domain_rank, url_depth, url_structure)
```

因素：
- 域名声誉
- URL 深度（斜杠越少，权威性越高）
- 干净的 URL 结构

### 自定义链接评分

```python
class CustomLinkScorer:
    def score(self, link: Link, query: str, state: CrawlState) -> float:
        # 优先处理特定 URL 模式
        if "/api/reference/" in link.href:
            return 2.0  # 分数加倍
        
        # 降低某些部分的优先级
        if "/archive/" in link.href:
            return 0.1  # 分数降低90%
        
        # 默认评分
        return 1.0

# 与自适应爬虫一起使用
adaptive = AdaptiveCrawler(
    crawler,
    config=config,
    link_scorer=CustomLinkScorer()
)
```

## 领域特定配置

### 技术文档

```python
tech_doc_config = AdaptiveConfig(
    confidence_threshold=0.85,
    max_pages=30,
    top_k_links=3,
    min_gain_threshold=0.05  # 为小收益继续爬取
)
```

原理：
- 高阈值确保全面覆盖
- 较低的增益阈值捕获边缘情况
- 适度的链接跟踪以获取深度

### 新闻与文章

```python
news_config = AdaptiveConfig(
    confidence_threshold=0.6,
    max_pages=10,
    top_k_links=5,
    min_gain_threshold=0.15  # 重复时快速停止
)
```

原理：
- 较低阈值（文章经常重复信息）
- 较高的增益阈值（避免重复报道）
- 每页更多链接（探索不同视角）

### 电子商务

```python
ecommerce_config = AdaptiveConfig(
    confidence_threshold=0.7,
    max_pages=20,
    top_k_links=2,
    min_gain_threshold=0.1
)
```

原理：
- 平衡阈值以应对产品变体
- 聚焦链接跟踪（避免无限产品）
- 标准增益阈值

### 研究与学术

```python
research_config = AdaptiveConfig(
    confidence_threshold=0.9,
    max_pages=50,
    top_k_links=4,
    min_gain_threshold=0.02  # 非常低 - 捕获引用
)
```

原理：
- 非常高的阈值以确保完整性
- 允许许多页面进行彻底研究
- 非常低的增益阈值以捕获参考文献

## 性能优化

### 内存管理

```python
# 对于大型爬取，使用流式处理
config = AdaptiveConfig(
    max_pages=100,
    save_state=True,
    state_path="large_crawl.json"
)

# 定期清理状态
if len(state.knowledge_base) > 1000:
    # 仅保留最相关的
    state.knowledge_base = get_top_relevant(state.knowledge_base, 500)
```

### 并行处理

```python
# 使用多个起点
start_urls = [
    "https://docs.example.com/intro",
    "https://docs.example.com/api",
    "https://docs.example.com/guides"
]

# 并行爬取
tasks = [
    adaptive.digest(url, query)
    for url in start_urls
]
results = await asyncio.gather(*tasks)
```

### 缓存策略

```python
# 为重复爬取启用缓存
async with AsyncWebCrawler(
    config=BrowserConfig(
        cache_mode=CacheMode.ENABLED
    )
) as crawler:
    adaptive = AdaptiveCrawler(crawler, config)
```

## 调试与分析

### 启用详细日志记录

```python
import logging

logging.basicConfig(level=logging.DEBUG)
adaptive = AdaptiveCrawler(crawler, config, verbose=True)
```

### 分析爬取模式

```python
# 爬取后
state = await adaptive.digest(start_url, query)

# 分析链接选择
print("链接选择顺序:")
for i, url in enumerate(state.crawl_order):
    print(f"{i+1}. {url}")

# 分析术语发现率
print("\n术语发现率:")
for i, new_terms in enumerate(state.new_terms_history):
    print(f"Page {i+1}: {new_terms} new terms")

# 分析分数进展
print("\n分数进展:")
print(f"覆盖率: {state.metrics['coverage_history']}")
print(f"饱和度: {state.metrics['saturation_history']}")
```

### 导出以供分析

```python
# 导出详细指标
import json

metrics = {
    "query": query,
    "total_pages": len(state.crawled_urls),
    "confidence": adaptive.confidence,
    "coverage_stats": adaptive.coverage_stats,
    "crawl_order": state.crawl_order,
    "term_frequencies": dict(state.term_frequencies),
    "new_terms_history": state.new_terms_history
}

with open("crawl_analysis.json", "w") as f:
    json.dump(metrics, f, indent=2)
```

## 自定义策略

### 实现自定义策略

```python
from crawl4ai.adaptive_crawler import BaseStrategy

class DomainSpecificStrategy(BaseStrategy):
    def calculate_coverage(self, state: CrawlState) -> float:
        # 自定义覆盖率计算
        # 例如，更重地加权某些术语
        pass
    
    def calculate_consistency(self, state: CrawlState) -> float:
        # 自定义一致性逻辑
        # 例如，领域特定验证
        pass
    
    def rank_links(self, links: List[Link], state: CrawlState) -> List[Link]:
        # 自定义链接排名
        # 例如，优先处理特定 URL 模式
        pass

# 使用自定义策略
adaptive = AdaptiveCrawler(
    crawler,
    config=config,
    strategy=DomainSpecificStrategy()
)
```

### 组合策略

```python
class HybridStrategy(BaseStrategy):
    def __init__(self):
        self.strategies = [
            TechnicalDocStrategy(),
            SemanticSimilarityStrategy(),
            URLPatternStrategy()
        ]
    
    def calculate_confidence(self, state: CrawlState) -> float:
        # 策略的加权组合
        scores = [s.calculate_confidence(state) for s in self.strategies]
        weights = [0.5, 0.3, 0.2]
        return sum(s * w for s, w in zip(scores, weights))
```

## 最佳实践

### 1. 从保守开始

从默认设置开始，并根据结果进行调整：

```python
# 从默认值开始
result = await adaptive.digest(url, query)

# 分析并调整
if adaptive.confidence < 0.7:
    config.max_pages += 10
    config.confidence_threshold -= 0.1
```

### 2. 监控资源使用情况

```python
import psutil

# 在大型爬取前检查内存
memory_percent = psutil.virtual_memory().percent
if memory_percent > 80:
    config.max_pages = min(config.max_pages, 20)
```

### 3. 使用领域知识

```python
# 对于 API 文档
if "api" in start_url:
    config.top_k_links = 2  # API 具有清晰的结构
    
# 对于博客
if "blog" in start_url:
    config.min_gain_threshold = 0.2  # 避免类似帖子
```

### 4. 验证结果

```python
# 始终验证知识库
relevant_content = adaptive.get_relevant_content(top_k=10)

# 检查覆盖率
query_terms = set(query.lower().split())
covered_terms = set()

for doc in relevant_content:
    content_lower = doc['content'].lower()
    for term in query_terms:
        if term in content_lower:
            covered_terms.add(term)

coverage_ratio = len(covered_terms) / len(query_terms)
print(f"查询术语覆盖率: {coverage_ratio:.0%}")
```

## 后续步骤

- 探索[自定义策略实现](../tutorials/custom-adaptive-strategies.md)
- 了解[知识库管理](../tutorials/knowledge-base-management.md)
- 查看[性能基准](../benchmarks/adaptive-performance.md)