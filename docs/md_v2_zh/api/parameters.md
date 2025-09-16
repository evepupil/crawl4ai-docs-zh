# 1. **BrowserConfig** – 控制浏览器

`BrowserConfig` 专注于浏览器**如何**启动和运行。包括无头模式、代理、用户代理和其他环境调整。

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig

browser_cfg = BrowserConfig(
    browser_type="chromium",
    headless=True,
    viewport_width=1280,
    viewport_height=720,
    proxy="http://user:pass@proxy:8080",
    user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/116.0.0.0 Safari/537.36",
)
```

## 1.1 参数亮点

| **参数**                 | **类型 / 默认值**                      | **功能说明**                                                                                                                     |
|--------------------------|----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| **`browser_type`**       | `"chromium"`, `"firefox"`, `"webkit"`<br/>*(默认: `"chromium"`)* | 使用哪个浏览器引擎。`"chromium"` 适用于许多站点，`"firefox"` 或 `"webkit"` 用于专项测试。                 |
| **`headless`**           | `bool` (默认: `True`)               | 无头模式意味着没有可见的 UI。`False` 便于调试。                                                                         |
| **`viewport_width`**     | `int` (默认: `1080`)                | 初始页面宽度（像素）。对测试响应式布局很有用。                                                                    |
| **`viewport_height`**    | `int` (默认: `600`)                 | 初始页面高度（像素）。                                                                                                          |
| **`proxy`**              | `str` (默认: `None`)                | 单代理 URL，如果你希望所有流量都通过它，例如 `"http://user:pass@proxy:8080"`。                                      |
| **`proxy_config`**       | `dict` (默认: `None`)               | 用于高级或多代理需求，指定详细信息如 `{"server": "...", "username": "...", ...}`。                                  |
| **`use_persistent_context`** | `bool` (默认: `False`)       | 如果为 `True`，使用**持久化**浏览器上下文（跨运行保留 cookies、会话）。同时设置 `use_managed_browser=True`。          |
| **`user_data_dir`**      | `str or None` (默认: `None`)        | 存储用户数据（配置文件、cookies）的目录。如果要永久会话，必须设置此项。                                         |
| **`ignore_https_errors`** | `bool` (默认: `True`)           | 如果为 `True`，即使证书无效也继续（在开发/预发布环境中常见）。                                                            |
| **`java_script_enabled`** | `bool` (默认: `True`)           | 如果不需要 JS 开销或只需要静态内容，则禁用。                                                              |
| **`cookies`**            | `list` (默认: `[]`)                 | 预设 cookies，每个都是一个字典，如 `{"name": "session", "value": "...", "url": "..."}`。                                                |
| **`headers`**            | `dict` (默认: `{}`)                 | 为每个请求添加额外的 HTTP 头，例如 `{"Accept-Language": "en-US"}`。                                                            |
| **`user_agent`**         | `str` (默认: 基于 Chrome 的 UA)       | 你的自定义或随机用户代理。`user_agent_mode="random"` 可以随机更换。                                                          |
| **`light_mode`**         | `bool` (默认: `False`)              | 禁用一些后台功能以提高性能。                                                                              |
| **`text_mode`**          | `bool` (默认: `False`)              | 如果为 `True`，尝试禁用图像/其他繁重内容以提高速度。                                                                     |
| **`use_managed_browser`** | `bool` (默认: `False`)          | 用于高级“托管”交互（调试、CDP 使用）。如果启用了持久化上下文，通常会自动设置。                  |
| **`extra_args`**         | `list` (默认: `[]`)                 | 底层浏览器进程的额外标志，例如 `["--disable-extensions"]`。                                                |

**提示**:
- 设置 `headless=False` 以可视化**调试**页面加载方式或交互过程。  
- 如果需要**认证**存储或重复会话，考虑 `use_persistent_context=True` 并指定 `user_data_dir`。  
- 对于大型页面，可能需要更大的 `viewport_width` 和 `viewport_height` 来处理动态内容。

---

# 2. **CrawlerRunConfig** – 控制每次爬取

`BrowserConfig` 设置了**环境**，而 `CrawlerRunConfig` 详细说明了每次**爬取操作**应如何行为：缓存、内容过滤、链接或域名阻止、超时、JavaScript 代码等。

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

run_cfg = CrawlerRunConfig(
    wait_for="css:.main-content",
    word_count_threshold=15,
    excluded_tags=["nav", "footer"],
    exclude_external_links=True,
    stream=True,  # 为 arun_many() 启用流式处理
)
```

