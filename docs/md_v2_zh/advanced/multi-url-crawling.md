# 使用调度器进行高级多URL爬取

> **注意**：Crawl4AI 支持用于**并行**或**限流**爬取的高级调度器，提供动态速率限制和内存使用检查。内置的 `arun_many()` 函数使用这些调度器来高效处理并发。

## 1. 简介

当爬取多个URL时：

- **基础**：在循环中使用 `arun()`（简单但效率较低）
- **更好**：使用 `arun_many()`，它通过适当的并发控制高效处理多个URL
- **最佳**：根据您的特定需求自定义调度器行为（内存管理、速率限制等）

**为什么使用调度器？**

- **自适应**：基于内存的调度器可以根据系统资源暂停或减速
- **速率限制**：内置速率限制，针对429/503响应采用指数退避
- **实时监控**：实时显示正在进行的任务、内存使用情况和性能
- **灵活性**：可在内存自适应或基于信号量的并发之间选择

---

## 2. 核心组件

### 2.1 速率限制器

```python
class RateLimiter:
    def __init__(
        # 请求之间的随机延迟范围
        base_delay: Tuple[float, float] = (1.0, 3.0),  
        
        # 最大退避延迟
        max_delay: float = 60.0,                        
        
        # 放弃前的重试次数
        max_retries: int = 3,                          
        
        # 触发退避的状态码
        rate_limit_codes: List[int] = [429, 503]        
    )
```

以下是**RateLimiter**的修订简化说明，重点关注构造函数参数，并遵循您的markdown风格和mkDocs指南。

#### RateLimiter 构造函数参数

**RateLimiter**是一个实用工具，用于管理请求节奏，避免服务器过载或因速率限制而被阻止。它在内部操作以延迟请求和处理重试，但可以通过其构造函数参数进行配置。

**`RateLimiter` 构造函数的参数：**

1. **`base_delay`** (`Tuple[float, float]`, 默认: `(1.0, 3.0)`)  
  对同一域名的连续请求之间的随机延迟范围（以秒为单位）。

- 每个请求的延迟在 `base_delay[0]` 和 `base_delay[1]` 之间随机选择。
- 这可以防止以可预测的频率发送请求，降低触发速率限制的可能性。

**示例：**  
如果 `base_delay = (2.0, 5.0)`，延迟可能随机选择为 `2.3s`、`4.1s` 等。

---

2. **`max_delay`** (`float`, 默认: `60.0`)  
  发生速率限制错误时的最大允许延迟。

- 当服务器返回速率限制响应（例如429或503）时，延迟会随抖动呈指数增长。
- `max_delay` 确保延迟不会增长到不合理的高值，将其限制在此值。

**示例：**  
对于 `max_delay = 30.0`，即使退避计算建议延迟为 `45s`，它也会限制在 `30s`。

---

3. **`max_retries`** (`int`, 默认: `3`)  
  如果发生速率限制错误，请求的最大重试次数。

- 遇到速率限制响应后，`RateLimiter` 会重试请求，最多重试此次数。
- 如果所有重试都失败，则请求标记为失败，过程继续。

**示例：**  
如果 `max_retries = 3`，系统会在放弃前重试失败的请求三次。

---

4. **`rate_limit_codes`** (`List[int]`, 默认: `[429, 503]`)  
  触发速率限制逻辑的HTTP状态码列表。

- 这些状态码表示服务器不堪重负或正在主动限制请求。
- 您可以根据特定的服务器行为自定义此列表以包含其他代码。

**示例：**  
如果 `rate_limit_codes = [429, 503, 504]`，爬虫将在遇到这三个错误代码时退避。

---

**如何使用 `RateLimiter`：**

以下是在项目中初始化和使用 `RateLimiter` 的示例：

```python
from crawl4ai import RateLimiter

# 使用自定义设置创建 RateLimiter
rate_limiter = RateLimiter(
    base_delay=(2.0, 4.0),  # 2-4秒之间的随机延迟
    max_delay=30.0,         # 延迟上限为30秒
    max_retries=5,          # 在速率限制错误时最多重试5次
    rate_limit_codes=[429, 503]  # 处理这些HTTP状态码
)

# RateLimiter 将在内部处理延迟和重试
# 无需为其操作进行额外设置
```

`RateLimiter` 与 `MemoryAdaptiveDispatcher` 和 `SemaphoreDispatcher` 等调度器无缝集成，确保请求正确节奏，无需用户干预。其内部机制管理延迟和重试，以避免服务器过载，同时最大化效率。


### 2.2 爬虫监视器

CrawlerMonitor 提供对爬取操作的实时可见性：

