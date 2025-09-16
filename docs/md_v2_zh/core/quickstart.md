# Crawl4AI 入门指南

欢迎使用 **Crawl4AI**，一个开源的LLM友好型网络爬虫与数据提取工具。在本教程中，您将：

1. 使用最小配置运行**第一次爬取**  
2. 生成**Markdown**输出（并了解内容过滤器如何影响结果）  
3. 尝试基于**CSS的选择器提取**策略  
4. 初步了解**基于LLM的提取**（包括开源和闭源模型选项）  
5. 爬取通过JavaScript加载内容的**动态**页面

---

## 1. 简介

Crawl4AI提供：

- 异步爬虫 **`AsyncWebCrawler`**  
- 通过 **`BrowserConfig`** 和 **`CrawlerRunConfig`** 配置浏览器和运行设置  
- 通过 **`DefaultMarkdownGenerator`** 自动将HTML转换为Markdown（支持可选过滤器）  
- 多种提取策略（基于LLM或"传统"的CSS/XPath）

完成本指南后，您将掌握基本爬取、生成Markdown、尝试两种提取策略，并能爬取使用"加载更多"按钮或JavaScript更新的动态页面。

---

## 2. 第一次爬取

这是一个创建 **`AsyncWebCrawler`**、获取网页并打印其Markdown输出前300个字符的最小Python脚本：

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com")
        print(result.markdown[:300])  # 打印前300个字符

if __name__ == "__main__":
    asyncio.run(main())
```

**发生了什么？**
- **`AsyncWebCrawler`** 启动无头浏览器（默认Chromium）
- 获取 `https://example.com`
- Crawl4AI自动将HTML转换为Markdown

现在您已经完成了一个简单可用的爬取！

---

## 3. 基本配置（简要介绍）

Crawl4AI的爬虫可通过两个主要类进行高度定制：

1. **`BrowserConfig`**：控制浏览器行为（无头或完整UI、用户代理、JavaScript开关等）  
2. **`CrawlerRunConfig`**：控制每次爬取的运行方式（缓存、提取、超时、钩子等）

以下是一个最小化使用示例：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def main():
    browser_conf = BrowserConfig(headless=True)  # 或False以查看浏览器
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(
            url="https://example.com",
            config=run_conf
        )
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())
```

> 重要提示：默认缓存模式为 `CacheMode.ENABLED`。要获取最新内容，需设置为 `CacheMode.BYPASS`

我们将在后续教程中探索更高级的配置（如启用代理、PDF输出、多标签会话等）。现在只需注意如何传递这些对象来管理爬取。

---

## 4. 生成Markdown输出

默认情况下，Crawl4AI自动将每个爬取的页面转换为Markdown。但具体输出取决于是否指定**markdown生成器**或**内容过滤器**。

- **`result.markdown`**：  
  直接的HTML到Markdown转换  
- **`result.markdown.fit_markdown`**：  
  应用任何配置的**内容过滤器**后的相同内容（如`PruningContentFilter`）

### 示例：使用带有`DefaultMarkdownGenerator`的过滤器

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

md_generator = DefaultMarkdownGenerator(
    content_filter=PruningContentFilter(threshold=0.4, threshold_type="fixed")
)

config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    markdown_generator=md_generator
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun("https://news.ycombinator.com", config=config)
    print("原始Markdown长度:", len(result.markdown.raw_markdown))
    print("适配后Markdown长度:", len(result.markdown.fit_markdown))
```

**注意**：如果未指定内容过滤器或markdown生成器，通常只会看到原始Markdown。`PruningContentFilter`可能会增加约`50ms`的处理时间。我们将在专门的**Markdown生成**教程中深入探讨这些策略。

---

## 5. 简单数据提取（基于CSS）

Crawl4AI还可以使用CSS或XPath选择器提取结构化数据（JSON）。以下是一个最小的基于CSS的示例：

> **新功能！** Crawl4AI现在提供了一个强大的实用程序，可使用LLM自动生成提取模式。这是一次性成本，为您提供可重用的模式，实现快速、无需LLM的提取：

```python
from crawl4ai import JsonCssExtractionStrategy
from crawl4ai import LLMConfig

# 生成模式（一次性成本）
html = "<div class='product'><h2>游戏笔记本</h2><span class='price'>$999.99</span></div>"

# 使用OpenAI（需要API令牌）
schema = JsonCssExtractionStrategy.generate_schema(
    html,
    llm_config = LLMConfig(provider="openai/gpt-4o",api_token="your-openai-token")  # OpenAI需要
)

# 或使用Ollama（开源，无需令牌）
schema = JsonCssExtractionStrategy.generate_schema(
    html,
    llm_config = LLMConfig(provider="ollama/llama3.3", api_token=None)  # Ollama不需要
)

# 使用模式进行快速、重复的提取
strategy = JsonCssExtractionStrategy(schema)
```