## 2.1 参数亮点

我们按类别分组。

### A) **内容处理**

| **参数**                | **类型 / 默认值**                   | **功能说明**                                                                                |
|------------------------------|--------------------------------------|-------------------------------------------------------------------------------------------------|
| **`word_count_threshold`**   | `int` (默认: ~200)                | 跳过少于 X 词的文本块。有助于忽略琐碎部分。                                 |
| **`extraction_strategy`**    | `ExtractionStrategy` (默认: None) | 如果设置，则提取结构化数据（基于 CSS、基于 LLM 等）。                                  |
| **`markdown_generator`**     | `MarkdownGenerationStrategy` (None)  | 如果你想要专门的 markdown 输出（引用、过滤、分块等）。可以使用 `content_source` 等选项进行自定义，以选择 HTML 输入源（'cleaned_html'、'raw_html' 或 'fit_html'）。                 |
| **`css_selector`**           | `str` (None)                         | 仅保留页面中与此选择器匹配的部分。影响整个提取过程。 |
| **`target_elements`**        | `List[str]` (None)                   | 用于专注于 markdown 生成和数据提取的元素的 CSS 选择器列表，同时仍处理整个页面的链接、媒体等。比 `css_selector` 提供更大的灵活性。 |
| **`excluded_tags`**          | `list` (None)                        | 移除整个标签（例如 `["script", "style"]`）。                                               |
| **`excluded_selector`**      | `str` (None)                         | 类似于 `css_selector`，但用于排除。例如 `"#ads, .tracker"`。                                    |
| **`only_text`**              | `bool` (False)                       | 如果为 `True`，尝试仅提取纯文本内容。                                                  |
| **`prettiify`**              | `bool` (False)                       | 如果为 `True`，美化最终 HTML（速度较慢，纯属美观）。                                      |
| **`keep_data_attributes`**   | `bool` (False)                       | 如果为 `True`，在清理后的 HTML 中保留 `data-*` 属性。                                         |
| **`remove_forms`**           | `bool` (False)                       | 如果为 `True`，移除所有 `<form>` 元素。                                                        |

---

### B) **缓存和会话**

| **参数**           | **类型 / 默认值**     | **功能说明**                                                                                                              |
|-------------------------|------------------------|------------------------------------------------------------------------------------------------------------------------------|
| **`cache_mode`**        | `CacheMode or None`    | 控制缓存处理方式（`ENABLED`、`BYPASS`、`DISABLED` 等）。如果为 `None`，通常默认为 `ENABLED`。          |
| **`session_id`**        | `str or None`          | 分配唯一 ID 以在多个 `arun()` 调用中重用单个浏览器会话。                                          |
| **`bypass_cache`**      | `bool` (False)         | 如果为 `True`，行为类似于 `CacheMode.BYPASS`。                                                                                     |
| **`disable_cache`**     | `bool` (False)         | 如果为 `True`，行为类似于 `CacheMode.DISABLED`。                                                                                   |
| **`no_cache_read`**     | `bool` (False)         | 如果为 `True`，行为类似于 `CacheMode.WRITE_ONLY`（写入缓存但从不读取）。                                                  |
| **`no_cache_write`**    | `bool` (False)         | 如果为 `True`，行为类似于 `CacheMode.READ_ONLY`（读取缓存但从不写入）。                                                   |

使用这些来控制是否从本地内容缓存读取或写入。对于大批量爬取或重复访问站点非常方便。

---

### C) **页面导航和计时**

