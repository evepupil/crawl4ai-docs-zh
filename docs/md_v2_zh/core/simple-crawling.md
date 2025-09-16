# 简易爬虫指南

本文档介绍使用 Crawl4AI 进行网页爬取的基础知识。您将学习如何设置爬虫、发起首次请求以及理解返回结果。

## 基础用法

使用 `BrowserConfig` 和 `CrawlerRunConfig` 设置简单爬取：

```python
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

async def main():
    browser_config = BrowserConfig()  # 默认浏览器配置
    run_config = CrawlerRunConfig()   # 默认爬取运行配置

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://example.com",
            config=run_config
        )
        print(result.markdown)  # 打印清理后的markdown内容

if __name__ == "__main__":
    asyncio.run(main())
```

## 理解返回结果

`arun()` 方法返回一个包含多个有用属性的 `CrawlResult` 对象。以下是简要概述（完整详情请参阅 [CrawlResult](../api/crawl-result.md)）：

```python
config = CrawlerRunConfig(
    markdown_generator=DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=0.6),
        options={"ignore_links": True}
    )
)

result = await crawler.arun(
    url="https://example.com",
    config=config
)

# 不同内容格式
print(result.html)         # 原始HTML
print(result.cleaned_html) # 清理后的HTML
print(result.markdown.raw_markdown) # 从清理后HTML生成的原始markdown
print(result.markdown.fit_markdown) # markdown中最相关的内容

# 检查成功状态
print(result.success)      # 爬取成功则为True
print(result.status_code)  # HTTP状态码(如200, 404)

# 访问提取的媒体和链接
print(result.media)        # 找到的媒体字典(图片、视频、音频)
print(result.links)        # 内部和外部链接字典
```

## 添加基础选项

使用 `CrawlerRunConfig` 自定义爬取：

```python
run_config = CrawlerRunConfig(
    word_count_threshold=10,        # 每个内容块的最小字数
    exclude_external_links=True,    # 移除外部链接
    remove_overlay_elements=True,   # 移除弹窗/模态框
    process_iframes=True           # 处理iframe内容
)

result = await crawler.arun(
    url="https://example.com",
    config=run_config
)
```

## 错误处理

始终检查爬取是否成功：

```python
run_config = CrawlerRunConfig()
result = await crawler.arun(url="https://example.com", config=run_config)

if not result.success:
    print(f"爬取失败: {result.error_message}")
    print(f"状态码: {result.status_code}")
```

## 日志与调试

在 `BrowserConfig` 中启用详细日志：

```python
browser_config = BrowserConfig(verbose=True)

async with AsyncWebCrawler(config=browser_config) as crawler:
    run_config = CrawlerRunConfig()
    result = await crawler.arun(url="https://example.com", config=run_config)
```

## 完整示例

以下是展示常见使用模式的更全面示例：

```python
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode

async def main():
    browser_config = BrowserConfig(verbose=True)
    run_config = CrawlerRunConfig(
        # 内容过滤
        word_count_threshold=10,
        excluded_tags=['form', 'header'],
        exclude_external_links=True,
        
        # 内容处理
        process_iframes=True,
        remove_overlay_elements=True,
        
        # 缓存控制
        cache_mode=CacheMode.ENABLED  # 如果可用则使用缓存
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://example.com",
            config=run_config
        )
        
        if result.success:
            # 打印清理后的内容
            print("内容:", result.markdown[:500])  # 前500个字符
            
            # 处理图片
            for image in result.media["images"]:
                print(f"找到图片: {image['src']}")
            
            # 处理链接
            for link in result.links["internal"]:
                print(f"内部链接: {link['href']}")
                
        else:
            print(f"爬取失败: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
```