关于模式生成和高级使用的完整指南，请参阅[无LLM提取策略](../extraction/no-llm-strategies.md)。

这是一个基本的提取示例：

```python
import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai import JsonCssExtractionStrategy

async def main():
    schema = {
        "name": "示例项目",
        "baseSelector": "div.item",
        "fields": [
            {"name": "title", "selector": "h2", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
        ]
    }

    raw_html = "<div class='item'><h2>项目1</h2><a href='https://example.com/item1'>链接1</a></div>"

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="raw://" + raw_html,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=JsonCssExtractionStrategy(schema)
            )
        )
        # JSON输出存储在'extracted_content'中
        data = json.loads(result.extracted_content)
        print(data)

if __name__ == "__main__":
    asyncio.run(main())
```

**为什么这很有用？**
- 适用于重复的页面结构（如项目列表、文章）
- 无需AI使用或成本
- 爬虫返回可解析或存储的JSON字符串

> 提示：您可以向爬虫传递原始HTML而非URL。为此，在HTML前加上`raw://`。

---

## 6. 简单数据提取（基于LLM）

对于更复杂或不规则的页面，语言模型可以智能地将文本解析为您定义的结构。Crawl4AI支持**开源**或**闭源**提供商：

- **开源模型**（如`ollama/llama3.3`，`no_token`）  
- **OpenAI模型**（如`openai/gpt-4`，需要`api_token`）  
- 或底层库支持的任何提供商

以下是使用**开源**风格（无令牌）和闭源的示例：

```python
import os
import json
import asyncio
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai import LLMExtractionStrategy

class OpenAIModelFee(BaseModel):
    model_name: str = Field(..., description="OpenAI模型的名称。")
    input_fee: str = Field(..., description="OpenAI模型输入令牌的费用。")
    output_fee: str = Field(
        ..., description="OpenAI模型输出令牌的费用。"
    )

async def extract_structured_data_using_llm(
    provider: str, api_token: str = None, extra_headers: Dict[str, str] = None
):
    print(f"\n--- 使用{provider}提取结构化数据 ---")

    if api_token is None and provider != "ollama":
        print(f"{provider}需要API令牌。跳过此示例。")
        return

    browser_config = BrowserConfig(headless=True)

    extra_args = {"temperature": 0, "top_p": 0.9, "max_tokens": 2000}
    if extra_headers:
        extra_args["extra_headers"] = extra_headers

    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=1,
        page_timeout=80000,
        extraction_strategy=LLMExtractionStrategy(
            llm_config = LLMConfig(provider=provider,api_token=api_token),
            schema=OpenAIModelFee.model_json_schema(),
            extraction_type="schema",
            instruction="""从爬取的内容中，提取所有提到的模型名称及其输入和输出令牌的费用。
            不要遗漏整个内容中的任何模型。""",
            extra_args=extra_args,
        ),
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://openai.com/api/pricing/", config=crawler_config
        )
        print(result.extracted_content)

if __name__ == "__main__":

    asyncio.run(
        extract_structured_data_using_llm(
            provider="openai/gpt-4o", api_token=os.getenv("OPENAI_API_KEY")
        )
    )
```

**发生了什么？**
- 我们定义了一个Pydantic模式（`PricingInfo`），描述我们想要的字段
- LLM提取策略使用该模式和您的指令将原始文本转换为结构化JSON
- 根据**提供商**和**api_token**，您可以使用本地模型或远程API

---

## 7. 自适应爬取（新功能！）

Crawl4AI现在包含智能自适应爬取，自动确定何时收集到足够的信息。以下是一个快速示例：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, AdaptiveCrawler

async def adaptive_example():
    async with AsyncWebCrawler() as crawler:
        adaptive = AdaptiveCrawler(crawler)
        
        # 开始自适应爬取
        result = await adaptive.digest(
            start_url="https://docs.python.org/3/",
            query="异步上下文管理器"
        )
        
        # 查看结果
        adaptive.print_stats()
        print(f"爬取了{len(result.crawled_urls)}个页面")
        print(f"达到{adaptive.confidence:.0%}的置信度")

if __name__ == "__main__":
    asyncio.run(adaptive_example())