| **参数**              | **类型 / 默认值**      | **功能说明**                                                                                                    |
|----------------------------|-------------------------|----------------------------------------------------------------------------------------------------------------------|
| **`wait_until`**           | `str` (domcontentloaded)| 导航“完成”的条件。通常是 `"networkidle"` 或 `"domcontentloaded"`。                               |
| **`page_timeout`**         | `int` (60000 ms)        | 页面导航或 JS 步骤的超时时间。对于慢速站点增加此值。                                                    |
| **`wait_for`**             | `str or None`           | 在内容提取之前等待 CSS（`"css:selector"`）或 JS（`"js:() => bool"`）条件。                     |
| **`wait_for_images`**      | `bool` (False)          | 在完成之前等待图像加载。如果你只需要文本，会减慢速度。                                          |
| **`delay_before_return_html`** | `float` (0.1)       | 在最终 HTML 捕获之前的额外暂停（秒）。对最后一刻的更新很有用。                               |
| **`check_robots_txt`**     | `bool` (False)          | 是否在爬取前检查并遵守 robots.txt 规则。如果为 True，则缓存 robots.txt 以提高效率。            |
| **`mean_delay`** 和 **`max_range`** | `float` (0.1, 0.3) | 如果你调用 `arun_many()`，这些定义了爬取之间的随机延迟间隔，有助于避免检测或速率限制。 |
| **`semaphore_count`**      | `int` (5)               | `arun_many()` 的最大并发数。如果你有资源进行并行爬取，则增加此值。                                |

---

### D) **页面交互**

| **参数**              | **类型 / 默认值**            | **功能说明**                                                                                                                       |
|----------------------------|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| **`js_code`**              | `str or list[str]` (None)      | 加载后运行的 JavaScript。例如 `"document.querySelector('button')?.click();"`。                                                     |
| **`js_only`**              | `bool` (False)                 | 如果为 `True`，表示我们正在重用现有会话并仅应用 JS。不完整重新加载。                                           |
| **`ignore_body_visibility`** | `bool` (True)                | 跳过检查 `<body>` 是否可见。通常最好保持 `True`。                                                                     |
| **`scan_full_page`**       | `bool` (False)                 | 如果为 `True`，自动滚动页面以加载动态内容（无限滚动）。                                                              |
| **`scroll_delay`**         | `float` (0.2)                  | 如果 `scan_full_page=True`，滚动步骤之间的延迟。                                                                                   |
| **`process_iframes`**      | `bool` (False)                 | 将 iframe 内容内联以进行单页提取。                                                                                     |
| **`remove_overlay_elements`** | `bool` (False)              | 移除可能阻挡主要内容的模态框/弹出窗口。                                                                              |
| **`simulate_user`**        | `bool` (False)                 | 模拟用户交互（鼠标移动）以避免机器人检测。                                                                    |
| **`override_navigator`**   | `bool` (极速模式)                 | 在 JS 中覆盖 `navigator` 属性以进行隐身。                                                                                      |
| **`magic`**                | `bool` (False)                 | 自动处理弹出窗口/同意横幅。实验性功能。                                                                             |
| **`adjust_viewport_to_content`** | `bool` (False)           | 调整视口大小以匹配页面内容高度。                                                                                          |

如果你的页面是具有重复 JS 更新的单页应用程序，则在后续调用中设置 `js_only=True`，并为重用同一标签页设置 `session_id`。

---

### E) **媒体处理**

| **参数**                              | **类型 / 默认值**  | **功能说明**                                                                                         |
|--------------------------------------------|---------------------|-----------------------------------------------------------------------------------------------------------|
| **`screenshot`**                           | `极速模式` (False)      | 在 `result.screenshot` 中捕获屏幕截图（base64）。                                                     |
| **`screenshot_wait_for`**                  | `float or None`     | 屏幕截图前的额外等待时间。                                                                    |
| **`screenshot_height_threshold`**          | `int` (~20000)      | 如果页面高于此值，则使用备用屏幕截图策略。                                |
| **`pdf`**                                  | `bool` (False)      | 如果为 `True`，在 `result.pdf` 中返回 PDF。                                                                 |
| **`capture_mhtml`**                        | `bool` (False)      | 如果为 `True`，在 `result.mhtml` 中捕获页面的 MHTML 快照。MHTML 包括所有页面资源（CSS、图像等）在一个文件中。 |
| **极速模式** | `int` (~50)         | 图像 alt 文本或描述被视为有效的最小词数。                              |
| **`image_score_threshold`**                | `int` (~3)          | 过滤掉低分图像。爬虫根据相关性（大小、上下文等）对图像进行评分。              |
| **`exclude_external_images`**              | `bool` (False)      | 排除来自其他域的图像。                                                                        |

