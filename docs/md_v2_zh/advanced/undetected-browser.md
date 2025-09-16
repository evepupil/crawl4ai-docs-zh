# 无痕浏览模式

## 概述

Crawl4AI 提供两种强大的反检测功能，帮助您访问具有机器人检测机制的网站：

1. **隐身模式** - 使用 playwright-stealth 修改浏览器指纹和行为
2. **无痕浏览模式** - 高级浏览器适配器，提供深度级别的补丁以应对复杂的机器人检测

本指南涵盖这两种功能，并帮助您根据需求选择合适的方法。

## 反检测功能对比

| 功能 | 常规浏览器 | 隐身模式 | 无痕浏览器 |
|---------|----------------|--------------|-------------------|
| WebDriver 检测 | ❌ | ✅ | ✅ |
| Navigator 属性 | ❌ | ✅ | ✅ |
| 插件模拟 | ❌ | ✅ | ✅ |
| CDP 检测 | ❌ | 部分支持 | ✅ |
| 深度浏览器补丁 | ❌ | ❌ | ✅ |
| 性能影响 | 无 | 最小 | 中等 |
| 设置复杂度 | 无 | 无 | 最小 |

## 何时使用每种方法

### 使用常规浏览器 + 隐身模式的情况：
- 网站具有基本的机器人检测（检查 navigator.webdriver、插件等）
- 您需要良好性能与基本保护
- 网站检查常见的自动化指标

### 使用无痕浏览器的情况：
- 网站采用复杂的机器人检测服务（Cloudflare、DataDome 等）
- 仅使用隐身模式不够
- 您愿意牺牲一些性能以获得更好的规避效果

### 最佳实践：渐进式增强
1. **开始使用**：常规浏览器 + 隐身模式
2. **如果被阻止**：切换到无痕浏览器
3. **如果仍然被阻止**：结合无痕浏览器 + 隐身模式

## 隐身模式

隐身模式是更简单的反检测解决方案，可与常规和无痕浏览器一起使用：

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig

# 启用常规浏览器的隐身模式
browser_config = BrowserConfig(
    enable_stealth=True,  # 简单的启用标志
    headless=False       # 更好地避免检测
)

async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun("https://example.com")
```

### 隐身模式的功能：
- 移除 `navigator.webdriver` 标志
- 修改浏览器指纹
- 模拟真实的插件行为
- 调整 navigator 属性
- 修复常见的自动化泄漏

## 无痕浏览模式

对于隐身模式无法绕过的具有复杂机器人检测的网站，请使用无痕浏览器适配器：

### 主要特性

- **即插即用**：使用与常规浏览器模式相同的 API
- **增强隐身**：内置补丁以规避常见的检测方法
- **浏览器适配器模式**：无缝切换常规和无痕模式
- **自动安装**：`crawl4ai-setup` 安装所有必要的浏览器依赖项

### 快速开始

```python
import asyncio
from crawl4ai import (
    AsyncWebCrawler, 
    BrowserConfig, 
    CrawlerRunConfig,
    UndetectedAdapter
)
from crawl4ai.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy

async def main():
    # 创建无痕适配器
    undetected_adapter = UndetectedAdapter()
    
    # 创建浏览器配置
    browser_config = BrowserConfig(
        headless=False,  # 无头模式更容易被检测
        verbose=True,
    )
    
    # 使用无痕适配器创建爬虫策略
    crawler_strategy = AsyncPlaywrightCrawlerStrategy(
        browser_config=browser_config,
        browser_adapter=undetected_adapter
    )
    
    # 使用自定义策略创建爬虫
    async with AsyncWebCrawler(
        crawler_strategy=crawler_strategy,
        config=browser_config
    ) as crawler:
        # 在此处编写爬取代码
        result = await crawler.arun(
            url="https://example.com",
            config=CrawlerRunConfig()
        )
        print(result.markdown[:500])

asyncio.run(main())
```

## 结合两种功能

为了最大程度地规避检测，请将隐身模式与无痕浏览器结合使用：

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, UndetectedAdapter
from crawl4ai.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy

# 创建启用隐身的浏览器配置
browser_config = BrowserConfig(
    enable_stealth=True,  # 启用隐身模式
    headless=False
)

# 创建无痕适配器
adapter = UndetectedAdapter()

# 创建包含两种功能的策略
strategy = AsyncPlaywrightCrawlerStrategy(
    browser_config=browser_config,
    browser_adapter=adapter
)

async with AsyncWebCrawler(
    crawler_strategy=strategy,
    config=browser_config
) as crawler:
    result = await crawler.arun("https://protected-site.com")
```

## 示例

### 示例 1：基本隐身模式

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def test_stealth_mode():
    # 简单的隐身模式配置
    browser_config = BrowserConfig(
        enable_stealth=True,
        headless=False
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://bot.sannysoft.com",
            config=CrawlerRunConfig(screenshot=True)
        )
        
        if result.success:
            print("✓ 成功访问机器人检测测试网站")
            # 保存截图以验证检测结果
            if result.screenshot:
                import base64
                with open("stealth_test.png", "wb") as f:
                    f.write(base64.b64decode(result.screenshot))
                print("✓ 截图已保存 - 检查绿色（通过）的测试")

asyncio.run(test_stealth_mode())
```

### 示例 2：无痕浏览模式

```python
import asyncio
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    UndetectedAdapter
)
from crawl4ai.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy


async def main():
    # 创建浏览器配置
    browser_config = BrowserConfig(
        headless=False,
        verbose=True,
    )
    
    # 创建无痕适配器
    undetected_adapter = UndetectedAdapter()
    
    # 使用无痕适配器创建爬虫策略
    crawler_strategy = AsyncPlaywrightCrawlerStrategy(
        browser_config=browser_config,
        browser_adapter=undetected_adapter
    )
    
    # 使用自定义策略创建爬虫
    async with AsyncWebCrawler(
        crawler_strategy=crawler_strategy,
        config=browser_config
    ) as crawler:
        # 配置爬取参数
        crawler_config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter()
            ),
            capture_console_messages=True,  # 测试适配器控制台捕获
        )
        
        # 在通常检测机器人的网站上测试
        print("测试无痕适配器...")
        result: CrawlResult = await crawler.arun(
            url="https://www.helloworld.org", 
            config=crawler_config
        )
        
        print(f"状态: {result.status_code}")
        print(f"成功: {result.success}")
        print(f"捕获的控制台消息: {len(result.console_messages or [])}")
        print(f"Markdown 内容 (前500字符):\n{result.markdown.raw_markdown[:500]}")


if __name__ == "__main__":
    asyncio.run(main())
```

## 浏览器适配器模式

无痕浏览器支持使用适配器模式实现，允许在不同浏览器实现之间无缝切换：

```python
# 常规浏览器适配器（默认）
from crawl4ai import PlaywrightAdapter
regular_adapter = PlaywrightAdapter()

# 无痕浏览器适配器
from crawl4ai import UndetectedAdapter
undetected_adapter = UndetectedAdapter()
```

适配器处理：
- JavaScript 执行
- 控制台消息捕获
- 错误处理
- 浏览器特定优化

## 最佳实践

1. **避免无头模式**：无头模式更容易被检测
   ```python
   browser_config = BrowserConfig(headless=False)
   ```

2. **使用合理的延迟**：不要快速浏览页面
   ```python
   crawler_config = CrawlerRunConfig(
       wait_time=3.0,  # 页面加载后等待3秒
       delay_before_return_html=2.0  # 额外延迟
   )
   ```

3. **轮换 User Agent**：您可以自定义用户代理
   ```python
   browser_config = BrowserConfig(
       headers={"User-Agent": "your-user-agent"}
   )
   ```

4. **优雅处理失败**：某些网站可能仍然检测并阻止
   ```python
   if not result.success:
       print(f"爬取失败: {result.error_message}")
   ```

## 高级使用技巧

### 渐进式检测处理

```python
async def crawl_with_progressive_evasion(url):
    # 步骤 1：尝试常规浏览器 + 隐身
    browser_config = BrowserConfig(
        enable_stealth=True,
        headless=False
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url)
        if result.success and "Access Denied" not in result.html:
            return result
    
    # 步骤 2：如果被阻止，尝试无痕浏览器
    print("常规 + 隐身被阻止，尝试无痕浏览器...")
    
    adapter = UndetectedAdapter()
    strategy = AsyncPlaywrightCrawlerStrategy(
        browser_config=browser_config,
        browser_adapter=adapter
    )
    
    async with AsyncWebCrawler(
        crawler_strategy=strategy,
        config=browser_config
    ) as crawler:
        result = await crawler.arun(url)
        return result
```

## 安装

无痕浏览器依赖项会在您运行以下命令时自动安装：

```bash
crawl4ai-setup
```

此命令安装常规和无痕模式所需的所有浏览器依赖项。

## 限制

- **性能**：由于额外的补丁，比常规模式稍慢
- **无头检测**：某些网站仍然可以检测无头模式
- **资源使用**：可能比常规模式使用更多资源
- **并非100%保证**：高级反机器人服务不断演进

## 故障排除

### 浏览器未找到

运行设置命令：
```bash
crawl4ai-setup
```

### 仍然被检测到

尝试结合其他功能：
```python
crawler_config = CrawlerRunConfig(
    simulate_user=True,  # 添加用户模拟
    magic=True,  # 启用魔法模式
    wait_time=5.0,  # 更长的等待时间
)
```

### 性能问题

如果遇到性能缓慢：
```python
# 仅对受保护的站点使用选择性无痕模式
if is_protected_site(url):
    adapter = UndetectedAdapter()
else:
    adapter = PlaywrightAdapter()  # 默认适配器
```

## 未来计划

**注意**：在 Crawl4AI 的未来版本中，我们可能会默认启用隐身模式和无痕浏览器，以提供更好的开箱即用成功率。目前，用户应在需要时显式启用这些功能。

## 结论

Crawl4AI 提供灵活的反检测解决方案：

1. **从简单开始**：对大多数网站使用常规浏览器 + 隐身模式
2. **需要时升级**：对复杂保护切换到无痕浏览器
3. **结合以获得最大效果**：面对最严峻挑战时同时使用两种功能

请记住：
- 始终尊重 robots.txt 和网站服务条款
- 使用适当的延迟以避免压垮服务器
- 考虑每种方法的性能权衡
- 逐步测试以找到必要的最小规避级别

## 另请参阅

- [高级功能](advanced-features.md) - 所有高级功能的概述
- [代理与安全](proxy-security.md) - 将代理与反检测功能结合使用
- [会话管理](session-management.md) - 跨请求维护会话
- [基于身份的爬取](identity-based-crawling.md) - 额外的反检测策略