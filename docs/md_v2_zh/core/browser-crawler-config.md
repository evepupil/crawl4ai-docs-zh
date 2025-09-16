# 浏览器、爬虫与 LLM 配置（快速概览）

Crawl4AI 的灵活性源于两个关键类：

1. **`BrowserConfig`** – 控制浏览器**如何**启动和运行（例如，无头模式或可见模式、代理、用户代理）。  
2. **`CrawlerRunConfig`** – 控制每次**爬取**操作的**方式**（例如，缓存、提取、超时、要运行的 JavaScript 代码等）。  
3. **`LLMConfig`** - 控制 LLM 提供商的配置方式（模型、API 令牌、基础 URL、温度等）。

在大多数示例中，您为整个爬虫会话创建**一个** `BrowserConfig`，然后在每次调用 `arun()` 时传递一个**新的**或重复使用的 `CrawlerRunConfig`。本教程展示了最常用的参数。如果您需要高级或很少使用的字段，请参阅[配置参数](../api/parameters.md)。

---

## 1. BrowserConfig 要点

```python
class BrowserConfig:
    def __init__(
        browser_type="chromium",
        headless=True,
        proxy_config=None,
        viewport_width=1080,
        viewport_height=600,
        verbose=True,
        use_persistent_context=False,
        user_data_dir=None,
        cookies=None,
        headers=None,
        user_agent=None,
        text_mode=False,
        light_mode=False,
        extra_args=None,
        enable_stealth=False,
        # ... 此处省略了其他高级参数
    ):
        ...
```

### 需要注意的关键字段

1. **`browser_type`**  
- 选项：`"chromium"`、`"firefox"` 或 `"webkit"`。  
- 默认为 `"chromium"`。  
- 如果您需要不同的引擎，请在此处指定。

2. **`headless`**  
   - `True`：在无头模式下运行浏览器（不可见的浏览器）。  
   - `False`：在可见模式下运行浏览器，有助于调试。

3. **`proxy_config`**  
   - 一个包含如下字段的字典：  
```json
{
    "server": "http://proxy.example.com:8080", 
    "username": "...", 
    "password": "..."
}
```
   - 如果不需要代理，则保留为 `None`。

4. **`viewport_width` & `viewport_height`**:  
   - 初始窗口大小。  
   - 某些网站在较小或较大的视口下表现不同。

5. **`verbose`**:  
   - 如果为 `True`，则打印额外的日志。  
   - 便于调试。

6. **`use_persistent_context`**:  
   - 如果为 `True`，则使用**持久化**浏览器配置文件，跨运行存储 cookies/本地存储。  
   - 通常还需要设置 `user_data_dir` 指向一个文件夹。

7. **`cookies`** & **`headers`**:  
   - 如果您想从特定的 cookies 开始或添加通用的 HTTP 头，请在此处设置它们。  
   - 例如：`cookies=[{"name": "session", "value": "abc123", "domain": "example.com"}]`。

8. **`user_agent`**:  
   - 自定义 User-Agent 字符串。如果为 `None`，则使用默认值。  
   - 您也可以设置 `user_agent_mode="random"` 进行随机化（如果您想对抗机器人检测）。

9. **`text_mode`** & **`light_mode`**:  
   - `text_mode=True` 禁用图像，可能加速纯文本爬取。  
   - `light_mode=True` 为性能关闭某些后台功能。  

10. **`extra_args`**:  
    - 底层浏览器的附加标志。  
    - 例如：`["--disable-extensions"]`。

11. **`enable_stealth`**:  
    - 如果为 `True`，则使用 playwright-stealth 启用隐身模式。  
    - 修改浏览器指纹以避免基本的机器人检测。  
    - 默认为 `False`。推荐用于有机器人防护的网站。

### 辅助方法

两个配置类都提供了 `clone()` 方法来创建修改后的副本：

```python
# 创建一个基础浏览器配置
base_browser = BrowserConfig(
    browser_type="chromium",
    headless=True,
    text_mode=True
)

# 为调试创建一个可见的浏览器配置
debug_browser = base_browser.clone(
    headless=False,
    verbose=True
)
```

**最小示例**:

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig

browser_conf = BrowserConfig(
    browser_type="firefox",
    headless=False,
    text_mode=True
)

async with AsyncWebCrawler(config=browser_conf) as crawler:
    result = await crawler.arun("https://example.com")
    print(result.markdown[:300])
```

---

## 2. CrawlerRunConfig 要点

```python
class CrawlerRunConfig:
    def __init__(
        word_count_threshold=200,
        extraction_strategy=None,
        markdown_generator=None,
        cache_mode=None,
        js_code=None,
        wait_for=None,
        screenshot=False,
        pdf=False,
        capture_mhtml=False,
        # Location and Identity Parameters
        locale=None,            # e.g. "en-US", "fr-FR"
        timezone_id=None,       # e.g. "America/New_York"
        geolocation=None,       # GeolocationConfig object
        # Resource Management
        enable_rate_limiting=False,
        rate_limit_config=None,
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=20,
        display_mode=None,
        verbose=True,
        stream=False,  # Enable streaming for arun_many()
        # ... 此处省略了其他高级参数
    ):
        ...