```

**自适应爬取有什么特别之处？**
- **自动停止**：当收集到足够信息时停止
- **智能链接选择**：仅跟踪相关链接
- **置信度评分**：了解信息的完整程度

[了解更多关于自适应爬取→](adaptive-crawling.md)

---

## 8. 多URL并发（预览）

如果需要**并行**爬取多个URL，可以使用`arun_many()`。默认情况下，Crawl4AI使用**MemoryAdaptiveDispatcher**，根据系统资源自动调整并发。以下是一个快速示例：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

async def quick_parallel_example():
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3"
    ]
    
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=True  # 启用流模式
    )

    async with AsyncWebCrawler() as crawler:
        # 流式处理完成的结果
        async for result in await crawler.arun_many(urls, config=run_conf):
            if result.success:
                print(f"[成功] {result.url}, 长度: {len(result.markdown.raw_markdown)}")
            else:
                print(f"[错误] {result.url} => {result.error_message}")

        # 或一次性获取所有结果（默认行为）
        run_conf = run_conf.clone(stream=False)
        results = await crawler.arun_many(urls, config=run_conf)
        for res in results:
            if res.success:
                print(f"[成功] {res.url}, 长度: {len(res.markdown.raw_markdown)}")
            else:
                print(f"[错误] {res.url} => {res.error_message}")

if __name__ == "__main__":
    asyncio.run(quick_parallel_example())
```

上面的示例展示了处理多个URL的两种方式：
1. **流模式**（`stream=True`）：使用`async for`处理可用的结果
2. **批处理模式**（`stream=False`）：等待所有结果完成

关于更高级的并发（如**基于信号量**的方法、**自适应内存使用节流**或自定义速率限制），请参阅[高级多URL爬取](../advanced/multi-url-crawling.md)。

---

## 8. 动态内容示例

某些网站需要多次"页面点击"或动态JavaScript更新。以下是一个示例，展示如何在GitHub上**点击**"下一页"按钮并等待新提交加载，使用**`BrowserConfig`**和**`CrawlerRunConfig`**：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai import JsonCssExtractionStrategy

async def extract_structured_data_using_css_extractor():
    print("\n--- 使用JsonCssExtractionStrategy快速结构化输出 ---")
    schema = {
        "name": "KidoCode课程",
        "baseSelector": "section.charge-methodology .w-tab-content > div",
        "fields": [
            {
                "name": "section_title",
                "selector": "h3.heading-50",
                "type": "text",
            },
            {
                "name": "section_description",
                "selector": ".charge-content",
                "type": "text",
            },
            {
                "name": "course_name",
                "selector": ".text-block-93",
                "type": "text",
            },
            {
                "name": "course_description",
                "selector": ".course-content-text",
                "type": "text",
            },
            {
                "name": "course_icon",
                "selector": ".image-92",
                "type": "attribute",
                "attribute": "src",
            },
        ],
    }

    browser_config = BrowserConfig(headless=True, java_script_enabled=True)

    js_click_tabs = """
    (async () => {
        const tabs = document.querySelectorAll("section.charge-methodology .tabs-menu-3 > div");
        for(let tab of tabs) {
            tab.scrollIntoView();
            tab.click();
            await new Promise(r => setTimeout(r, 500));
        }
    })();
    """

    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(schema),
        js_code=[js_click_tabs],
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://www.kidocode.com/degrees/technology", config=crawler_config
        )

        companies = json.loads(result.extracted_content)
        print(f"成功提取了{len(companies)}家公司")
        print(json.dumps(companies[0], indent=2))

async def main():
    await extract_structured_data_using_css_extractor()

if __name__ == "__main__":
    asyncio.run(main())
```

**关键点**：

- **`BrowserConfig(headless=False)`**：我们想观察它点击"下一页"  
- **`CrawlerRunConfig(...)`**：我们指定提取策略，传递`session_id`以重用同一页面  
- **`js_code`**和**`wait_for`**用于后续页面（`page > 0`）点击"下一页"按钮并等待新提交加载  
- **`js_only=True`**表示我们不重新导航，而是继续现有会话  
- 最后，我们调用`kill_session()`清理页面和浏览器会话

---

## 9. 下一步

恭喜！您已经：

1. 执行了基本爬取并打印了Markdown  
2. 使用**内容过滤器**与markdown生成器  
3. 通过**CSS**或**LLM**策略提取JSON  
4. 处理了带有JavaScript触发器的**动态**页面  

如果您准备好进一步学习，请查看：

- **安装**：深入了解高级安装、Docker使用（实验性）或可选依赖项  
- **钩子与认证**：学习如何运行自定义JavaScript或处理带有cookie、本地存储等的登录  
- **部署**：探索Docker中的临时测试或为即将到来的稳定Docker版本做准备  
- **浏览器管理**：深入研究用户模拟、隐身模式和并发最佳实践  

Crawl4AI是一个强大、灵活的工具。祝您构建爬虫、数据管道或AI驱动的提取流程顺利。爬取愉快！