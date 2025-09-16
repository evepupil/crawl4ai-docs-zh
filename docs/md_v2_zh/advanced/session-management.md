# 会话管理

Crawl4AI 中的会话管理是一项强大功能，允许您在多个请求之间保持状态，特别适合处理复杂的多步骤爬取任务。它使您能够在连续操作和爬取中重复使用同一个浏览器标签页（或页面对象），这对于以下场景尤为有益：

- **在爬取前后执行 JavaScript 操作**
- **更快地执行连续多次爬取**，无需重复打开标签页或分配内存

**注意：** 此功能专为顺序工作流设计，不适用于并行操作。

---

#### 基础会话使用

使用 `BrowserConfig` 和 `CrawlerRunConfig` 通过 `session_id` 保持状态：

```python
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

async with AsyncWebCrawler() as crawler:
    session_id = "my_session"

    # 定义配置
    config1 = CrawlerRunConfig(
        url="https://example.com/page1", session_id=session_id
    )
    config2 = CrawlerRunConfig(
        url="https://example.com/page2", session_id=session_id
    )

    # 首次请求
    result1 = await crawler.arun(config=config1)

    # 使用相同会话的后续请求
    result2 = await crawler.arun(config=config2)

    # 完成后清理
    await crawler.crawler_strategy.kill_session(session_id)
```

---

#### 动态内容与会话

以下是通过会话状态爬取 GitHub 多页提交记录的示例：

```python
from crawl4ai.async_configs import CrawlerRunConfig
from crawl4ai import JsonCssExtractionStrategy
from crawl4ai.cache_context import CacheMode

async def crawl_dynamic_content():
    url = "https://github.com/microsoft/TypeScript/commits/main"
    session_id = "wait_for_session"
    all_commits = []

    js_next_page = """
    const commits = document.querySelectorAll('li[data-testid="commit-row-item"] h4');
    if (commits.length > 0) {
        window.lastCommit = commits[0].textContent.trim();
    }
    const button = document.querySelector('a[data-testid="pagination-next-button"]');
    if (button) {button.click(); console.log('button clicked') }
    """

    wait_for = """() => {
        const commits = document.querySelectorAll('li[data-testid="commit-row-item"] h4');
        if (commits.length === 0) return false;
        const firstCommit = commits[0].textContent.trim();
        return firstCommit !== window.lastCommit;
    }"""
    
    schema = {
        "name": "Commit Extractor",
        "baseSelector": "li[data-testid='commit-row-item']",
        "fields": [
            {
                "name": "title",
                "selector": "h4 a",
                "type": "text",
                "transform": "strip",
            },
        ],
    }
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)
    
    
    browser_config = BrowserConfig(
        verbose=True,
        headless=False,
    )
        
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for page in range(3):
            crawler_config = CrawlerRunConfig(
                session_id=session_id,
                css_selector="li[data-testid='commit-row-item']",
                extraction_strategy=extraction_strategy,
                js_code=js_next_page if page > 0 else None,
                wait_for=wait_for if page > 0 else None,
                js_only=page > 0,
                cache_mode=CacheMode.BYPASS,
                capture_console_messages=True,
            )
            
            result = await crawler.arun(url=url, config=crawler_config)
            
            if result.console_messages:
                print(f"Page {page + 1} console messages:", result.console_messages)
            
            if result.extracted_content:
                # print(f"Page {page + 1} result:", result.extracted_content)
                commits = json.loads(result.extracted_content)
                all_commits.extend(commits)
                print(f"Page {page + 1}: Found {len(commits)} commits")
            else:
                print(f"Page {page + 1}: No content extracted")

        print(f"Successfully crawled {len(all_commits)} commits across 3 pages")
        # 清理会话
        await crawler.crawler_strategy.kill_session(session_id)
```

---

## 示例1：基础会话爬取

使用会话爬取的简单示例：