```

### 需要注意的关键字段

1. **`word_count_threshold`**:  
   - 一个块被考虑之前的最小词数。  
   - 如果您的网站有很多短段落或项目，可以降低此值。

2. **`extraction_strategy`**:  
   - 您在此处插入基于 JSON 的提取（CSS、LLM 等）。  
   - 如果为 `None`，则不进行结构化提取（仅原始/清理后的 HTML + markdown）。

3. **`markdown_generator`**:  
   - 例如，`DefaultMarkdownGenerator(...)`，控制 HTML→Markdown 转换的方式。  
   - 如果为 `None`，则使用默认方法。

4. **`cache_mode`**:  
   - 控制缓存行为（`ENABLED`、`BYPASS`、`DISABLED` 等）。  
   - 如果为 `None`，则默认为某种级别的缓存，或者您可以指定 `CacheMode.ENABLED`。

5. **`js_code`**:  
   - 要执行的 JS 字符串或字符串列表。  
   - 非常适合“加载更多”按钮或用户交互。  

6. **`wait_for`**:  
   - 在提取内容之前等待的 CSS 或 JS 表达式。  
   - 常见用法：`wait_for="css:.main-loaded"` 或 `wait_for="js:() => window.loaded === true"`。

7. **`screenshot`**, **`pdf`**, & **`capture_mhtml`**:  
   - 如果为 `True`，则在页面完全加载后捕获屏幕截图、PDF 或 MHTML 快照。  
   - 结果将存入 `result.screenshot` (base64)、`result.pdf` (字节) 或 `result.mhtml` (字符串)。

8. **位置参数**:  
   - **`locale`**: 浏览器的区域设置（例如，`"en-US"`、`"fr-FR"`），用于语言偏好
   - **`timezone_id`**: 浏览器的时区（例如，`"America/New_York"`、`"Europe/Paris"`）
   - **`geolocation`**: 通过 `GeolocationConfig(latitude=48.8566, longitude=2.3522)` 设置的 GPS 坐标
   - 参见[基于身份的爬取](../advanced/identity-based-crawling.md#7-locale-timezone-and-geolocation-control)

9. **`verbose`**:  
   - 记录额外的运行时详细信息。  
   - 如果在 `BrowserConfig` 中也设置为 `True`，则与浏览器的详细程度重叠。

10. **`enable_rate_limiting`**:  
   - 如果为 `True`，则为批处理启用速率限制。  
   - 需要设置 `rate_limit_config`。

11. **`memory_threshold_percent`**:  
    - 要监视的内存阈值（百分比）。  
    - 如果超过，爬虫将暂停或减速。

12. **`check_interval`**:  
    - 检查系统资源的间隔（秒）。  
    - 影响监视内存和 CPU 使用情况的频率。

13. **`max_session_permit`**:  
    - 并发爬取会话的最大数量。  
    - 有助于防止系统过载。

14. **`url_matcher`** & **`match_mode`**:  
    - 与 `arun_many()` 一起使用时，启用特定于 URL 的配置。
    - 将 `url_matcher` 设置为模式（全局、函数或列表）以匹配特定 URL。
    - 使用 `match_mode` (OR/AND) 来控制多个模式的组合方式。
    - 有关示例，请参见[URL 特定配置](../api/arun_many.md#url-specific-configurations)。

15. **`display_mode`**:  
    - 进度信息的显示模式（`DETAILED`、`BRIEF` 等）。  
    - 影响爬取期间打印的信息量。


### 辅助方法

`clone()` 方法对于创建爬虫配置的变体特别有用：

```python
# 创建一个基础配置
base_config = CrawlerRunConfig(
    cache_mode=CacheMode.ENABLED,
    word_count_threshold=200,
    wait_until="networkidle"
)

# 为不同的用例创建变体
stream_config = base_config.clone(
    stream=True,  # 启用流模式
    cache_mode=CacheMode.BYPASS
)

