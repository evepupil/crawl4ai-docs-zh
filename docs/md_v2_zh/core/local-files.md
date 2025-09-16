# Crawl4AI 基于前缀的输入处理指南

本指南将介绍如何使用 Crawl4AI 库来爬取网页、本地 HTML 文件和原始 HTML 字符串。我们将以维基百科页面为例演示这些功能。

## 爬取网页 URL

要爬取在线网页，请提供以 `http://` 或 `https://` 开头的 URL，并使用 `CrawlerRunConfig` 对象：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

async def crawl_web():
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://en.wikipedia.org/wiki/apple", 
            config=config
        )
        if result.success:
            print("Markdown Content:")
            print(result.markdown)
        else:
            print(f"Failed to crawl: {result.error_message}")

asyncio.run(crawl_web())
```

## 爬取本地 HTML 文件

要爬取本地 HTML 文件，请在文件路径前添加 `file://` 前缀。

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

async def crawl_local_file():
    local_file_path = "/path/to/apple.html"  # 替换为你的文件路径
    file_url = f"file://{local_file_path}"
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=file_url, config=config)
        if result.success:
            print("Markdown Content from Local File:")
            print(result.markdown)
        else:
            print(f"Failed to crawl local file: {result.error_message}")

asyncio.run(crawl_local_file())
```

## 爬取原始 HTML 内容

要爬取原始 HTML 内容，请在 HTML 字符串前添加 `raw:` 前缀。

```python
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig

async def crawl_raw_html():
    raw_html = "<html><body><h1>Hello, World!</h1></body></html>"
    raw_html_url = f"raw:{raw_html}"
    config = CrawlerRunConfig(bypass_cache=True)
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=raw_html_url, config=config)
        if result.success:
            print("Markdown Content from Raw HTML:")
            print(result.markdown)
        else:
            print(f"Failed to crawl raw HTML: {result.error_message}")

asyncio.run(crawl_raw_html())
```

---

# 完整示例

以下是包含完整功能的脚本，它将：

1. 爬取维基百科的"Apple"页面
2. 将 HTML 内容保存到本地文件 (`apple.html`)
3. 爬取本地 HTML 文件并验证 Markdown 长度是否与原始爬取结果一致
4. 从保存的文件中爬取原始 HTML 内容并验证一致性

```python
import os
import sys
import asyncio
from pathlib import Path
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

async def main():
    wikipedia_url = "https://en.wikipedia.org/wiki/apple"
    script_dir = Path(__file__).parent
    html_file_path = script_dir / "apple.html"

    async with AsyncWebCrawler() as crawler:
        # Step 1: Crawl the Web URL
        print("\n=== Step 1: Crawling the Wikipedia URL ===")
        web_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
        result = await crawler.arun(url=wikipedia_url, config=web_config)

        if not result.success:
            print(f"Failed to crawl {wikipedia_url}: {result.error_message}")
            return

        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(result.html)
        web_crawl_length = len(result.markdown)
        print(f"Length of markdown from web crawl: {web_crawl_length}\n")

        # Step 2: Crawl from the Local HTML File
        print("=== Step 2: Crawling from the Local HTML File ===")
        file_url = f"file://{html_file_path.resolve()}"
        file_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
        local_result = await crawler.arun(url=file_url, config=file_config)

        if not local_result.success:
            print(f"Failed to crawl local file {file_url}: {local_result.error_message}")
            return

        local_crawl_length = len(local_result.markdown)
        assert web_crawl_length == local_crawl_length, "Markdown length mismatch"
        print("✅ Markdown length matches between web and local file crawl.\n")

        # Step 3: Crawl Using Raw HTML Content
        print("=== Step 3: Crawling Using Raw HTML Content ===")
        with open(html_file_path, 'r', encoding='utf-8') as f:
            raw_html_content = f.read()
        raw_html_url = f"raw:{raw_html_content}"
        raw_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
        raw_result = await crawler.arun(url=raw_html_url, config=raw_config)

        if not raw_result.success:
            print(f"Failed to crawl raw HTML content: {raw_result.error_message}")
            return

        raw_crawl_length = len(raw_result.markdown)
        assert web_crawl_length == raw_crawl_length, "Markdown length mismatch"
        print("✅ Markdown length matches between web and raw HTML crawl.\n")

        print("All tests passed successfully!")
    if html_file_path.exists():
        os.remove(html_file_path)

if __name__ == "__main__":
    asyncio.run(main())
```

---

# 结论

通过 **Crawl4AI** 的统一 `url` 参数和基于前缀的处理方式，您可以无缝处理网页 URL、本地 HTML 文件和原始 HTML 内容。在所有场景中使用 `CrawlerRunConfig` 可实现灵活且一致的配置。