---

### F) **链接/域名处理**

| **参数**                | **类型 / 默认值**      | **功能说明**                                                                                                             |
|------------------------------|-------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **`exclude_social_media_domains`** | `list` (例如 Facebook/Twitter) | 可以扩展的默认列表。任何指向这些域的链接将从最终输出中移除。                                      |
| **`exclude_external_links`** | `bool` (False)          | 移除所有指向当前域之外的链接。                                                                      |
| **`exclude_social_media_links`** | `bool` (False)      | 特别移除指向社交站点（如 Facebook 或 Twitter）的链接。                                                      |
| **`极速模式`**        | `list` ([])             | 提供要排除的自定义域列表（如 `["ads.com", "trackers.io"]`）。                                            |

使用这些进行链接级内容过滤（通常是为了保持爬取“内部”或移除垃圾域）。

---

### G) **调试和日志记录**

| **参数**  | **类型 / 默认值** | **功能说明**                                                         |
|----------------|--------------------|---------------------------------------------------------------------------|
| **`verbose`**  | `bool` (True)     | 打印详细说明爬取、交互或错误每个步骤的日志。    |
| **`log_console`** | `bool` (False) | 如果你想要更深入的 JS 调试，则记录页面的 JavaScript 控制台输出。|

---


### H) **虚拟滚动配置**

| **参数**                | **类型 / 默认值**           | **功能说明**                                                                                                                    |
|------------------------------|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| **`virtual_scroll_config`**  | `VirtualScrollConfig or dict` (None) | 用于处理像 Twitter/Instagram 这样使用虚拟滚动的站点的配置，这些站点在滚动时内容被替换而不是追加。 |

当站点使用虚拟滚动（内容在滚动时被替换）时，使用 `VirtualScrollConfig`：

```python
from crawl4ai import VirtualScrollConfig

virtual_config = VirtualScrollConfig(
    container_selector="#timeline",    # 可滚动容器的 CSS 选择器
    scroll_count=30,                   # 滚动次数
    scroll_by="container_height",      # 滚动量："container_height"、"page_height" 或像素（例如 500）
    wait_after_scroll=0.5             # 每次滚动后等待内容加载的秒数
)

config = CrawlerRunConfig(
    virtual_scroll_config=virtual_config
)
```

**VirtualScrollConfig 参数:**

| **参数**          | **类型 / 默认值**        | **功能说明**                                                                          |
|------------------------|---------------------------|-------------------------------------------------------------------------------------------|
| **`container_selector`** | `str` (必需)        | 可滚动容器的 CSS 选择器（例如，`"#feed"`、`".timeline"`）。              |
| **`scroll_count`**     | `极速模式` (10)               | 执行的最大滚动次数                                                      |
| **`scroll_by`**        | `str or int` ("container_height") | 滚动量：`"container_height"`、`"page_height"` 或像素（例如，`500`）。   |
| **`wait_after_scroll`** | `float` (0.5)           | 每次滚动后等待新内容加载的时间（秒）。                        |

**何时使用虚拟滚动 vs scan_full_page:**
- 当内容在滚动过程中被**替换**时使用 `virtual_scroll_config`（Twitter、Instagram）
- 当内容在滚动过程中被**追加**时使用 `scan_full_page`（传统的无限滚动）

有关详细示例，请参阅[虚拟滚动文档](../../advanced/virtual-scroll.md)。

---

### I) **URL 匹配配置**