debug_config = base_config.clone(
    page_timeout=120000,  # 为调试设置更长的超时
    verbose=True
)
```

`clone()` 方法：
- 创建一个具有所有相同设置的新实例
- 仅更新指定的参数
- 保持原始配置不变
- 非常适合在不重复所有参数的情况下创建变体

---

## 3. LLMConfig 要点

### 需要注意的关键字段

1. **`provider`**:  
- 使用哪个 LLM 提供商。
- 可能的值是 `"ollama/llama3"`、`"groq/llama3-70b-8192"`、`"groq/llama3-8b-8192"`、`"openai/gpt-4o-mini"`、`"openai/gpt-4o"`、`"openai/o1-mini"`、`"openai/o1-preview"`、`"openai/o3-mini"`、`"openai/o3-mini-high"`、`"anthropic/claude-3-haiku-20240307"`、`"anthropic/claude-3-opus-20240229"`、`"anthropic/claude-3-sonnet-20240229"`、`"anthropic/claude-3-5-sonnet-20240620"`、`"gemini/gemini-pro"`、`"gemini/gemini-1.5-pro"`、`"gemini/gemini-2.0-flash"`、`"gemini/gemini-2.0-flash-exp"`、`"gemini/gemini-2.0-flash-lite-preview-02-05"`、`"deepseek/deepseek-chat"`<br/>*(默认：`"openai/gpt-4o-mini"`)*

2. **`api_token`**:  
    - 可选。当未明确提供时，api_token 将根据提供商从环境变量中读取。例如：如果传递了一个 gemini 模型作为提供商，则将从环境变量中读取 `"GEMINI_API_KEY"`。
    - LLM 提供商的 API 令牌 <br/> 例如：`api_token = "gsk_1ClHGGJ7Lpn4WGybR7vNWGdyb3FY7zXEw3SCiy0BAVM9lL8CQv"`
    - 环境变量 - 使用前缀 "env:" <br/> 例如：`api_token = "env: GROQ_API_KEY"`            

3. **`base_url`**:  
   - 如果您的提供商有自定义端点

```python
llm_config = LLMConfig(provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY"))
```

## 4. 综合运用

在典型场景中，您为爬虫会话定义**一个** `BrowserConfig`，然后根据每次调用的需要创建**一个或多个** `CrawlerRunConfig` & `LLMConfig`：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig, LLMContentFilter, DefaultMarkdownGenerator
from crawl4ai import JsonCssExtractionStrategy

async def main():
    # 1) 浏览器配置：无头，更大的视口，无代理
    browser_conf = BrowserConfig(
        headless=True,
        viewport_width=1280,
        viewport_height=720
    )

    # 2) 示例提取策略
    schema = {
        "name": "Articles",
        "baseSelector": "div.article",
        "fields": [
            {"name": "title", "selector": "h2", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
        ]
    }
    extraction = JsonCssExtractionStrategy(schema)

    # 3) 示例 LLM 内容过滤

    gemini_config = LLMConfig(
        provider="gemini/gemini-1.5-pro", 
        api_token = "env:GEMINI_API_TOKEN"
    )

    # 使用特定指令初始化 LLM 过滤器
    filter = LLMContentFilter(
        llm_config=gemini_config,  # 或您首选的提供商
        instruction="""
        专注于提取核心教育内容。
        包括：
        - 关键概念和解释
        - 重要的代码示例
        - 必要的技术细节
        排除：
        - 导航元素
        - 侧边栏
        - 页脚内容
        将输出格式化为带有适当代码块和标题的干净 markdown。
        """,
        chunk_token_threshold=500,  # 根据您的需要调整
        verbose=True
    )

    md_generator = DefaultMarkdownGenerator(
        content_filter=filter,
        options={"ignore_links": True}
    )

    # 4) 爬虫运行配置：跳过缓存，使用提取
    run_conf = CrawlerRunConfig(
        markdown_generator=md_generator,
        extraction_strategy=extraction,
        cache_mode=CacheMode.BYPASS,
    )

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        # 4) 执行爬取
        result = await crawler.arun(url="https://example.com/news", config=run_conf)

        if result.success:
            print("Extracted content:", result.extracted_content)
        else:
            print("Error:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 5. 后续步骤

有关可用参数（包括高级参数）的**详细列表**，请参阅：

- [BrowserConfig, CrawlerRunConfig & LLMConfig 参考](../api/parameters.md)  

您可以探索以下主题：

- **自定义钩子和认证**（注入 JavaScript 或处理登录表单）。  
- **会话管理**（重用页面，在多次调用之间保持状态）。  
- **魔法模式**或**基于身份的爬取**（通过模拟用户行为来对抗机器人检测）。  
- **高级缓存**（微调读/写缓存模式）。  

---

## 6. 结论

**BrowserConfig**、**CrawlerRunConfig** 和 **LLMConfig** 为您提供了直接的方法来定义：

- **哪个**浏览器启动，它应该如何运行，以及任何代理或用户代理需求。  
- **每次爬取**应该如何行为——缓存、超时、JavaScript 代码、提取策略等。
- **使用哪个** LLM 提供商、API 令牌、温度以及用于自定义端点的基础 URL。

将它们一起用于**清晰、可维护**的代码，当您需要更专业的行为时，请查看[参考文档](../api/parameters.md)中的高级参数。祝您爬取愉快！