# `arun()` 参数指南（新方法）

在 Crawl4AI 的**最新**配置模型中，几乎所有原本直接传入 `arun()` 的参数现在都归属于 **`CrawlerRunConfig`**。调用 `arun()` 时，你需要提供：

```python
await crawler.arun(
    url="https://example.com",  
    config=my_run_config
)
```

以下是按功能区域分类的 `CrawlerRunConfig` 参数整理。关于**浏览器**设置（如 `headless`、`browser_type`），请参阅 [BrowserConfig](./parameters.md)。

---

## 1. 核心用法

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

async def main():
    run_config = CrawlerRunConfig(
        verbose=True,            # 详细日志记录
        cache_mode=CacheMode.ENABLED,  # 使用正常读写缓存
        check_robots_txt=True,   # 遵守 robots.txt 规则
        # ... 其他参数
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://example.com",
            config=run_config
        )
        
        # 检查是否被 robots.txt 阻止
        if not result.success and result.status_code == 403:
            print(f"Error: {result.error_message}")
```

**关键字段**：
- `verbose=True` 记录每个爬取步骤的日志。  
- `cache_mode` 决定如何读写本地爬取缓存。

---

## 2. 缓存控制

**`cache_mode`**（默认：`CacheMode.ENABLED`）  
使用 `CacheMode` 的内置枚举：

- `ENABLED`：正常缓存——如果可用则读取，如果缺失则写入。
- `DISABLED`：禁用缓存——始终重新获取页面。
- `READ_ONLY`：仅从缓存读取；不写入新数据。
- `WRITE_ONLY`：写入缓存但不读取现有数据。
- `BYPASS`：跳过读取缓存（但仍可能根据设置写入）。

```python
run_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS
)
```

**附加标志**：

- `bypass_cache=True` 等同于 `CacheMode.BYPASS`。
- `disable_cache=True` 等同于 `CacheMode.DISABLED`。
- `no_cache_read=True` 等同于 `CacheMode.WRITE_ONLY`。
- `no_cache_write=True` 等同于 `CacheMode.READ_ONLY`。

---

## 3. 内容处理与选择

### 3.1 文本处理

```python
run_config = CrawlerRunConfig(
    word_count_threshold=10,   # 忽略少于 10 个单词的文本块
    only_text=False,           # 如果为 True，尝试移除非文本元素
    keep_data_attributes=False # 保留或丢弃 data-* 属性
)
```

### 3.2 内容选择

```python
run_config = CrawlerRunConfig(
    css_selector=".main-content",  # 仅关注 .main-content 区域
    excluded_tags=["form", "nav"], # 移除整个标签块
    remove_forms=True,             # 专门移除 <form> 元素
    remove_overlay_elements=True,  # 尝试移除模态框/弹窗
)
```

### 3.3 链接处理

```python
run_config = CrawlerRunConfig(
    exclude_external_links=True,         # 从最终内容中移除外部链接
    exclude_social_media_links=True,     # 移除已知社交媒体链接
    exclude_domains=["ads.example.com"], # 排除指向这些域的链接
    exclude_social_media_domains=["facebook.com","twitter.com"], # 扩展默认列表
)
```

### 3.4 媒体过滤

```python
run_config = CrawlerRunConfig(
    exclude_external_images=True  # 移除来自其他域的图片
)
```

---

## 4. 页面导航与计时

### 4.1 基本浏览器流程

```python
run_config = CrawlerRunConfig(
    wait_for="css:.dynamic-content", # 等待 .dynamic-content 出现
    delay_before_return_html=2.0,    # 捕获最终 HTML 前等待 2 秒
    page_timeout=60000,             # 导航和脚本超时（毫秒）
)
```

**关键字段**：

- `wait_for`：  
  - `"css:selector"` 或  
  - `"js:() => boolean"`  
  例如：`js:() => document.querySelectorAll('.item').length > 10`。

- `mean_delay` 和 `max_range`：定义 `arun_many()` 调用的随机延迟。  
- `semaphore_count`：爬取多个 URL 时的并发限制。

### 4.2 JavaScript 执行

```python
run_config = CrawlerRunConfig(
    js_code=[
        "window.scrollTo(0, document.body.scrollHeight);",
        "document.querySelector('.load-more')?.click();"
    ],
    js_only=False
)
```

- `js_code` 可以是单个字符串或字符串列表。  
- `js_only=True` 表示“我在同一会话中继续执行新的 JS 步骤，不进行新的完整导航”。

### 4.3 反爬虫

```python
run_config = CrawlerRunConfig(
    magic=True,
    simulate_user=True,
    override_navigator=True
)
```
- `magic=True` 尝试多种隐身功能。  
- `simulate_user=True` 模拟鼠标移动或随机延迟。  
- `override_navigator=True` 伪造一些 navigator 属性（如用户代理检查）。

---

## 5. 会话管理

**`session_id`**： 
```python
run_config = CrawlerRunConfig(
    session_id="my_session123"
)
```
如果在后续 `arun()` 调用中重复使用，将继续使用相同的标签页/页面上下文（适用于多步骤任务或有状态浏览）。

---

## 6. 截图、PDF 和媒体选项

```python
run_config = CrawlerRunConfig(
    screenshot=True,             # 获取 base64 格式的截图
    screenshot_wait_for=1.0,     # 捕获前等待 1 秒
    pdf=True,                    # 同时生成 PDF
    image_description_min_word_threshold=5,  # 分析 alt 文本时的最小单词阈值
    image_score_threshold=3,                # 过滤低分图片
)
```
**结果位置**：
- `result.screenshot` → base64 截图字符串。
- `result.pdf` → PDF 数据的字节数组。

---

## 7. 提取策略

**用于高级数据提取**（基于 CSS/LLM），设置 `extraction_strategy`：

```python
run_config = CrawlerRunConfig(
    extraction_strategy=my_css_or_llm_strategy
)
```

提取的数据将出现在 `result.extracted_content` 中。

---

## 8. 综合示例

以下是结合多个参数的代码片段：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai import JsonCssExtractionStrategy

async def main():
    # 示例 schema
    schema = {
        "name": "Articles",
        "baseSelector": "article.post",
        "fields": [
            {"name": "title", "selector": "h2", "type": "text"},
            {"name": "link",  "selector": "a",  "type": "attribute", "attribute": "href"}
        ]
    }

    run_config = CrawlerRunConfig(
        # 核心
        verbose=True,
        cache_mode=CacheMode.ENABLED,
        check_robots_txt=True,   # 遵守 robots.txt 规则
        
        # 内容
        word_count_threshold=10,
        css_selector="main.content",
        excluded_tags=["nav", "footer"],
        exclude_external_links=True,
        
        # 页面和 JS
        js_code="document.querySelector('.show-more')?.click();",
        wait_for="css:.loaded-block",
        page_timeout=30000,
        
        # 提取
        extraction_strategy=JsonCssExtractionStrategy(schema),
        
        # 会话
        session_id="persistent_session",
        
        # 媒体
        screenshot=True,
        pdf=True,
        
        # 反爬虫
        simulate_user=True,
        magic=True,
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com/posts", config=run_config)
        if result.success:
            print("HTML length:", len(result.cleaned_html))
            print("Extraction JSON:", result.extracted_content)
            if result.screenshot:
                print("Screenshot length:", len(result.screenshot))
            if result.pdf:
                print("PDF bytes length:", len(result.pdf))
        else:
            print("Error:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
```