| **参数**          | **类型 / 默认值**           | **功能说明**                                                                                                                    |
|------------------------|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| **`url_matcher`**      | `UrlMatcher` (None)          | 用于匹配 URL 的模式。可以是：字符串（glob）、函数或混合类型的列表。**None 表示匹配所有 URL**。         |
| **`match_mode`**       | `MatchMode` (MatchMode.OR)   | 如何组合列表中的多个匹配器：`MatchMode.OR`（任意匹配）或 `MatchMode.AND`（全部必须匹配）。                       |

`url_matcher` 参数在与 `arun_many()` 一起使用时启用特定于 URL 的配置：

```python
from crawl4ai import CrawlerRunConfig, MatchMode
from crawl极速模式.processors.pdf import PDFContentScrapingStrategy
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

# 简单字符串模式（glob 风格）
pdf_config = Crawler极速模式(
    url_matcher="*.pdf",
    scraping_strategy=PDFContentScrapingStrategy()
)

# 使用 OR 逻辑的多个模式（默认）
blog_config = CrawlerRunConfig(
    url_matcher=["*/blog/*", "*/article/*", "*/news/*"],
    match_mode=MatchMode.OR  # 任意模式匹配
)

# 函数匹配器
api_config = CrawlerRunConfig(
    url_matcher=lambda url: 'api' in url or url.endswith('.json'),
    # 其他设置如 extraction_strategy
)

# 混合：字符串 + 函数，使用 AND 逻辑
complex_config = CrawlerRunConfig(
    url_matcher=[
        lambda url: url.startswith('https://'),  # 必须是 HTTPS
        "*.org/*",                               # 必须是 .org 域
        lambda url: 'docs' in url                # 必须包含 'docs'
    ],
    match_mode=MatchMode.AND  # 所有条件必须匹配
)

# 使用 AND 逻辑组合模式和函数
secure_docs = CrawlerRunConfig(
    url_matcher=["https://*", lambda url: '.doc' in url],
    match_mode=MatchMode.AND  # 必须是 HTTPS 且包含 .doc
)

# 默认配置 - 匹配所有 URL
default_config = CrawlerRunConfig()  # 未设置 url_matcher = 匹配所有内容
```

**UrlMatcher 类型:**
- **None (默认)**: 当 `url_matcher` 为 None 或未设置时，配置匹配所有 URL
- **字符串模式**: Glob 风格模式，如 `"*.pdf"`、`"*/api/*"`、`"https://*.example.com/*"`
- **函数**: `lambda url: bool` - 用于复杂匹配的自定义逻辑
- **列表**: 混合字符串和函数，使用 `MatchMode.OR` 或 `MatchMode.AND` 组合

**重要行为:**
- 当将配置列表传递给 `arun_many()` 时，URL 会按顺序与每个配置的 `url_matcher` 匹配。第一个匹配项胜出！
- 如果没有配置匹配 URL 并且没有默认配置（没有 `url_matcher` 的配置），URL 将失败并显示“未找到匹配的配置”
- 如果要处理所有 URL，请始终将默认配置作为最后一项包含

---## 2.2 辅助方法

`BrowserConfig` 和 `CrawlerRunConfig` 都提供了一个 `clone()` 方法来创建修改后的副本：

```python
# 创建基础配置
base_config = CrawlerRunConfig(
    cache_mode=CacheMode.ENABLED,
    word_count_threshold=200
)

# 使用 clone() 创建变体
stream_config = base_config.clone(stream=True)
no_cache_config = base_config.clone(
    cache_mode=CacheMode.BYPASS,
    stream=True
)
```

当你需要为不同用例使用稍有不同的配置而不修改原始配置时，`clone()` 方法特别有用。

