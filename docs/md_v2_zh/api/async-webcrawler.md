# AsyncWebCrawler

**`AsyncWebCrawler`** 是 Crawl4AI 中异步网络爬取的核心类。通常你只需创建**一次**，可选地通过 **`BrowserConfig`** 进行定制（例如无头模式、用户代理），然后使用不同的 **`CrawlerRunConfig`** 对象多次**运行** **`arun()`**。

**推荐用法**：

1. **创建**一个 `BrowserConfig` 用于全局浏览器设置。  

2. **实例化** `AsyncWebCrawler(config=browser_config)`。  

3. 在异步上下文管理器 (`async with`) 中使用爬虫，或手动管理启动/关闭。  

4. 对每个目标页面**调用** `arun(url, config=crawler_run_config)`。

---

## 1. 构造函数概述

```python
class AsyncWebCrawler:
    def __init__(
        self,
        crawler_strategy: Optional[AsyncCrawlerStrategy] = None,
        config: Optional[BrowserConfig] = None,
        always_bypass_cache: bool = False,           # 已弃用
        always_by_pass_cache: Optional[bool] = None, # 也已弃用
        base_directory: str = ...,
        thread_safe: bool = False,
        **kwargs,
    ):
        """
        创建 AsyncWebCrawler 实例。

        Args:
            crawler_strategy: 
                （高级用法）如需自定义爬取策略可提供。
            config: 
                指定浏览器设置的 BrowserConfig 对象。
            always_bypass_cache: 
                （已弃用）改用 CrawlerRunConfig.cache_mode。
            base_directory:     
                存储缓存/日志的文件夹（如适用）。
            thread_safe: 
                若为 True，尝试实现一些并发安全措施。通常为 False。
            **kwargs: 
                其他遗留或调试参数。
        """
    )

### 典型初始化

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig

browser_cfg = BrowserConfig(
    browser_type="chromium",
    headless=True,
    verbose=True
)

crawler = AsyncWebCrawler(config=browser_cfg)
```

**注意事项**：

- **遗留**参数如 `always_bypass_cache` 仍保留以向后兼容，但建议在 **`CrawlerRunConfig`** 中设置**缓存**策略。

---

## 2. 生命周期：启动/关闭或上下文管理器

### 2.1 上下文管理器（推荐）

```python
async with AsyncWebCrawler(config=browser_cfg) as crawler:
    result = await crawler.arun("https://example.com")
    # 爬虫会自动释放资源（关闭浏览器等）
```

当 `async with` 代码块结束时，爬虫会自动清理资源。

### 2.2 手动启动 & 关闭

```python
crawler = AsyncWebCrawler(config=browser_cfg)
await crawler.start()

result1 = await crawler.arun("https://example.com")
result2 = await crawler.arun("https://another.com")

await crawler.close()
```

若需**长时间运行**应用或需要完全控制爬虫生命周期，可使用此方式。

---

## 3. 核心方法：`arun()`

```python
async def arun(
    self,
    url: str,
    config: Optional[CrawlerRunConfig] = None,
    # 为向后兼容保留的遗留参数...
) -> CrawlResult:
    ...
```

### 3.1 新式用法

通过 `CrawlerRunConfig` 对象配置爬取的所有细节——内容过滤、缓存、会话复用、JS 代码、截图等。

```python
import asyncio
from crawl4ai import CrawlerRunConfig, CacheMode

run_cfg = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    css_selector="main.article",
    word_count_threshold=10,
    screenshot=True
)

async with AsyncWebCrawler(config=browser_cfg) as crawler:
    result = await crawler.arun("https://example.com/news", config=run_cfg)
    print("清理后HTML长度:", len(result.cleaned_html))
    if result.screenshot:
        print("截图base64长度:", len(result.screenshot))
```

### 3.2 仍支持遗留参数

为**向后兼容**，`arun()` 仍接受直接参数如 `css_selector=...`、`word_count_threshold=...` 等，但强烈建议迁移至 **`CrawlerRunConfig`**。

---

## 4. 批量处理：`arun_many()`

```python
async def arun_many(
    self,
    urls: List[str],
    config: Optional[CrawlerRunConfig] = None,
    # 为向后兼容保留的遗留参数...
) -> List[CrawlResult]:
    """
    处理多个URL，具备智能速率限制和资源监控功能。
    """
```

### 4.1 资源感知爬取

`arun_many()` 方法使用智能调度器实现：

