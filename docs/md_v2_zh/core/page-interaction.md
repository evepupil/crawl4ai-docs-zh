# 页面交互

Crawl4AI 提供了强大的功能来与**动态**网页进行交互，处理 JavaScript 执行、等待条件和管理多步骤流程。通过结合 **js_code**、**wait_for** 和某些 **CrawlerRunConfig** 参数，您可以：

1. 点击“加载更多”按钮  
2. 填写表单并提交  
3. 等待元素或数据出现  
4. 在多个步骤中复用会话  

以下是快速概述如何实现这些功能。

---

## 1. JavaScript 执行

### 基础执行

**`CrawlerRunConfig`** 中的 **`js_code`** 接受单个 JS 字符串或 JS 片段列表。  
**示例**：我们将滚动到页面底部，然后可选地点击“加载更多”按钮。

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def main():
    # 单个 JS 命令
    config = CrawlerRunConfig(
        js_code="window.scrollTo(0, document.body.scrollHeight);"
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://news.ycombinator.com",  # 示例网站
            config=config
        )
        print("Crawled length:", len(result.cleaned_html))

    # 多个命令
    js_commands = [
        "window.scrollTo(0, document.body.scrollHeight);",
        # Hacker News 上的 'More' 链接
        "document.querySelector('a.morelink')?.click();",  
    ]
    config = CrawlerRunConfig(js_code=js_commands)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://news.ycombinator.com",  # 另一次操作
            config=config
        )
        print("After scroll+click, length:", len(result.cleaned_html))

if __name__ == "__main__":
    asyncio.run(main())
```

**相关 `CrawlerRunConfig` 参数**:
- **`js_code`**: 页面加载后要运行的 JavaScript 字符串或字符串列表。
- **`js_only`**: 如果在后续调用中设置为 `True`，表示我们继续现有会话而不进行新的完整导航。  
- **`session_id`**: 如果您想在多个调用中保持同一页面，请指定一个 ID。

---

## 2. 等待条件

### 2.1 基于 CSS 的等待

有时，您只需要等待特定元素出现。例如：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def main():
    config = CrawlerRunConfig(
        # 等待 Hacker News 上至少 30 个项目
        wait_for="css:.athing:nth-child(30)"  
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://news.ycombinator.com",
            config=config
        )
        print("We have at least 30 items loaded!")
        # 粗略检查
        print("Total items in HTML:", result.cleaned_html.count("athing"))  

if __name__ == "__main__":
    asyncio.run(main())
```

**关键参数**:
- **`wait_for="css:..."`**: 告诉爬虫等待该 CSS 选择器出现。

### 2.2 基于 JavaScript 的等待

对于更复杂的条件（例如等待内容长度超过阈值），使用 `js:` 前缀：

```python
wait_condition = """() => {
    const items = document.querySelectorAll('.athing');
    return items.length > 50;  // 等待至少 51 个项目
}"""

config = CrawlerRunConfig(wait_for=f"js:{wait_condition}")
```

**幕后原理**: Crawl4AI 会持续轮询 JS 函数，直到它返回 `true` 或超时。

---

## 3. 处理动态内容

许多现代网站需要**多个步骤**：滚动、点击“加载更多”或通过 JavaScript 更新。以下是典型模式。

### 3.1 加载更多示例（Hacker News 的“More”链接）

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def main():
    # 步骤 1：加载初始 Hacker News 页面
    config = CrawlerRunConfig(
        wait_for="css:.athing:nth-child(30)"  # 等待 30 个项目
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://news.ycombinator.com",
            config=config
        )
        print("Initial items loaded.")

        # 步骤 2：滚动并点击“More”链接
        load_more_js = [
            "window.scrollTo(0, document.body.scrollHeight);",
            # 页面底部的“More”链接
            "document.querySelector('a.morelink')?.click();"  
        ]
        
        next_page_conf = CrawlerRunConfig(
            js_code=load_more_js,
            wait_for="""js:() => {
                return document.querySelectorAll('.athing').length > 30;
            }""",
            # 标记我们不重新导航，而是在同一会话中运行 JS：
            js_only=True,
            session_id="hn_session"
        )

        # 复用同一爬虫会话
        result2 = await crawler.arun(
            url="https://news.ycombinator.com",  # 相同 URL 但继续会话
            config=next_page_conf
        )
        total_items = result2.cleaned_html.count("athing")
        print("Items after load-more:", total_items)

