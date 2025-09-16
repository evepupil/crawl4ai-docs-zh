# 深度爬取

Crawl4AI最强大的功能之一是能够执行**可配置的深度爬取**，可以探索网站的多层页面。通过精细控制爬取深度、域名边界和内容过滤，Crawl4AI为您提供了精确提取所需内容的工具。

在本教程中，您将学习：

1. 如何使用BFS策略设置**基础深度爬虫**  
2. 理解**流式与非流式**输出的区别  
3. 实现**过滤器和评分器**来定位特定内容  
4. 创建**高级过滤链**实现复杂爬取  
5. 使用**最佳优先爬取**实现智能探索优先级  

> **先决条件**  
> - 您已完成或阅读过[AsyncWebCrawler基础](../core/simple-crawling.md)以了解如何运行简单爬取。  
> - 您知道如何配置`CrawlerRunConfig`。

---

## 1. 快速示例

这是一个使用**BFSDeepCrawlStrategy**实现基础深度爬取的最小代码示例：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

async def main():
    # 配置2层深度爬取
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=2, 
            include_external=False
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True
    )
    
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun("https://example.com", config=config)
        
        print(f"总共爬取了{len(results)}个页面")
        
        # 访问单个结果
        for result in results[:3]:  # 显示前3个结果
            print(f"URL: {result.url}")
            print(f"深度: {result.metadata.get('depth', 0)}")

if __name__ == "__main__":
    asyncio.run(main())
```

**发生了什么？**  
- `BFSDeepCrawlStrategy(max_depth=2, include_external=False)`指示Crawl4AI：
  - 爬取起始页面(深度0)再加2层深度
  - 保持在同一个域名内(不跟踪外部链接)
- 每个结果包含如爬取深度等元数据
- 所有爬取完成后以列表形式返回结果

---

## 2. 理解深度爬取策略选项

### 2.1 BFSDeepCrawlStrategy (广度优先搜索)

**BFSDeepCrawlStrategy**使用广度优先方法，先探索同一深度的所有链接再深入：

```python
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

# 基础配置
strategy = BFSDeepCrawlStrategy(
    max_depth=2,               # 爬取起始页面+2层深度
    include_external=False,    # 保持在同一个域名内
    max_pages=50,              # 最大爬取页面数(可选)
    score_threshold=0.3,       # URL爬取的最低分数(可选)
)
```

**关键参数：**
- **`max_depth`**: 起始页面之外的爬取层数
- **`include_external`**: 是否跟踪其他域名的链接
- **`max_pages`**: 最大爬取页面数(默认：无限)
- **`score_threshold`**: URL爬取的最低分数(默认：-inf)
- **`filter_chain`**: 用于URL过滤的FilterChain实例
- **`url_scorer`**: 用于评估URL的评分器实例

### 2.2 DFSDeepCrawlStrategy (深度优先搜索)

**DFSDeepCrawlStrategy**使用深度优先方法，尽可能深入一个分支再回溯。

```python
from crawl4ai.deep_crawling import DFSDeepCrawlStrategy

# 基础配置
strategy = DFSDeepCrawlStrategy(
    max_depth=2,               # 爬取起始页面+2层深度
    include_external=False,    # 保持在同一个域名内
    max_pages=30,              # 最大爬取页面数(可选)
    score_threshold=0.5,       # URL爬取的最低分数(可选)
)
```

**关键参数：**
- **`max_depth`**: 起始页面之外的爬取层数
- **`include_external`**: 是否跟踪其他域名的链接
- **`max_pages`**: 最大爬取页面数(默认：无限)
- **`score_threshold`**: URL爬取的最低分数(默认：-inf)
- **`filter_chain`**: 用于URL过滤的FilterChain实例
- **`url_scorer`**: 用于评估URL的评分器实例

### 2.3 BestFirstCrawlingStrategy (⭐️ - 推荐深度爬取策略)

对于更智能的爬取，使用**BestFirstCrawlingStrategy**配合评分器优先处理最相关页面：

```python
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer

# 创建评分器
scorer = KeywordRelevanceScorer(
    keywords=["crawl", "example", "async", "configuration"],
    weight=0.7
)

# 配置策略
strategy = BestFirstCrawlingStrategy(
    max_depth=2,
    include_external=False,
    url_scorer=scorer,
    max_pages=25,              # 最大爬取页面数(可选)
)
```

这种爬取方式：
- 基于评分器标准评估每个发现的URL
- 优先访问高分页面
- 帮助将爬取资源集中在最相关内容上
- 可通过`max_pages`限制总爬取页面数
- 不需要`score_threshold`，因为它自然按分数排序

---

## 3. 流式与非流式结果

Crawl4AI可以两种模式返回结果：

### 3.1 非流式模式(默认)

```python
config = CrawlerRunConfig(
    deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=1),
    stream=False  # 默认行为
)