- 监控系统内存使用
- 自适应速率限制
- 提供详细进度监控
- 高效管理并发爬取

### 4.2 使用示例

查看页面 [多URL爬取](../advanced/multi-url-crawling.md) 了解 `arun_many()` 的详细用法示例。

```python

### 4.3 关键特性

1. **速率限制**
   
   - 请求间自动延迟
   - 检测到速率限制时指数退避
   - 针对特定域名的速率限制
   - 可配置的重试策略

2. **资源监控**

   - 内存使用跟踪
   - 基于系统负载的自适应并发
   - 资源受限时自动暂停

3. **进度监控**

   - 详细或聚合的进度显示
   - 实时状态更新
   - 内存使用统计

4. **错误处理**

   - 优雅处理速率限制
   - 带退避的自动重试
   - 详细的错误报告

---

## 5. `CrawlResult` 输出

每次 `arun()` 返回一个 **`CrawlResult`** 包含：

- `url`: 最终URL（若发生重定向）。
- `html`: 原始HTML。
- `cleaned_html`: 清理后的HTML。
- `markdown_v2`: 已弃用。改用常规 `markdown`
- `extracted_content`: 若使用提取策略（CSS/LLM策略的JSON结果）。
- `screenshot`, `pdf`: 如请求了截图/PDF。
- `media`, `links`: 发现的图片/链接信息。
- `success`, `error_message`: 状态信息。

详见 [CrawlResult 文档](./crawl-result.md)。

---

## 6. 快速示例

以下是一个完整示例：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai import JsonCssExtractionStrategy
import json

async def main():
    # 1. 浏览器配置
    browser_cfg = BrowserConfig(
        browser_type="firefox",
        headless=False,
        verbose=True
    )

    # 2. 运行配置
    schema = {
        "name": "Articles",
        "baseSelector": "article.post",
        "fields": [
            {
                "name": "title", 
                "selector": "h2", 
                "type": "text"
            },
            {
                "name": "url", 
                "selector": "a", 
                "type": "attribute", 
                "attribute": "href"
            }
        ]
    }

    run_cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(schema),
        word_count_threshold=15,
        remove_overlay_elements=True,
        wait_for="css:.post"  # 等待文章出现
    )

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(
            url="https://example.com/blog",
            config=run_cfg
        )

        if result.success:
            print("清理后HTML长度:", len(result.cleaned_html))
            if result.extracted_content:
                articles = json.loads(result.extracted_content)
                print("提取的文章:", articles[:2])
        else:
            print("错误:", result.error_message)

asyncio.run(main())
```

**说明**：

- 定义 **`BrowserConfig`** 使用 Firefox，非无头模式，`verbose=True`。  
- 定义 **`CrawlerRunConfig`** **绕过缓存**，使用 **CSS** 提取模式，设置 `word_count_threshold=15` 等。  
- 将它们分别传递给 `AsyncWebCrawler(config=...)` 和 `arun(url=..., config=...)`。

---

## 7. 最佳实践 & 迁移说明

1. **使用** `BrowserConfig` 配置浏览器**全局**环境。  
2. **使用** `CrawlerRunConfig` 配置**每次爬取**的逻辑（缓存、内容过滤、提取策略、等待条件）。  
3. **避免**在 `arun()` 中直接使用遗留参数如 `css_selector` 或 `word_count_threshold`。 改为：

   ```python
   run_cfg = CrawlerRunConfig(css_selector=".main-content", word_count_threshold=20)
   result = await crawler.arun(url="...", config=run_cfg)
   ```

4. 除非需要跨多次调用保持爬虫持久化，否则推荐使用**上下文管理器**。

---

## 8. 总结

**AsyncWebCrawler** 是异步爬取的入口：

- **构造函数**接受 **`BrowserConfig`**（或使用默认值）。  
- **`arun(url, config=CrawlerRunConfig)`** 是单页面爬取的主方法。  
- **`arun_many(urls, config=CrawlerRunConfig)`** 处理多URL并发爬取。  
- 如需高级生命周期控制，可显式使用 `start()` 和 `close()`。  

**迁移指南**：  

- 若曾使用 `AsyncWebCrawler(browser_type="chromium", css_selector="...")`，请将浏览器设置移至 `BrowserConfig(...)`，内容/爬取逻辑移至 `CrawlerRunConfig(...)`。

这种模块化设计确保代码**清晰**、**可扩展**且**易于维护**。 其他高级或罕见参数请参阅 [BrowserConfig 文档](../api/parameters.md)。