# AsyncWebCrawler 中的钩子与认证

Crawl4AI 的**钩子**允许您在爬取流程的特定节点自定义爬虫行为：

1. **`on_browser_created`** – 浏览器实例创建后触发  
2. **`on_page_context_created`** – 新上下文和页面创建后触发  
3. **`before_goto`** – 页面导航前触发  
4. **`after_goto`** – 页面导航完成后触发  
5. **`on_user_agent_updated`** – 用户代理变更时触发  
6. **`on_execution_started`** – 自定义JavaScript执行开始时触发  
7. **`before_retrieve_html`** – 获取最终HTML前触发  
8. **`before_return_html`** – 返回HTML内容前触发

**重要提示**：避免在`on_browser_created`中执行繁重任务，因为此时尚未创建页面上下文。如需*登录*操作，请在**`on_page_context_created`**中进行。

> note "钩子使用重要警告"
    **避免错误使用钩子**：不要在错误的钩子或错误的时间操作页面对象，否则可能导致流程崩溃或结果错误。常见错误是在`on_browser_created`中过早处理认证——例如创建或关闭页面。

>   **使用正确的钩子进行认证**：如需登录或设置令牌，请使用`on_page_context_created`。这确保您拥有有效的页面/上下文进行操作，同时不影响主爬取流程。

>    **基于身份的爬取**：要实现健壮的认证，建议采用基于身份的爬取（或传递会话ID）来保持状态。将初始登录步骤放在独立的明确定义流程中执行，然后将该会话提供给主爬取流程——而不是在早期钩子中强行处理复杂认证。详见[基于身份的爬取](../advanced/identity-based-crawling.md)。

>    **谨慎操作**：在错误的钩子中覆盖或删除元素可能影响最终爬取结果。保持钩子专注于小任务（如路由过滤、自定义头信息），让主逻辑（爬取、数据提取）正常进行。


以下是示例演示。

---

## 示例：在AsyncWebCrawler中使用钩子

