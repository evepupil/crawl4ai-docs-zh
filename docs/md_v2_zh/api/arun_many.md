# `arun_many(...)` 参考文档

> **注意**：此函数与 [`arun()`](./arun.md) 非常相似，但专注于**并发**或**批量**爬取。如果您不熟悉 `arun()` 的用法，请先阅读该文档，然后再查看本文了解差异。

## 函数签名

```python
async def arun_many(
    urls: Union[List[str], List[Any]],
    config: Optional[Union[CrawlerRunConfig, List[CrawlerRunConfig]]] = None,
    dispatcher: Optional[BaseDispatcher] = None,
    ...
) -> Union[List[CrawlResult], AsyncGenerator[CrawlResult, None]]:
    """
    并发或批量爬取多个URL。

    :param urls: 要爬取的URL（或任务）列表。
    :param config: (可选) 可以是：
        - 适用于所有URL的单个 `CrawlerRunConfig`
        - 带有url_matcher模式的 `CrawlerRunConfig` 对象列表
    :param dispatcher: (可选) 并发控制器（例如 MemoryAdaptiveDispatcher）。
    ...
    :return: 返回 `CrawlResult` 对象列表，如果启用流式处理则返回异步生成器。
    """
```

## 与 `arun()` 的区别

1. **多URL处理**：  
   
   - 不再爬取单个URL，而是传入URL列表（字符串或任务）。  
   - 函数返回 `CrawlResult` 的**列表**，如果启用流式处理则返回**异步生成器**。

2. **并发与调度器**：  

   - **`dispatcher`** 参数允许高级并发控制。  
   - 如果省略，内部会使用默认调度器（如 `MemoryAdaptiveDispatcher`）。  
   - 调度器处理并发、速率限制和基于内存的自适应节流（参见[多URL爬取](../advanced/multi-url-crawling.md)）。

3. **流式支持**：  

   - 在 `CrawlerRunConfig` 中设置 `stream=True` 启用流式处理。
   - 使用 `async for` 按结果可用性逐步处理。
   - 适合处理大量URL而无需等待全部完成。

4. **并行执行**：  

   - `arun_many()` 可以在底层并发执行多个请求。  
   - 每个 `CrawlResult` 可能包含**`dispatch_result`**，记录并发细节（如内存使用、开始/结束时间）。

### 基础示例（批量模式）

```python
# 最简用法：使用默认调度器
results = await crawler.arun_many(
    urls=["https://site1.com", "https://site2.com"],
    config=CrawlerRunConfig(stream=False)  # 默认行为
)

for res in results:
    if res.success:
        print(res.url, "爬取成功！")
    else:
        print("失败:", res.url, "-", res.error_message)
```

### 流式示例

```python
config = CrawlerRunConfig(
    stream=True,  # 启用流式模式
    cache_mode=CacheMode.BYPASS
)

# 按完成顺序处理结果
async for result in await crawler.arun_many(
    urls=["https://site1.com", "https://site2.com", "https://site3.com"],
    config=config
):
    if result.success:
        print(f"刚刚完成: {result.url}")
        # 立即处理每个结果
        process_result(result)
```

### 使用自定义调度器

```python
dispatcher = MemoryAdaptiveDispatcher(
    memory_threshold_percent=70.0,
    max_session_permit=10
)
results = await crawler.arun_many(
    urls=["https://site1.com", "https://site2.com", "https://site3.com"],
    config=my_run_config,
    dispatcher=dispatcher
)
```

### URL特定配置

通过 `url_matcher` 模式提供配置列表，而非全局统一配置：

```python
from crawl4ai import CrawlerRunConfig, MatchMode
from crawl4ai.processors.pdf import PDFContentScrapingStrategy
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

# PDF文件 - 专用提取策略
pdf_config = CrawlerRunConfig(
    url_matcher="*.pdf",
    scraping_strategy=PDFContentScrapingStrategy()
)

# 博客/文章页面 - 内容过滤
blog_config = CrawlerRunConfig(
    url_matcher=["*/blog/*", "*/article/*", "*python.org*"],
    markdown_generator=DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=0.48)
    )
)

# 动态页面 - JavaScript执行
github_config = CrawlerRunConfig(
    url_matcher=lambda url: 'github.com' in url,
    js_code="window.scrollTo(0, 500);"
)

# API端点 - JSON提取
api_config = CrawlerRunConfig(
    url_matcher=lambda url: 'api' in url or url.endswith('.json'),
    # JSON提取的自定义设置
)

# 默认回退配置
default_config = CrawlerRunConfig()  # 无url_matcher表示仅作为回退配置

# 传入配置列表 - 首次匹配生效！
results = await crawler.arun_many(
    urls=[
        "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",  # → pdf_config
        "https://blog.python.org/",  # → blog_config
        "https://github.com/microsoft/playwright",  # → github_config
        "https://httpbin.org/json",  # → api_config
        "https://example.com/"  # → default_config
    ],
    config=[pdf_config, blog_config, github_config, api_config, default_config]
)
```

**URL匹配特性**：
- **字符串模式**：`"*.pdf"`、`"*/blog/*"`、`"*python.org*"`
- **函数匹配器**：`lambda url: 'api' in url`
- **混合模式**：使用 `MatchMode.OR` 或 `MatchMode.AND` 组合字符串和函数
- **首次匹配优先**：按顺序评估配置

**关键点**：
- 根据调度器策略，每个URL可能由相同或独立的会话处理。
- 每个 `CrawlResult` 中的 `dispatch_result`（如果使用并发）可能包含内存和时间信息。  
- 如需处理认证或会话ID，请在单个任务或运行配置中传递。
- **重要**：如需处理所有URL，请始终在最后包含无 `url_matcher` 的默认配置，否则未匹配的URL将失败。

### 返回值

返回 [`CrawlResult`](./crawl-result.md) 对象**列表**，如果启用流式处理则返回**异步生成器**。可通过迭代检查 `result.success` 或读取每个项的 `extracted_content`、`markdown` 或 `dispatch_result`。

---

## 调度器参考

- **`MemoryAdaptiveDispatcher`**：根据系统内存使用动态管理并发。  
- **`SemaphoreDispatcher`**：固定并发限制，更简单但缺乏自适应性。  

高级用法或自定义设置参见[使用调度器进行多URL爬取](../advanced/multi-url-crawling.md)。

---

## 常见问题

1. **大型列表**：传入数千个URL时，注意内存或速率限制。调度器可辅助管理。  

2. **会话复用**：如需专用登录或持久上下文，请确保调度器或任务正确处理会话。  

3. **错误处理**：每个 `CrawlResult` 可能因不同原因失败——处理前务必检查 `result.success` 或 `error_message`。

---

## 总结

当需要**同时爬取多个URL**或以受控并行任务爬取时，使用 `arun_many()`。如需高级并发功能（如基于内存的自适应节流或复杂速率限制），请提供**调度器**。每个结果都是标准 `CrawlResult`，可能附加并发统计信息（`dispatch_result`）供深度检查。更多并发逻辑和调度器细节，参见[高级多URL爬取](../advanced/multi-url-crawling.md)文档。