```python
import asyncio
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from crawl4ai.cache_context import CacheMode

async def basic_session_crawl():
    async with AsyncWebCrawler() as crawler:
        session_id = "dynamic_content_session"
        url = "https://example.com/dynamic-content"

        for page in range(3):
            config = CrawlerRunConfig(
                url=url,
                session_id=session_id,
                js_code="document.querySelector('.load-more-button').click();" if page > 0 else None,
                css_selector=".content-item",
                cache_mode=CacheMode.BYPASS
            )
            
            result = await crawler.arun(config=config)
            print(f"Page {page + 1}: Found {result.extracted_content.count('.content-item')} items")

        await crawler.crawler_strategy.kill_session(session_id)

asyncio.run(basic_session_crawl())
```

此示例展示：
1. 在多个请求间复用相同的 `session_id`
2. 执行 JavaScript 动态加载更多内容
3. 正确关闭会话释放资源

---

## 高级技巧1：自定义执行钩子

> 警告：接下来的几个示例可能会让您感到困惑 😅，请确保您已熟悉前面的内容再继续。

使用自定义钩子处理复杂场景，例如等待动态内容加载：

```python
async def advanced_session_crawl_with_hooks():
    first_commit = ""

    async def on_execution_started(page):
        nonlocal first_commit
        try:
            while True:
                await page.wait_for_selector("li.commit-item h4")
                commit = await page.query_selector("li.commit-item h4")
                commit = await commit.evaluate("(element) => element.textContent").strip()
                if commit and commit != first_commit:
                    first_commit = commit
                    break
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Warning: New content didn't appear: {e}")

    async with AsyncWebCrawler() as crawler:
        session_id = "commit_session"
        url = "https://github.com/example/repo/commits/main"
        crawler.crawler_strategy.set_hook("on_execution_started", on_execution_started)

        js_next_page = """document.querySelector('a.pagination-next').click();"""

        for page in range(3):
            config = CrawlerRunConfig(
                url=url,
                session_id=session_id,
                js_code=js_next_page if page > 0 else None,
                css_selector="li.commit-item",
                js_only=page > 0,
                cache_mode=CacheMode.BYPASS
            )

            result = await crawler.arun(config=config)
            print(f"Page {page + 1}: Found {len(result.extracted_content)} commits")

        await crawler.crawler_strategy.kill_session(session_id)

asyncio.run(advanced_session_crawl_with_hooks())
```

此技术确保新内容在下次操作前完成加载。

---

## 高级技巧2：集成JavaScript执行与等待

结合JavaScript执行和等待逻辑，简洁处理动态内容：

```python
async def integrated_js_and_wait_crawl():
    async with AsyncWebCrawler() as crawler:
        session_id = "integrated_session"
        url = "https://github.com/example/repo/commits/main"

        js_next_page_and_wait = """
        (async () => {
            const getCurrentCommit = () => document.querySelector('li.commit-item h4').textContent.trim();
            const initialCommit = getCurrentCommit();
            document.querySelector('a.pagination-next').click();
            while (getCurrentCommit() === initialCommit) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        })();
        """

        for page in range(3):
            config = CrawlerRunConfig(
                url=url,
                session_id=session_id,
                js_code=js_next_page_and_wait if page > 0 else None,
                css_selector="li.commit-item",
                js_only=page > 0,
                cache_mode=CacheMode.BYPASS
            )

            result = await crawler.arun(config=config)
            print(f"Page {page + 1}: Found {len(result.extracted_content)} commits")

        await crawler.crawler_strategy.kill_session(session_id)

asyncio.run(integrated_js_and_wait_crawl())
```

---

#### 会话的常见用例

1. **认证流程**：登录并与受保护页面交互

2. **分页处理**：浏览多页内容

3. **表单提交**：填写表单、提交并处理结果

4. **多步骤流程**：完成跨多个操作的工作流

5. **动态内容导航**：处理JavaScript渲染或事件触发的内容