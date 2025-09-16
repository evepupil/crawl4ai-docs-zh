# 内容选择

Crawl4AI 提供了多种方式来**选择**、**过滤**和**优化**爬取内容。无论您需要定位特定CSS区域、排除整个标签、过滤外部链接，还是移除特定域名和图片，**`CrawlerRunConfig`**都提供了丰富的参数配置。

下面我们将展示如何配置这些参数并组合使用以实现精准控制。

---

## 1. 基于CSS的选择

有两种方式可以从页面中选择内容：使用`css_selector`或更灵活的`target_elements`。

### 1.1 使用`css_selector`

**`css_selector`**是**`CrawlerRunConfig`**中最直接的**限制**爬取结果到页面特定区域的方法：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def main():
    config = CrawlerRunConfig(
        # 例如，Hacker News的前30条内容
        css_selector=".athing:nth-child(-n+30)"  
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://news.ycombinator.com/newest", 
            config=config
        )
        print("部分HTML长度:", len(result.cleaned_html))

if __name__ == "__main__":
    asyncio.run(main())
```

**结果**：只有匹配该选择器的元素会保留在`result.cleaned_html`中。

### 1.2 使用`target_elements`

`target_elements`参数提供了更大的灵活性，允许您针对**多个元素**进行内容提取，同时保留整个页面的上下文以供其他功能使用：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def main():
    config = CrawlerRunConfig(
        # 定位文章主体和侧边栏，但不包括其他内容
        target_elements=["article.main-content", "aside.sidebar"]
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://example.com/blog-post", 
            config=config
        )
        print("专注于目标元素的Markdown")
        print("整个页面的链接仍然可用:", len(result.links.get("internal", [])))

if __name__ == "__main__":
    asyncio.run(main())
```

**关键区别**：使用`target_elements`时，Markdown生成和结构化数据提取会专注于这些元素，但其他页面元素（如链接、图片和表格）仍会从整个页面中提取。这使您可以精细控制Markdown内容中显示的内容，同时保留完整的页面上下文以进行链接分析和媒体收集。

---

## 2. 内容过滤与排除

### 2.1 基本概述

```python
config = CrawlerRunConfig(
    # 内容阈值
    word_count_threshold=10,        # 每个文本块的最小单词数

    # 标签排除
    excluded_tags=['form', 'header', 'footer', 'nav'],

    # 链接过滤
    exclude_external_links=True,    
    exclude_social_media_links=True,
    # 阻止整个域名
    exclude_domains=["adtrackers.com", "spammynews.org"],    
    exclude_social_media_domains=["facebook.com", "twitter.com"],

    # 媒体过滤
    exclude_external_images=True
)
```

**说明**：

- **`word_count_threshold`**：忽略少于X个单词的文本块。有助于跳过导航或免责声明等简短内容。  
- **`excluded_tags`**：移除整个标签（如`<form>`、`<header>`、`<footer>`等）。  
- **链接过滤**：  
  - `exclude_external_links`：移除外部链接，并可能从`result.links`中删除它们。  
  - `exclude_social_media_links`：移除指向已知社交媒体域名的链接。  
  - `exclude_domains`：自定义域名列表，阻止发现的链接。  
  - `exclude_social_media_domains`：社交媒体网站的精选列表（可覆盖或添加）。  
- **媒体过滤**：  
  - `exclude_external_images`：丢弃非主页面域名（或其子域名）托管的图片。

默认情况下，如果您设置`exclude_social_media_links=True`，以下社交媒体域名将被排除：
```python
[
    'facebook.com',
    'twitter.com',
    'x.com',
    'linkedin.com',
    'instagram.com',
    'pinterest.com',
    'tiktok.com',
    'snapchat.com',
    'reddit.com',
]
```


### 2.2 示例用法

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