```python
from crawl4ai import CrawlerMonitor, DisplayMode
monitor = CrawlerMonitor(
    # 实时显示中的最大行数
    max_visible_rows=15,          

    # DETAILED 或 AGGREGATED 视图
    display_mode=DisplayMode.DETAILED  
)
```

**显示模式**:

1. **DETAILED**：显示单个任务状态、内存使用情况和时间
2. **AGGREGATED**：显示摘要统计信息和整体进度

---

## 3. 可用调度器

### 3.1 MemoryAdaptiveDispatcher（默认）

根据系统内存使用情况自动管理并发：

```python
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher

dispatcher = MemoryAdaptiveDispatcher(
    memory_threshold_percent=90.0,  # 如果内存超过此值则暂停
    check_interval=1.0,             # 检查内存的频率
    max_session_permit=10,          # 最大并发任务数
    rate_limiter=RateLimiter(       # 可选的速率限制
        base_delay=(1.0, 2.0),
        max_delay=30.0,
        max_retries=2
    ),
    monitor=CrawlerMonitor(         # 可选监控
        max_visible_rows=15,
        display_mode=DisplayMode.DETAILED
    )
)
```

**构造函数参数：**

1. **`memory_threshold_percent`** (`float`, 默认: `90.0`)  
  指定内存使用阈值（百分比）。如果系统内存使用超过此值，调度器将暂停爬取以防止系统过载。

2. **`check_interval`** (`float`, 默认: `1.0`)  
  调度器检查系统内存使用情况的间隔（以秒为单位）。

3. **`max_session_permit`** (`int`, 默认: `10`)  
  允许的最大并发爬取任务数。这确保在保持并发的同时遵守资源限制。

4. **`memory_wait_timeout`** (`float`, 默认: `600.0`)
  可选的超时时间（以秒为单位）。如果内存使用超过 `memory_threshold_percent` 的时间长于此持续时间，则会引发 `MemoryError`。

5. **`rate_limiter`** (`RateLimiter`, 默认: `None`)  
  可选的速率限制逻辑，以避免服务器端阻塞（例如，用于处理429或503错误）。有关详细信息，请参阅 **RateLimiter**。

6. **`monitor`** (`CrawlerMonitor`, 默认: `None`)  
  可选的监控，用于实时任务跟踪和性能洞察。有关详细信息，请参阅 **CrawlerMonitor**。

---

### 3.2 SemaphoreDispatcher

提供具有固定限制的简单并发控制：

```python
from crawl4ai.async_dispatcher import SemaphoreDispatcher

dispatcher = SemaphoreDispatcher(
    max_session_permit=20,         # 最大并发任务数
    rate_limiter=RateLimiter(      # 可选的速率限制
        base_delay=(0.5, 1.0),
        max_delay=10.0
    ),
    monitor=CrawlerMonitor(        # 可选监控
        max_visible_rows=15,
        display_mode=DisplayMode.DETAILED
    )
)
```

**构造函数参数：**

1. **`max_session_permit`** (`int`, 默认: `20`)  
  允许的最大并发爬取任务数，与信号量槽无关。

2. **`rate_limiter`** (`RateLimiter`, 默认: `None`)  
  可选的速率限制逻辑，以避免服务器过载。有关详细信息，请参阅 **RateLimiter**。

3. **`monitor`** (`CrawlerMonitor`, 默认: `None`)  
  可选的监控，用于跟踪任务进度和资源使用情况。有关详细信息，请参阅 **CrawlerMonitor**。

---

## 4. 使用示例

### 4.1 批处理（默认）

```python
async def crawl_batch():
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=False  # 默认：一次性获取所有结果
    )
    
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=10,
        monitor=CrawlerMonitor(
            display_mode=DisplayMode.DETAILED
        )
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # 一次性获取所有结果
        results = await crawler.arun_many(
            urls=urls,
            config=run_config,
            dispatcher=dispatcher
        )
        
        # 完成后处理所有结果
        for result in results:
            if result.success:
                await process_result(result)
            else:
                print(f"Failed to crawl {result.url}: {result.error_message}")
```

**回顾：**  
- **目的：** 执行批处理爬取，所有URL在爬取完成后一起处理。  
- **调度器：** 使用 `MemoryAdaptiveDispatcher` 来管理并发和系统内存。  
- **流：** 禁用 (`stream=False`)，因此所有结果一次性收集用于后处理。  
- **最佳用例：** 当您需要批量分析结果而不是在爬取过程中单独分析时。

---

### 4.2 流模式

