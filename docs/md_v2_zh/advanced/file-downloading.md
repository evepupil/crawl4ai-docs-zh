# Crawl4AI 下载处理指南

本文档介绍如何使用 Crawl4AI 处理爬取过程中的文件下载操作。您将学习如何触发下载、指定下载位置以及访问已下载文件。

## 启用下载功能

要启用下载功能，请在 `BrowserConfig` 对象中设置 `accept_downloads` 参数，并将其传递给爬虫。

```python
from crawl4ai.async_configs import BrowserConfig, AsyncWebCrawler

async def main():
    config = BrowserConfig(accept_downloads=True)  # 全局启用下载功能
    async with AsyncWebCrawler(config=config) as crawler:
        # ... 您的爬取逻辑 ...

asyncio.run(main())
```

## 指定下载位置

使用 `BrowserConfig` 对象中的 `downloads_path` 属性指定下载目录。如未指定，Crawl4AI 默认会在用户主目录的 `.crawl4ai` 文件夹内创建 "downloads" 目录。

```python
from crawl4ai.async_configs import BrowserConfig
import os

downloads_path = os.path.join(os.getcwd(), "my_downloads")  # 自定义下载路径
os.makedirs(downloads_path, exist_ok=True)

config = BrowserConfig(accept_downloads=True, downloads_path=downloads_path)

async def main():
    async with AsyncWebCrawler(config=config) as crawler:
        result = await crawler.arun(url="https://example.com")
        # ...
```

## 触发下载操作

下载通常由网页上的用户交互触发，例如点击下载按钮。使用 `CrawlerRunConfig` 中的 `js_code` 模拟这些操作，并使用 `wait_for` 确保有足够时间开始下载。

```python
from crawl4ai.async_configs import CrawlerRunConfig

config = CrawlerRunConfig(
    js_code="""
        const downloadLink = document.querySelector('a[href$=".exe"]');
        if (downloadLink) {
            downloadLink.click();
        }
    """,
    wait_for=5  # 等待5秒让下载开始
)

result = await crawler.arun(url="https://www.python.org/downloads/", config=config)
```

## 访问已下载文件

通过 `CrawlResult` 对象的 `downloaded_files` 属性可获取已下载文件的路径。

```python
if result.downloaded_files:
    print("已下载文件:")
    for file_path in result.downloaded_files:
        print(f"- {file_path}")
        file_size = os.path.getsize(file_path)
        print(f"- 文件大小: {file_size} bytes")
else:
    print("没有文件被下载。")
```

## 示例：下载多个文件

```python
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
import os
from pathlib import Path

async def download_multiple_files(url: str, download_path: str):
    config = BrowserConfig(accept_downloads=True, downloads_path=download_path)
    async with AsyncWebCrawler(config=config) as crawler:
        run_config = CrawlerRunConfig(
            js_code="""
                const downloadLinks = document.querySelectorAll('a[download]');
                for (const link of downloadLinks) {
                    link.click();
                    // 点击间隔延迟
                    await new Promise(r => setTimeout(r, 2000));  
                }
            """,
            wait_for=10  # 等待所有下载开始
        )
        result = await crawler.arun(url=url, config=run_config)

        if result.downloaded_files:
            print("已下载文件:")
            for file in result.downloaded_files:
                print(f"- {file}")
        else:
            print("没有文件被下载。")

# 使用示例
download_path = os.path.join(Path.home(), ".crawl4ai", "downloads")
os.makedirs(download_path, exist_ok=True)

asyncio.run(download_multiple_files("https://www.python.org/downloads/windows/", download_path))
```

## 重要注意事项

- **浏览器上下文:** 下载操作在浏览器上下文中管理。确保 `js_code` 正确定位网页上的下载触发器。
- **时间控制:** 使用 `CrawlerRunConfig` 中的 `wait_for` 管理下载时间。
- **错误处理:** 妥善处理错误，优雅应对下载失败或路径错误的情况。
- **安全性:** 使用前请扫描下载文件，防范潜在安全威胁。

本指南通过使用 `BrowserConfig` 和 `CrawlerRunConfig` 进行所有下载相关配置，确保与 `Crawl4AI` 代码库保持一致。如需进一步调整，请告知！