async def main():
    config = CrawlerRunConfig(
        css_selector="main.content", 
        word_count_threshold=10,
        excluded_tags=["nav", "footer"],
        exclude_external_links=True,
        exclude_social_media_links=True,
        exclude_domains=["ads.com", "spammytrackers.net"],
        exclude_external_images=True,
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://news.ycombinator.com", config=config)
        print("清理后的HTML长度:", len(result.cleaned_html))

if __name__ == "__main__":
    asyncio.run(main())
```

**注意**：如果这些参数移除的内容过多，可以相应减少或禁用它们。

---

## 3. 处理Iframes

某些网站在`<iframe>`标签中嵌入内容。如果您希望将其内联：
```python
config = CrawlerRunConfig(
    # 将iframe内容合并到最终输出中
    process_iframes=True,    
    remove_overlay_elements=True
)
```

**用法**：
```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def main():
    config = CrawlerRunConfig(
        process_iframes=True,
        remove_overlay_elements=True
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://example.org/iframe-demo", 
            config=config
        )
        print("合并iframe后的长度:", len(result.cleaned_html))

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 4. 结构化提取示例

您可以将内容选择与更高级的提取策略结合使用。例如，可以在过滤后的HTML上运行**基于CSS**或**基于LLM**的提取策略。

### 4.1 使用`JsonCssExtractionStrategy`进行模式提取

```python
import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai import JsonCssExtractionStrategy

async def main():
    # 重复项的最小模式
    schema = {
        "name": "News Items",
        "baseSelector": "tr.athing",
        "fields": [
            {"name": "title", "selector": "span.titleline a", "type": "text"},
            {
                "name": "link", 
                "selector": "span.titleline a", 
                "type": "attribute", 
                "attribute": "href"
            }
        ]
    }

    config = CrawlerRunConfig(
        # 内容过滤
        excluded_tags=["form", "header"],
        exclude_domains=["adsite.com"],
        
        # CSS选择或整个页面
        css_selector="table.itemlist",

        # 演示时不使用缓存
        cache_mode=CacheMode.BYPASS,

        # 提取策略
        extraction_strategy=JsonCssExtractionStrategy(schema)
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://news.ycombinator.com/newest", 
            config=config
        )
        data = json.loads(result.extracted_content)
        print("示例提取项:", data[:1])  # 显示第一项

if __name__ == "__main__":
    asyncio.run(main())
```

### 4.2 基于LLM的提取

```python
import asyncio
import json
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai import LLMExtractionStrategy

class ArticleData(BaseModel):
    headline: str
    summary: str

async def main():
    llm_strategy = LLMExtractionStrategy(
        llm_config = LLMConfig(provider="openai/gpt-4",api_token="sk-YOUR_API_KEY")
        schema=ArticleData.schema(),
        extraction_type="schema",
        instruction="从内容中提取'headline'和简短的'summary'。"
    )

    config = CrawlerRunConfig(
        exclude_external_links=True,
        word_count_threshold=20,
        extraction_strategy=llm_strategy
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://news.ycombinator.com", config=config)
        article = json.loads(result.extracted_content)
        print(article)

if __name__ == "__main__":
    asyncio.run(main())
```

在此示例中，爬虫：

- 过滤掉外部链接（`exclude_external_links=True`）。  
- 忽略非常短的文本块（`word_count_threshold=20`）。  
- 将最终的HTML传递给您的LLM策略进行AI驱动的解析。

---

## 5. 综合示例

以下是一个简短的函数，结合了**CSS选择**、**排除**逻辑和基于模式的提取，展示了如何微调最终数据：

```python
import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai import JsonCssExtractionStrategy

async def extract_main_articles(url: str):
    schema = {
        "name": "ArticleBlock",
        "baseSelector": "div.article-block",
        "fields": [
            {"name": "headline", "selector": "h2", "type": "text"},
            {"name": "summary", "selector": ".summary", "type": "text"},
            {
                "name": "metadata",
                "type": "nested",
                "fields": [
                    {"name": "author", "selector": ".author", "type": "text"},
                    {"name": "date", "selector": ".date", "type": "text"}
                ]
            }
        ]
    }

    config = CrawlerRunConfig(
        # 仅保留#main-content
        css_selector="#main-content",
        
        # 过滤
        word_count_threshold=10,
        excluded_tags=["nav", "footer"],  
        exclude_external_links=True,
        exclude_domains=["somebadsite.com"],
        exclude_external_images=True,

        # 提取
        extraction_strategy=JsonCssExtractionStrategy(schema),
        
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        if not result.success:
            print(f"错误: {result.error_message}")
            return None
        return json.loads(result.extracted_content)

async def main():
    articles = await extract_main_articles("https://news.ycombinator.com/newest")
    if articles:
        print("提取的文章:", articles[:2])  # 显示前2项

if __name__ == "__main__":
    asyncio.run(main())
```

**为什么有效**：
- 使用`#main-content`进行**CSS**范围限定。  
- 多个**exclude_**参数用于移除域名、外部图片等。  
- 使用**JsonCssExtractionStrategy**解析重复的文章块。

---

## 6. 爬取模式

Crawl4AI默认使用`LXMLWebScrapingStrategy`（基于LXML）作为HTML内容处理的默认爬取策略。该策略提供了出色的性能，特别是对于大型HTML文档。

**注意：** 为了向后兼容，`WebScrapingStrategy`仍然可用，作为`LXMLWebScrapingStrategy`的别名。

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LXMLWebScrapingStrategy

async def main():
    # 默认配置已使用LXMLWebScrapingStrategy
    config = CrawlerRunConfig()
    
    # 或者显式指定
    config_explicit = CrawlerRunConfig(
        scraping_strategy=LXMLWebScrapingStrategy()
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://example.com", 
            config=config
        )
```

您还可以通过继承`ContentScrapingStrategy`创建自定义爬取策略。该策略必须返回一个`ScrapingResult`对象，其结构如下：

```python
from crawl4ai import ContentScrapingStrategy, ScrapingResult, MediaItem, Media, Link, Links

class CustomScrapingStrategy(ContentScrapingStrategy):
    def scrap(self, url: str, html: str, **kwargs) -> ScrapingResult:
        # 在此实现自定义爬取逻辑
        return ScrapingResult(
            cleaned_html="<html>...</html>",  # 清理后的HTML内容
            success=True,                     # 爬取是否成功
            media=Media(
                images=[                      # 找到的图片列表
                    MediaItem(
                        src="https://example.com/image.jpg",
                        alt="图片描述",
                        desc="周围文本",
                        score=1,
                        type="image",
                        group_id=1,
                        format="jpg",
                        width=800
                    )
                ],
                videos=[],                    # 视频列表（结构与图片相同）
                audios=[]                     # 音频文件列表（结构与图片相同）
            ),
            links=Links(
                internal=[                    # 内部链接列表
                    Link(
                        href="https://example.com/page",
                        text="链接文本",
                        title="链接标题",
                        base_domain="example.com"
                    )
                ],
                external=[]                   # 外部链接列表（结构相同）
            ),
            metadata={                        # 附加元数据
                "title": "页面标题",
                "description": "页面描述"
            }
        )

    async def ascrap(self, url: str, html: str, **kwargs) -> ScrapingResult:
        # 对于简单情况，可以使用同步版本
        return await asyncio.to_thread(self.scrap, url, html, **kwargs)
```

### 性能考虑

LXML策略提供了出色的性能，特别是在处理大型HTML文档时，与基于BeautifulSoup的方法相比，处理速度提高了10-20倍。

LXML策略的优势：
- 快速处理大型HTML文档（尤其是>100KB）
- 高效的内存使用
- 对格式良好的HTML处理良好
- 强大的表格检测和提取功能

### 向后兼容性

对于从早期版本升级的用户：
- `WebScrapingStrategy`现在是`LXMLWebScrapingStrategy`的别名
- 使用`WebScrapingStrategy`的现有代码无需修改即可继续工作
- 无需更改现有代码

---

## 7. 组合CSS选择方法

您可以结合`css_selector`和`target_elements`以实现对输出的精细控制：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

async def main():
    # 定位特定内容但保留页面上下文
    config = CrawlerRunConfig(
        # 专注于主内容和侧边栏的Markdown
        target_elements=["#main-content", ".sidebar"],
        
        # 应用于整个页面的全局过滤器
        excluded_tags=["nav", "footer", "header"],
        exclude_external_links=True,
        
        # 使用基本内容阈值
        word_count_threshold=15,
        
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://example.com/article",
            config=config
        )
        
        print(f"内容专注于特定元素，但仍分析所有链接")
        print(f"内部链接: {len(result.links.get('internal', []))}")
        print(f"外部链接: {len(result.links.get('external', []))}")

if __name__ == "__main__":
    asyncio.run(main())
```

这种方法结合了两者的优势：
- Markdown生成和内容提取专注于您关心的元素
- 链接、图片和其他页面数据仍提供完整的页面上下文
- 内容过滤仍全局应用

## 8. 结论

通过混合使用**target_elements**或**css_selector**范围限定、**内容过滤**参数和高级**提取策略**，您可以精确**选择**要保留的数据。**`CrawlerRunConfig`**中用于内容选择的关键参数包括：

1. **`target_elements`** – CSS选择器数组，专注于Markdown生成和数据提取，同时保留链接和媒体的完整页面上下文。
2. **`css_selector`** – 基本范围限定到元素或区域以进行所有提取过程。  
3. **`word_count_threshold`** – 跳过短文本块。  
4. **`excluded_tags`** – 移除整个HTML标签。  
5. **`exclude_external_links`**、**`exclude_social_media_links`**、**`exclude_domains`** – 过滤不需要的链接或域名。  
6. **`exclude_external_images`** – 移除来自外部源的图片。  
7. **`process_iframes`** – 根据需要合并iframe内容。  

将这些与结构化提取（CSS、基于LLM或其他）结合使用，可以构建强大的爬虫，从原始或清理后的HTML到复杂的JSON结构，获取您想要的确切内容。更多详情，请参阅[配置参考](../api/parameters.md)。尽情优化您的数据吧！