```python
async def crawl_streaming():
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=True  # 启用流模式
    )
    
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=10,
        monitor=CrawlerMonitor(
            display_mode=DisplayMode.DETAILED
        )
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # 在结果可用时立即处理
        async for result in await crawler.arun_many(
            urls=urls,
            config=run_config,
            dispatcher=dispatcher
        ):
            if result.success:
                # 立即处理每个结果
                await process_result(result)
            else:
                print(f"Failed to crawl {result.url}: {极result.error_message}")
```

**回顾：**  
- **目的：** 启用流式处理以在结果可用时立即处理。  
- **调度器：** 使用 `MemoryAdaptiveDispatcher` 进行并发和内存管理。  
- **流：** 启用 (`stream=True`)，允许在爬取过程中进行实时处理。  
- **最佳用例：** 当您需要立即对结果采取行动时，例如用于实时分析或渐进式数据存储。

---

### 4.3 基于信号量的爬取

```python
async def crawl_with_semaphore(urls):
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(cache_mode=极CacheMode.BYPASS)
    
    dispatcher = SemaphoreDispatcher(
        semaphore_count=5,
        rate_limiter=RateLimiter(
            base_delay=(0.5, 1.0),
            max_delay=10.0
        ),
        monitor=C极rawlerMonitor(
            max_visible_rows=15,
            display_mode=DisplayMode.DETAILED
        )
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun_many(
            urls, 
            config=run_config,
            dispatcher=dispatcher
        )
        return results
```

**回顾：**  
- **目的：** 使用 `SemaphoreDispatcher` 以固定数量的槽限制并发。  
- **调度器：** 配置有信号量以控制并行爬取任务。  
- **速率限制器：** 通过调整请求节奏防止服务器过载。  
- **最佳用例：** 当您希望精确控制并发请求数，而不依赖于系统内存时。

---

### 4.4 Robots.txt 注意事项

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