```python
import asyncio
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from playwright.async_api import Page, BrowserContext

async def main():
    print("🔗 钩子示例：演示推荐用法")

    # 1) 配置浏览器
    browser_config = BrowserConfig(
        headless=True,
        verbose=True
    )

    # 2) 配置爬取运行参数
    crawler_run_config = CrawlerRunConfig(
        js_code="window.scrollTo(0, document.body.scrollHeight);",
        wait_for="body",
        cache_mode=CacheMode.BYPASS
    )

    # 3) 创建爬虫实例
    crawler = AsyncWebCrawler(config=browser_config)

    #
    # 定义钩子函数
    #

    async def on_browser_created(browser, **kwargs):
        # 浏览器实例创建后调用（此时尚无页面或上下文）
        print("[钩子] on_browser_created - 浏览器创建成功！")
        # 通常在此处进行最小化设置（如有需要）
        return browser

    async def on_page_context_created(page: Page, context: BrowserContext, **kwargs):
        # 新页面+上下文创建后立即调用（适合认证或路由配置）
        print("[钩子] on_page_context_created - 设置页面和上下文。")
        
        # 示例1：路由过滤（如阻止图片）
        async def route_filter(route):
            if route.request.resource_type == "image":
                print(f"[钩子] 阻止图片请求: {route.request.url}")
                await route.abort()
            else:
                await route.continue_()

        await context.route("**", route_filter)

        # 示例2：（可选）模拟登录场景
        # （注意：此处不创建或关闭页面，仅执行必要步骤）
        # 例如：await page.goto("https://example.com/login")
        # 例如：await page.fill("input[name='username']", "testuser")
        # 例如：await page.fill("input[name='password']", "password123")
        # 例如：await page.click("button[type='submit']")
        # 例如：await page.wait_for_selector("#welcome")
        # 例如：await context.add_cookies([...])
        # 然后继续

        # 示例3：调整视口
        await page.set_viewport_size({"width": 1080, "height": 600})
        return page

    async def before_goto(
        page: Page, context: BrowserContext, url: str, **kwargs
    ):
        # 导航到每个URL前调用
        print(f"[钩子] before_goto - 即将导航至: {url}")
        # 例如：注入自定义头信息
        await page.set_extra_http_headers({
            "Custom-Header": "my-value"
        })
        return page

    async def after_goto(
        page: Page, context: BrowserContext, 
        url: str, response, **kwargs
    ):
        # 导航完成后调用
        print(f"[钩子] after_goto - 成功加载: {url}")
        # 例如：等待特定元素以验证
        try:
            await page.wait_for_selector('.content', timeout=1000)
            print("[钩子] 找到.content元素！")
        except:
            print("[钩子] 未找到.content元素，继续执行。")
        return page

    async def on_user_agent_updated(
        page: Page, context: BrowserContext, 
        user_agent: str, **kwargs
    ):
        # 用户代理更新时调用
        print(f"[钩子] on_user_agent_updated - 新用户代理: {user_agent}")
        return page

    async def on_execution_started(page: Page, context: BrowserContext, **kwargs):
        # 自定义JavaScript开始执行后调用
        print("[钩子] on_execution_started - JS代码正在运行！")
        return page

    async def before_retrieve_html(page: Page, context: BrowserContext, **kwargs):
        # 获取最终HTML前调用
        print("[钩子] before_retrieve_html - 可执行最终操作")
        # 示例：再次滚动
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        return page

    async def before_return_html(
        page: Page, context: BrowserContext, html: str, **kwargs
    ):
        # 返回结果中的HTML前调用
        print(f"[钩子] before_return_html - HTML长度: {len(html)}")
        return page

    #
    # 附加钩子
    #

    crawler.crawler_strategy.set_hook("on_browser_created", on_browser_created)
    crawler.crawler_strategy.set_hook(
        "on_page_context_created", on_page_context_created
    )
    crawler.crawler_strategy.set_hook("before_goto", before_goto)
    crawler.crawler_strategy.set_hook("after_goto", after_goto)
    crawler.crawler_strategy.set_hook(
        "on_user_agent_updated", on_user_agent_updated
    )
    crawler.crawler_strategy.set_hook(
        "on_execution_started", on_execution_started
    )
    crawler.crawler_strategy.set_hook(
        "before_retrieve_html", before_retrieve_html
    )
    crawler.crawler_strategy.set_hook(
        "before_return_html", before_return_html
    )

    await crawler.start()

    # 4) 在示例页面上运行爬虫
    url = "https://example.com"
    result = await crawler.arun(url, config=crawler_run_config)
    
    if result.success:
        print("\n已爬取URL:", result.url)
        print("HTML长度:", len(result.html))
    else:
        print("错误:", result.error_message)

    await crawler.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 钩子生命周期总结

1. **`on_browser_created`**:  
   - 浏览器已启动，但**尚无**页面或上下文  
   - 仅进行轻量设置——不要尝试在此处打开或关闭页面（这属于`on_page_context_created`的职责）

2. **`on_page_context_created`**:  
   - 最适合处理高级**认证**或路由拦截  
   - 此时**页面**+**上下文**已就绪，但尚未导航至目标URL

3. **`before_goto`**:  
   - 导航前触发。通常用于设置**自定义头信息**或记录目标URL

4. **`after_goto`**:  
   - 页面导航完成后触发。适合验证内容或等待关键元素  

5. **`on_user_agent_updated`**:  
   - 用户代理变更时触发（用于隐身模式或不同UA模式）

6. **`on_execution_started`**:  
   - 当设置`js_code`或运行自定义脚本时，在JS即将开始时触发

7. **`before_retrieve_html`**:  
   - 获取最终HTML快照前触发。通常在此处执行最终滚动或触发懒加载

8. **`before_return_html`**:  
   - 返回HTML到`CrawlResult`前的最后钩子。适合记录HTML长度或进行小修改

---

## 认证处理时机

**推荐**：在**`on_page_context_created`**中进行以下操作：

- 导航至登录页面或填写表单
- 设置cookies或localStorage令牌
- 拦截资源路由以避免广告

这确保在`arun()`导航至主URL前，新创建的上下文已处于您的控制之下。

---

## 其他注意事项

- **会话管理**：如需多个`arun()`调用复用同一会话，请在`CrawlerRunConfig`中传递`session_id=`。钩子保持不变。  
- **性能**：钩子执行繁重任务可能降低爬取速度。保持简洁。  
- **错误处理**：钩子失败可能导致整个爬取失败。捕获异常或优雅处理。  
- **并发**：运行`arun_many()`时，每个URL都会并行触发这些钩子。确保钩子是线程/异步安全的。

---

## 结论

钩子提供**细粒度**控制：

- **浏览器**创建（仅轻量任务）
- **页面**和**上下文**创建（认证、路由拦截）
- **导航**阶段
- **最终HTML**获取

遵循推荐用法：
- **登录**或高级任务放在`on_page_context_created`  
- **自定义头信息**或日志放在`before_goto`/`after_goto`  
- **滚动**或最终检查放在`before_retrieve_html`/`before_return_html`