async with AsyncWebCrawler() as crawler:
    # 等待收集所有结果后再返回
    results = await crawler.arun("https://example.com", config=config)
    
    for result in results:
        process_result(result)
```

**何时使用非流式模式：**
- 您需要在处理前获得完整数据集
- 您要对所有结果执行批量操作
- 爬取时间不是关键因素

### 3.2 流式模式

```python
config = CrawlerRunConfig(
    deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=1),
    stream=True  # 启用流式
)

async with AsyncWebCrawler() as crawler:
    # 返回异步迭代器
    async for result in await crawler.arun("https://example.com", config=config):
        # 结果可用时立即处理
        process_result(result)
```

**流式模式的优点：**
- 结果发现后立即处理
- 在爬取继续时可处理早期结果
- 更适合实时应用或渐进显示
- 处理大量页面时减少内存压力

---

## 4. 使用过滤链筛选内容

过滤器帮助您缩小爬取页面范围。使用**FilterChain**组合多个过滤器实现强大定位。

### 4.1 基础URL模式过滤器

```python
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter

# 仅跟踪包含"blog"或"docs"的URL
url_filter = URLPatternFilter(patterns=["*blog*", "*docs*"])

config = CrawlerRunConfig(
    deep_crawl_strategy=BFSDeepCrawlStrategy(
        max_depth=1,
        filter_chain=FilterChain([url_filter])
    )
)
```

### 4.2 组合多个过滤器

```python
from crawl4ai.deep_crawling.filters import (
    FilterChain,
    URLPatternFilter,
    DomainFilter,
    ContentTypeFilter
)

# 创建过滤器链
filter_chain = FilterChain([
    # 仅跟踪特定模式的URL
    URLPatternFilter(patterns=["*guide*", "*tutorial*"]),
    
    # 仅爬取特定域名
    DomainFilter(
        allowed_domains=["docs.example.com"],
        blocked_domains=["old.docs.example.com"]
    ),
    
    # 仅包含特定内容类型
    ContentTypeFilter(allowed_types=["text/html"])
])

config = CrawlerRunConfig(
    deep_crawl_strategy=BFSDeepCrawlStrategy(
        max_depth=2,
        filter_chain=filter_chain
    )
)
```

### 4.3 可用过滤器类型

Crawl4AI包含多种专用过滤器：

- **`URLPatternFilter`**: 使用通配符语法匹配URL模式
- **`DomainFilter`**: 控制包含或排除的域名
- **`ContentTypeFilter`**: 基于HTTP Content-Type过滤
- **`ContentRelevanceFilter`**: 使用与文本查询的相似度
- **`SEOFilter`**: 评估SEO元素(元标签、标题等)

---

## 5. 使用评分器实现优先爬取

评分器为发现的URL分配优先级值，帮助爬虫优先关注最相关内容。

### 5.1 KeywordRelevanceScorer

```python
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy

# 创建关键词相关性评分器
keyword_scorer = KeywordRelevanceScorer(
    keywords=["crawl", "example", "async", "configuration"],
    weight=0.7  # 此评分器的重要性(0.0到1.0)
)

config = CrawlerRunConfig(
    deep_crawl_strategy=BestFirstCrawlingStrategy(
        max_depth=2,
        url_scorer=keyword_scorer
    ),
    stream=True  # 推荐与BestFirstCrawling配合使用
)

# 结果将按相关性分数排序
async with AsyncWebCrawler() as crawler:
    async for result in await crawler.arun("https://example.com", config=config):
        score = result.metadata.get("score", 0)
        print(f"分数: {score:.2f} | {result.url}")
```

**评分器工作原理：**
- 在爬取前评估每个发现的URL
- 基于各种信号计算相关性
- 帮助爬虫做出智能的遍历顺序选择

---

## 6. 高级过滤技术

### 6.1 用于质量评估的SEO过滤器

**SEOFilter**帮助您识别具有强SEO特征的页面：

```python
from crawl4ai.deep_crawling.filters import FilterChain, SEOFilter

# 创建SEO过滤器，查找页面元数据中的特定关键词
seo_filter = SEOFilter(
    threshold=0.5,  # 最低分数(0.0到1.0)
    keywords=["tutorial", "guide", "documentation"]
)

config = CrawlerRunConfig(
    deep_crawl_strategy=BFSDeepCrawlStrategy(
        max_depth=1,
        filter_chain=FilterChain([seo_filter])
    )
)
```

### 6.2 内容相关性过滤器

**ContentRelevanceFilter**分析页面的实际内容：

```python
from crawl4ai.deep_crawling.filters import FilterChain, ContentRelevanceFilter

