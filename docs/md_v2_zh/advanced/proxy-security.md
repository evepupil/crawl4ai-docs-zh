# 代理

## 基础代理设置

使用 `BrowserConfig` 进行简单的代理配置：

```python
from crawl4ai.async_configs import BrowserConfig

# 使用代理 URL
browser_config = BrowserConfig(proxy="http://proxy.example.com:8080")
async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(url="https://example.com")

# 使用 SOCKS 代理
browser_config = BrowserConfig(proxy="socks5://proxy.example.com:1080")
async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(url="https://example.com")
```

## 认证代理

使用带有认证的代理与 `BrowserConfig`：

```python
from crawl4ai.async_configs import BrowserConfig

browser_config = BrowserConfig(proxy="http://[username]:[password]@[host]:[port]")
async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(url="https://example.com")
```

## 轮换代理

动态使用代理轮换服务的示例：

```python
import re
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    RoundRobinProxyStrategy,
)
import asyncio
from crawl4ai import ProxyConfig
async def main():
    # 加载代理并创建轮换策略
    proxies = ProxyConfig.from_env()
    #eg: export PROXIES="ip1:port1:username1:password1,ip2:port2:username2:password2"
    if not proxies:
        print("No proxies found in environment. Set PROXIES env variable!")
        return

    proxy_strategy = RoundRobinProxyStrategy(proxies)

    # 创建配置
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        proxy_rotation_strategy=proxy_strategy
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        urls = ["https://httpbin.org/ip"] * (len(proxies) * 2)  # 每个代理测试两次

        print("\n📈 Initializing crawler with proxy rotation...")
        async with AsyncWebCrawler(config=browser_config) as crawler:
            print("\n🚀 Starting batch crawl with proxy rotation...")
            results = await crawler.arun_many(
                urls=urls,
                config=run_config
            )
            for result in results:
                if result.success:
                    ip_match = re.search(r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}', result.html)
                    current_proxy = run_config.proxy_config if run_config.proxy_config else None

                    if current_proxy and ip_match:
                        print(f"URL {result.url}")
                        print(f"Proxy {current_proxy.server} -> Response IP: {ip_match.group(0)}")
                        verified = ip_match.group(0) == current_proxy.ip
                        if verified:
                            print(f"✅ Proxy working! IP matches: {current_proxy.ip}")
                        else:
                            print("❌ Proxy failed or IP mismatch!")
                    print("---")

asyncio.run(main())

```