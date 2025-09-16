# Crawl4AI 缓存系统与迁移指南

## 概述
从版本 0.5.0 开始，Crawl4AI 引入了全新的缓存系统，用更直观的 `CacheMode` 枚举替代了旧的布尔标志。这一变更简化了缓存控制，并使行为更加可预测。

## 新旧方案对比

### 旧方案（已弃用）
旧系统使用多个布尔标志：
- `bypass_cache`: 完全跳过缓存
- `disable_cache`: 禁用所有缓存
- `no_cache_read`: 不从缓存读取
- `no_cache_write`: 不写入缓存

### 新方案（推荐）
新系统使用单一的 `CacheMode` 枚举：
- `CacheMode.ENABLED`: 正常缓存（读取/写入）
- `CacheMode.DISABLED`: 完全禁用缓存
- `CacheMode.READ_ONLY`: 仅从缓存读取
- `CacheMode.WRITE_ONLY`: 仅写入缓存
- `CacheMode.BYPASS`: 跳过本次操作的缓存

## 迁移示例

### 旧代码（已弃用）
```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def use_proxy():
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url="https://www.nbcnews.com/business",
            bypass_cache=True  # Old way
        )
        print(len(result.markdown))

async def main():
    await use_proxy()

if __name__ == "__main__":
    asyncio.run(main())
```

### 新代码（推荐）
```python
import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.async_configs import CrawlerRunConfig

async def use_proxy():
    # Use CacheMode in CrawlerRunConfig
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)  
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url="https://www.nbcnews.com/business",
            config=config  # Pass the configuration object
        )
        print(len(result.markdown))

async def main():
    await use_proxy()

if __name__ == "__main__":
    asyncio.run(main())
```

## 常见迁移模式

| 旧标志                | 新模式                         |
|-----------------------|---------------------------------|
| `bypass_cache=True`   | `cache_mode=CacheMode.BYPASS`  |
| `disable_cache=True`  | `cache_mode=CacheMode.DISABLED`|
| `no_cache_read=True`  | `cache_mode=CacheMode.WRITE_ONLY` |
| `no_cache_write=True` | `cache_mode=CacheMode.READ_ONLY` |