if __name__ == "__main__":
    asyncio.run(main())
```

**关键参数**:
- **`session_id="hn_session"`**: 在多个 `arun()` 调用中保持同一页面。
- **`js_only=True`**: 我们不执行完整重载，只是在现有页面中应用 JS。
- **`wait_for`** 与 `js:`: 等待项目计数超过 30。

---

### 3.2 表单交互

如果网站有搜索或登录表单，您可以使用 **`js_code`** 填写字段并提交。例如，如果 GitHub 有一个本地搜索表单：

```python
js_form_interaction = """
document.querySelector('#your-search').value = 'TypeScript commits';
document.querySelector('form').submit();
"""

config = CrawlerRunConfig(
    js_code=js_form_interaction,
    wait_for="css:.commit"
)
result = await crawler.arun(url="https://github.com/search", config=config)
```

**实际应用**: 将 ID 或类替换为实际网站的表单选择器。

---

## 4. 时间控制

1. **`page_timeout`** (毫秒): 页面加载或脚本执行的总体时间限制。  
2. **`delay_before_return_html`** (秒): 在捕获最终 HTML 前额外等待一段时间。  
3. **`mean_delay`** 和 **`max_range`**: 如果您使用 `arun_many()` 调用多个 URL，这些参数会在每个请求之间添加随机暂停。

**示例**:

```python
config = CrawlerRunConfig(
    page_timeout=60000,  # 60 秒限制
    delay_before_return_html=2.5
)
```

---

## 5. 多步骤交互示例

以下是一个简化脚本，它在 GitHub 的 TypeScript 提交页面上多次点击“加载更多”。它**复用**同一会话来累积每次的新提交。代码包含您将依赖的相关 **`CrawlerRunConfig`** 参数。

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def multi_page_commits():
    browser_cfg = BrowserConfig(
        headless=False,  # 演示时可见
        verbose=True
    )
    session_id = "github_ts_commits"
    
    base_wait = """js:() => {
        const commits = document.querySelectorAll('li.Box-sc-g0xbh4-0 h4');
        return commits.length > 0;
    }"""

    # 步骤 1：加载初始提交
    config1 = CrawlerRunConfig(
        wait_for=base_wait,
        session_id=session_id,
        cache_mode=CacheMode.BYPASS,
        # 尚未使用 js_only，因为这是首次加载
    )

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(
            url="https://github.com/microsoft/TypeScript/commits/main",
            config=config1
        )
        print("Initial commits loaded. Count:", result.cleaned_html.count("commit"))

        # 步骤 2：对于后续页面，我们运行 JS 点击“下一页”（如果存在）
        js_next_page = """
        const selector = 'a[data-testid="pagination-next-button"]';
        const button = document.querySelector(selector);
        if (button) button.click();
        """
        
        # 等待新提交出现
        wait_for_more = """js:() => {
            const commits = document.querySelectorAll('li.Box-sc-g0xbh4-0 h4');
            if (!window.firstCommit && commits.length>0) {
                window.firstCommit = commits[0].textContent;
                return false;
            }
            // 如果顶部提交发生变化，表示有新提交
            const topNow = commits[0]?.textContent.trim();
            return topNow && topNow !== window.firstCommit;
        }"""

        for page in range(2):  # 再执行 2 次“下一页”
            config_next = CrawlerRunConfig(
                session_id=session_id,
                js_code=js_next_page,
                wait_for=wait_for_more,
                js_only=True,       # 我们从打开的标签页继续
                cache_mode=CacheMode.BYPASS
            )
            result2 = await crawler.arun(
                url="https://github.com/microsoft/TypeScript/commits/main",
                config=config_next
            )
            print(f"Page {page+2} commits count:", result2.cleaned_html.count("commit"))

        # 可选：终止会话
        await crawler.crawler_strategy.kill_session(session_id)

async def main():
    await multi_page_commits()

if __name__ == "__main__":
    asyncio.run(main())
```