## 2.3 使用示例

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def main():
    # 配置浏览器
    browser_cfg = BrowserConfig(
        headless=False,
        viewport_width=1280,
        viewport_height=720,
        proxy="极速模式://user:pass@myproxy:8080",
        text_mode=True
    )

    # 配置运行
    run_cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        session_id="my_session",
        css_selector="main.article",
        excluded_tags=["script", "style"],
        exclude_external_links=True,
        wait_for="css:.article-loaded",
        screenshot=True,
        stream=True
    )

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(
            url="https://example.com/news",
            config=run_cfg
        )
        if result.success:
            print("最终 cleaned_html 长度:", len(result.cleaned_html))
            if result.screenshot:
                print("已捕获屏幕截图 (base64, 长度):", len(result.screenshot))
        else:
            print("爬取失败:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
```

## 2.4 合规性和道德

| **参数**          | **类型 / 默认值**      | **功能说明**                                                                                                    |
|-----------------------|-------------------------|----------------------------------------------------------------------------------------------------------------------|
| **`check_robots_txt`**| `bool` (False)          | 当为 True 时，在爬取前检查并遵守 robots.txt 规则。使用高效的 SQLite 后端进行缓存。          |
| **`user_agent`**      | `str` (None)            | 用于标识你的爬虫的用户代理字符串。启用 robots.txt 检查时使用。                                |

```python
run_config = CrawlerRunConfig(
    check_robots_txt=True,  # 启用 robots.txt 合规性
    user_agent="MyBot/1.0"  # 标识你的爬虫
)
```

# 3. **LLMConfig** - 设置 LLM 提供商
LLMConfig 用于将 LLM 提供商配置传递给依赖 LLM 进行提取、过滤、模式生成等的策略和函数。目前可用于以下场景 -

1. LLMExtractionStrategy
2. LLMContentFilter
3. JsonCssExtractionStrategy.generate_schema
4. JsonXPathExtractionStrategy.generate_schema

## 3.1 参数
| **参数**         | **类型 / 默认值**                     | **功能说明**                                                                                                                     |
|-----------------------|----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| **`provider`**    | `"ollama/llama3","groq/llama3-70b-8192","groq/llama3-8b-8192", "openai/gpt-4o-mini" ,"openai/gpt-4o","openai/o1-mini","openai/o1-preview","openai/o3-min极速模式","openai/o3-mini-high","anthropic/claude-3-haiku-20240307","anthropic/claude-3-opus-20240229","anthropic/claude-3-sonnet-20240229","anthropic/claude-3-5-sonnet-20240620","gemini/gemini-pro","gemini/gemini-1.5-pro","gemini/gemini-2.0-flash","gemini/gemini-2.0-flash-exp","gemini/gemini-2.0-flash-lite-preview-02-05","deepseek/deepseek-chat"`<br/>*(默认: `"openai/gpt-4o-mini"`)* | 使用哪个 LLM 提供商。 
| **`api_token`**         |1.可选。当未明确提供时，api_token 将根据提供商从环境变量中读取。例如：如果传递了 gemini 模型作为提供商，则将从环境变量中读取 `"GEMINI_API_KEY"`  <br/> 2. LLM 提供商的 API 令牌 <br/> 例如：`api_token = "gsk_1ClHGGJ7Lpn4WGybR7vNWGdyb3FY7zXEw3SCiy0BAVM9lL8CQv"` <br/> 3. 环境变量 - 与前缀 "env:" 一起使用 <br/> 例如：`api_token = "env: GROQ_API_KEY"`              | 用于给定提供商的 API 令牌 
| **`base_url`**         |可选。自定义 API 端点 | 如果你的提供商有自定义端点

## 3.2 使用示例
```python
llm_config = LLMConfig(provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY"))
```

## 4. 综合运用

- **使用** `BrowserConfig` 进行**全局**浏览器设置：引擎、无头模式、代理、用户代理。  
- **使用** `CrawlerRunConfig` 进行每次爬取的**上下文**：如何过滤内容、处理缓存、等待动态元素或运行 JS。  
- **将**两个配置都传递给 `AsyncWebCrawler`（`BrowserConfig`），然后传递给 `arun()`（`CrawlerRunConfig`）。  
- **使用** `LLMConfig` 用于可在所有提取、过滤、模式生成任务中使用的 LLM 提供商配置。可用于 - `LLMExtractionStrategy`、`LLMContentFilter`、`JsonCssExtractionStrategy.generate_schema` 和 `JsonXPathExtractionStrategy.generate_schema`

```python
# 使用 clone() 方法创建修改后的副本
stream_cfg = run_cfg.clone(
    stream=True,
    cache_mode=CacheMode.BYPASS
)
```