async def main():
    urls = [
        "https://example1.com",
        "https://example2.com",
        "https://example3.com"
    ]
    
    config = CrawlerRunConfig(
        cache_mode=CacheMode.ENABLED,
        check_robots_txt=True,  # 将尊重每个URL的robots.txt
        semaphore_count=3      # 最大并发请求数
    )
    
    async with AsyncWebCrawler() as crawler:
        async for result in crawler.arun_many(urls, config=config):
            if result.success:
                print(f"Successfully crawled {result.url}")
            elif result.status_code == 403 and "robots.txt" in result.error_message:
                print(f"Skipped {result.url} - blocked by robots.txt")
            else:
                print(f"Failed to crawl {result.url}: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
```

**回顾：**  
- **目的：** 确保遵守 `robots.txt` 规则，以实现道德和合法的网络爬取。  
- **配置：** 设置 `check_robots_txt=True` 以在爬取前针对 `robots.txt` 验证每个URL。  
- **调度器：** 处理具有并发限制的请求 (`semaphore_count=3`)。  
- **最佳用例：** 当爬取严格执行robots.txt策略的网站或用于负责任的爬取实践时。

---

## 5. 调度结果

每个爬取结果都包含调度信息：

```python
@dataclass
class DispatchResult:
    task_id: str
    memory_usage: float
    peak_memory: float
    start极_time: datetime
    end_time: datetime
    error_message: str = ""
```

通过 `result.dispatch_result` 访问：

```python
for result in results:
    if result.success:
        dr = result.dispatch_result
        print(f"URL: {result.url}")
        print(f"Memory: {dr.memory_usage:.1f}MB")
        print(f"Duration: {dr.end_time - dr.start_time}")
```

## 6. URL特定配置

当爬取多样化的内容类型时，您通常需要为不同的URL使用不同的配置。例如：
- PDF需要专门的提取
- 博客页面受益于内容过滤
- 动态站点需要JavaScript执行
- API端点需要JSON解析

### 6.1 基本URL模式匹配

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, MatchMode
from crawl4ai.processors.pdf import PDFContentScrapingStrategy
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def crawl_mixed_content():
    # 为不同的内容配置不同的策略
    configs = [
        # PDF文件 - 专门提取
        CrawlerRunConfig(
            url_matcher="*.pdf",
            scraping_strategy=PDFContentScrapingStrategy()
        ),
        
        # 博客/文章页面 - 内容过滤
        CrawlerRunConfig(
            url_matcher=["*/blog/*", "*/article/*"],
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(threshold=0.48)
            )
        ),
        
        # 动态页面 - JavaScript执行
        Crawler极RunConfig(
            url_matcher=lambda url: 'github.com' in url,
            js_code="window.scrollTo(0, 500);"
        ),
        
        # API端点 - JSON提取
        CrawlerRunConfig(
            url_matcher=lambda url: 'api' in url or url.endswith('.json'),
            # JSON提取的自定义设置
        ),
        
        # 其他所有内容的默认配置
        CrawlerRunConfig()  # 没有 url_matcher 意味着匹配所有URL（后备）
    ]
    
    # 混合URL
    urls = [
        "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "https://blog.python.org/",
        "https://github.com/microsoft/playwright",
        "https://httpbin.org/json",
        "极https://example.com/"
    ]
    
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun_many(
            urls=url极s,
            config=configs  # 传递配置列表
        )
        
        for result in results:
            print(f"{result.url}: {len(result.markdown)} chars")
```

### 6.2 高级模式匹配

**重要**：没有 `url_matcher`（或 `url_matcher=None`）的 `CrawlerRunConfig` 匹配所有URL。这使其成为完美的默认/后备配置。

`url_matcher` 参数支持三种类型的模式：

#### Glob模式（字符串）
```python
# 简单模式
"*.pdf"                    # 任何PDF文件
"*/api/*"                  # 路径中包含 /api/ 的任何URL
"https://*.example.com/*"  # 子域匹配
"*://example.com/blog/*"   # 任何协议
```

#### 自定义函数
```python
# 使用lambda的复杂逻辑
lambda url: url.startswith('https://') and 'secure' in url
lambda url: len(url) > 50 and url.count('/') > 5
lambda url: any(domain in url for domain in ['api.', 'data.', 'feed.'])
```

#### 具有AND/OR逻辑的混合列表
```python
# 组合多个条件
CrawlerRunConfig(
    url_matcher=[
        "https://*",                        # 必须是HTTPS
        lambda url: 'internal' in url,      # 必须包含'internal'
        lambda url: not url.endswith('.pdf') # 不能是PDF
    ],
    match_mode=MatchMode.AND  # 必须匹配所有条件
)
```

### 6.3 实用示例：新闻站点爬虫

```python
async def crawl_news_site():
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        rate_limiter=RateLimiter(base_delay=(1.0, 2.0))
    )
    
    configs = [
        # 主页 - 轻量提取
        CrawlerRunConfig(
            url_matcher=lambda url: url.rstrip('/') == 'https://news.ycombinator.com',
            css_selector="nav, .headline",
            extraction_strategy=None
        ),
        
        # 文章页面 - 完整提取
        CrawlerRunConfig(
            url_matcher="*/article/*",
            extraction_strategy=CosineStrategy(
                semantic_filter="article content",
                word_count_threshold=100
            ),
            screenshot=True,
            excluded_tags=["nav", "aside", "footer"]
        ),
        
        # 作者页面 - 专注于元数据
        CrawlerRunConfig(
            url_matcher="*/author/*",
            extraction_strategy=JsonCssExtractionStrategy({
                "name": "h1.author-name",
                "bio": ".author-bio",
                "articles": "article.post-card h2"
            })
        ),
        
        # 其他所有内容
        CrawlerRunConfig()
    ]
    
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun_many(
            urls=news_urls,
            config=configs,
            dispatcher=dispatcher
        )
```

### 6.4 最佳实践

1. **顺序很重要**：配置按顺序评估 - 将特定模式放在通用模式之前
2. **默认配置行为**：
   - 没有 `url_matcher` 的配置匹配所有URL
   - 如果要处理所有URL，请始终将默认配置作为最后一项包含
   - 如果没有默认配置，不匹配的URL将失败并显示“未找到匹配的配置”
3. **测试您的模式**：使用配置的 `is_match()` 方法来测试模式：
   ```python
   config = CrawlerRunConfig(url_matcher="*.pdf")
   print(config.is_match("https://example.com/doc.pdf"))  # True
   
   default_config = CrawlerRunConfig()  # 没有 url_matcher
   print(default_config.is_match("https://any-url.com"))  # True - 匹配所有内容！
   ```
4. **优化性能**：
   - 对静态内容禁用JS
   - 对数据API跳过截图
   - 使用适当的提取策略

## 7. 总结

1. **两种调度器类型**：

   - MemoryAdaptiveDispatcher（默认）：基于内存的动态并发
   - SemaphoreDispatcher：固定并发限制

2. **可选组件**：

   - RateLimiter：智能请求节奏和退避
   - CrawlerMonitor：实时进度可视化

3. **主要优势**：

   - 自动内存管理
   - 内置速率限制
   - 实时进度监控
   - 灵活的并发控制

选择最适合您需求的调度器：

- **MemoryAdaptiveDispatcher**：适用于大规模爬取或资源有限的情况
- **SemaphoreDispatcher**：适用于简单、固定并发的场景