**关键点**:

- **`session_id`**: 保持同一页面打开。  
- **`js_code`** + **`wait_for`** + **`js_only=True`**: 我们执行部分刷新，等待新提交出现。  
- **`cache_mode=CacheMode.BYPASS`** 确保每一步都能看到最新数据。

---

## 6. 结合交互与提取

一旦加载了动态内容，您可以附加 **`extraction_strategy`**（如 `JsonCssExtractionStrategy` 或 `LLMExtractionStrategy`）。例如：

```python
from crawl4ai import JsonCssExtractionStrategy

schema = {
    "name": "Commits",
    "baseSelector": "li.Box-sc-g0xbh4-0",
    "fields": [
        {"name": "title", "selector": "h4.markdown-title", "type": "text"}
    ]
}
config = CrawlerRunConfig(
    session_id="ts_commits_session",
    js_code=js_next_page,
    wait_for=wait_for_more,
    extraction_strategy=JsonCssExtractionStrategy(schema)
)
```

完成后，检查 `result.extracted_content` 获取 JSON。

---

## 7. 相关 `CrawlerRunConfig` 参数

以下是 `CrawlerRunConfig` 中与交互相关的关键参数。完整列表请参见[配置参数](../api/parameters.md)。

- **`js_code`**: 初始加载后要运行的 JavaScript。  
- **`js_only`**: 如果为 `True`，不进行新页面导航——仅在现有会话中运行 JS。  
- **`wait_for`**: 等待的 CSS (`"css:..."`) 或 JS (`"js:..."`) 表达式。  
- **`session_id`**: 在多个调用中复用同一页面。  
- **`cache_mode`**: 是否从缓存读取/写入或绕过。  
- **`remove_overlay_elements`**: 自动移除某些弹窗。  
- **`simulate_user`, `override_navigator`, `magic`**: 反机器人或“类人”交互。

---

## 8. 结论

Crawl4AI 的**页面交互**功能让您可以：

1. **执行 JavaScript** 进行滚动、点击或表单填写。  
2. **等待** CSS 或自定义 JS 条件后再捕获数据。  
3. **处理**多步骤流程（如“加载更多”）与部分重载或持久会话。  
4. 结合**结构化提取**处理动态网站。

借助这些工具，您可以自信地抓取现代交互式网页。有关高级钩子、用户模拟或深入配置，请查看[API 参考](../api/parameters.md)或相关高级文档。祝您脚本愉快！

---

## 9. 虚拟滚动

对于使用**虚拟滚动**的网站（内容在滚动时被替换而非追加，如 Twitter 或 Instagram），Crawl4AI 提供了专用的 `VirtualScrollConfig`：

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, VirtualScrollConfig

async def crawl_twitter_timeline():
    # 为类似 Twitter 的 feeds 配置虚拟滚动
    virtual_config = VirtualScrollConfig(
        container_selector="[data-testid='primaryColumn']",  # Twitter 主列
        scroll_count=30,                # 滚动 30 次
        scroll_by="container_height",   # 每次滚动容器高度
        wait_after_scroll=1.0          # 每次滚动后等待 1 秒
    )
    
    config = CrawlerRunConfig(
        virtual_scroll_config=virtual_config
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://twitter.com/search?q=AI",
            config=config
        )
        # result.html 现在包含虚拟滚动的所有推文
```

### 虚拟滚动 vs JavaScript 滚动

| 特性 | 虚拟滚动 | JS 代码滚动 |
|---------|---------------|-------------------|
| **用例** | 滚动时内容被替换 | 内容追加或简单滚动 |
| **配置** | `VirtualScrollConfig` 对象 | 带滚动命令的 `js_code` |
| **自动合并** | 是 - 合并所有唯一内容 | 否 - 仅捕获最终状态 |
| **最适合** | Twitter、Instagram、虚拟表格 | 传统页面、加载更多按钮 |

详细示例和配置选项，请参阅[虚拟滚动文档](../advanced/virtual-scroll.md)。