**涵盖内容**：

1. 爬取主内容区域，忽略外部链接。  
2. 运行 JavaScript 点击“.show-more”。  
3. 等待“.loaded-block”出现。  
4. 生成最终页面的**截图**和**PDF**。  
5. 使用基于 **CSS** 的提取策略提取重复的“article.post”元素。

---

## 9. 最佳实践

1. 使用 `BrowserConfig` 配置**全局浏览器**设置（无头模式、用户代理）。  
2. 使用 `CrawlerRunConfig` 处理**特定**爬取需求：内容过滤、缓存、JS、截图、提取等。  
3. 保持运行配置中的**参数一致性**——尤其是在大型代码库中进行多次爬取时。  
4. 如果站点或系统无法处理，**限制**高并发（`semaphore_count`）。  
5. 对于动态页面，设置 `js_code` 或 `scan_full_page` 以确保加载所有内容。

---

## 10. 结论

所有原本作为 `arun()` 直接参数的配置现在都属于 **`CrawlerRunConfig`**。这种方法：

- 使代码**更清晰**、**更易维护**。  
- 减少关于哪些参数影响全局与每次爬取行为的混淆。  
- 允许为不同页面或任务创建**可重用**的配置对象。

如需**完整**参考，请查看 [CrawlerRunConfig 文档](./parameters.md)。 

祝您使用**结构化、灵活**的配置方法愉快爬取！