# 创建内容相关性过滤器
relevance_filter = ContentRelevanceFilter(
    query="使用Python进行网络爬取和数据提取",
    threshold=0.7  # 最低相似度分数(0.0到1.0)
)

config = CrawlerRunConfig(
    deep_crawl_strategy=BFSDeepCrawlStrategy(
        max_depth=1,
        filter_chain=FilterChain([relevance_filter])
    )
)
```

此过滤器：
- 测量查询与页面内容的语义相似度
- 是基于BM25的相关性过滤器，使用头部部分内容

---

## 7. 构建完整的高级爬虫

此示例结合多种技术实现复杂爬取：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.filters import (
    FilterChain,
    DomainFilter,
    URLPatternFilter,
    ContentTypeFilter
)
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer

async def run_advanced_crawler():
    # 创建复杂过滤器链
    filter_chain = FilterChain([
        # 域名边界
        DomainFilter(
            allowed_domains=["docs.example.com"],
            blocked_domains=["old.docs.example.com"]
        ),
        
        # 要包含的URL模式
        URLPatternFilter(patterns=["*guide*", "*tutorial*", "*blog*"]),
        
        # 内容类型过滤
        ContentTypeFilter(allowed_types=["text/html"])
    ])

    # 创建相关性评分器
    keyword_scorer = KeywordRelevanceScorer(
        keywords=["crawl", "example", "async", "configuration"],
        weight=0.7
    )

    # 设置配置
    config = CrawlerRunConfig(
        deep_crawl_strategy=BestFirstCrawlingStrategy(
            max_depth=2,
            include_external=False,
            filter_chain=filter_chain,
            url_scorer=keyword_scorer
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        stream=True,
        verbose=True
    )

    # 执行爬取
    results = []
    async with AsyncWebCrawler() as crawler:
        async for result in await crawler.arun("https://docs.example.com", config=config):
            results.append(result)
            score = result.metadata.get("score", 0)
            depth = result.metadata.get("depth", 0)
            print(f"深度: {depth} | 分数: {score:.2f} | {result.url}")

    # 分析结果
    print(f"爬取了{len(results)}个高价值页面")
    print(f"平均分数: {sum(r.metadata.get('score', 0) for r in results) / len(results):.2f}")

    # 按深度分组
    depth_counts = {}
    for result in results:
        depth = result.metadata.get("depth", 0)
        depth_counts[depth] = depth_counts.get(depth, 0) + 1

    print("按深度爬取的页面:")
    for depth, count in sorted(depth_counts.items()):
        print(f"  深度 {depth}: {count}个页面")

if __name__ == "__main__":
    asyncio.run(run_advanced_crawler())
```

---


## 8. 限制和控制爬取规模

### 8.1 使用max_pages

您可以使用`max_pages`参数限制总爬取页面数：

```python
# 无论深度如何，限制为20个页面
strategy = BFSDeepCrawlStrategy(
    max_depth=3,
    max_pages=20
)
```

此功能适用于：
- 控制API成本
- 设置可预测的执行时间
- 专注于最重要的内容
- 在完整执行前测试爬取配置

### 8.2 使用score_threshold

对于BFS和DFS策略，您可以设置最低分数阈值仅爬取高质量页面：

```python
# 仅跟踪分数高于0.4的链接
strategy = DFSDeepCrawlStrategy(
    max_depth=2,
    url_scorer=KeywordRelevanceScorer(keywords=["api", "guide", "reference"]),
    score_threshold=0.4  # 跳过低于此值的URL
)
```

注意对于BestFirstCrawlingStrategy，不需要score_threshold，因为页面已经按最高分优先处理。

## 9. 常见陷阱与技巧

1.**设置现实限制。** 谨慎使用`max_depth`值>3，这会指数级增加爬取规模。使用`max_pages`设置硬限制。

2.**不要忽视评分组件。** BestFirstCrawling配合调优良好的评分器效果最佳。尝试关键词权重以获得最佳优先级。

3.**做良好的网络公民。** 尊重robots.txt。(默认禁用)
  
4.**优雅处理页面错误。** 并非所有页面都可访问。处理结果时检查`result.status`。

5.**平衡广度与深度。** 明智选择策略 - BFS用于全面覆盖，DFS用于深度探索，BestFirst用于基于相关性的聚焦爬取。

---

## 10. 总结与下一步

在本**使用Crawl4AI进行深度爬取**教程中，您学会了：

- 配置**BFSDeepCrawlStrategy**、**DFSDeepCrawlStrategy**和**BestFirstCrawlingStrategy**
- 以流式或非流式模式处理结果
- 应用过滤器定位特定内容
- 使用评分器优先处理最相关页面
- 使用`max_pages`和`score_threshold`参数限制爬取
- 构建结合多种技术的完整高级爬虫

有了这些工具，您可以高效地从网站大规模提取结构化数据，精确聚焦于特定用例所需的内容。