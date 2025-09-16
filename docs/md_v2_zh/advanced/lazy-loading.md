## 处理懒加载图片

如今许多网站在滚动时会**懒加载**图片。若需确保它们出现在最终爬取结果（及 `result.media` 中），可考虑：

1. **`wait_for_images=True`** – 等待图片完全加载。  
2. **`scan_full_page`** – 强制爬虫滚动整个页面以触发懒加载。  
3. **`scroll_delay`** – 在滚动步骤间添加短暂延迟。  

**注意**：若网站需要多次触发"加载更多"或复杂交互，请参阅[页面交互文档](../core/page-interaction.md)。对于虚拟滚动（Twitter/Instagram风格）的网站，请查看[虚拟滚动文档](virtual-scroll.md)。

### 示例：确保懒加载图片出现

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from crawl4ai.async_configs import CacheMode

async def main():
    config = CrawlerRunConfig(
        # 强制爬虫等待图片完全加载
        wait_for_images=True,

        # 选项1：若需自动滚动页面加载图片
        scan_full_page=True,  # 指示爬虫尝试滚动整个页面
        scroll_delay=0.5,     # 滚动步骤间的延迟（秒）

        # 选项2：若网站使用"加载更多"或JS触发器加载图片，
        # 可在此指定js_code或wait_for逻辑

        cache_mode=CacheMode.BYPASS,
        verbose=True
    )

    async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
        result = await crawler.arun("https://www.example.com/gallery", config=config)
        
        if result.success:
            images = result.media.get("images", [])
            print("Images found:", len(images))
            for i, img in enumerate(images[:5]):
                print(f"[Image {i}] URL: {img['src']}, Score: {img.get('score','N/A')}")
        else:
            print("Error:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
```

**说明**：

- **`wait_for_images=True`**  
  爬虫会尝试确保图片完成加载后再生成最终HTML。  
- **`scan_full_page=True`**  
  指示爬虫尝试从顶部滚动到底部。每次滚动有助于触发懒加载。  
- **`scroll_delay=0.5`**  
  每次滚动步骤间暂停0.5秒。让网站在继续前完成图片加载。

**适用场景**：

- **懒加载**：若图片仅在用户滚动到视窗内才显示，`scan_full_page` + `scroll_delay` 可帮助爬虫捕获它们。  
- **重型页面**：若页面极长，需注意完整扫描可能较慢。可调整 `scroll_delay` 或最大滚动步数。

---

## 与其他链接和媒体过滤器结合使用

仍可将**懒加载**逻辑与常规的**exclude_external_images**、**exclude_domains**或链接过滤结合：

```python
config = CrawlerRunConfig(
    wait_for_images=True,
    scan_full_page=True,
    scroll_delay=0.5,

    # 若只需本地图片则过滤外部图片
    exclude_external_images=True,

    # 排除特定域名的链接
    exclude_domains=["spammycdn.com"],
)
```

此方法确保捕获主域名的**所有**图片同时忽略外部图片，且爬虫会实际滚动整个页面以触发懒加载。

---

## 技巧与故障排除

1. **长页面**  
   - 在极长或无限滚动页面上设置 `scan_full_page=True` 可能消耗较多资源。  
   - 可考虑使用[钩子](../core/page-interaction.md)或专用逻辑来加载特定区域或重复触发"加载更多"。

2. **混合图片行为**  
   - 部分网站滚动时批量加载图片。若遗漏图片，可增加 `scroll_delay` 或用JS代码/钩子循环调用部分滚动。

3. **与动态等待结合**  
   - 若网站占位图需特定事件后才转为真实图片，可使用 `wait_for="css:img.loaded"` 或自定义JS `wait_for`。

4. **缓存**  
   - 若启用 `cache_mode`，重复爬取可能跳过部分网络请求。若怀疑缓存遗漏新图片，可设 `cache_mode=CacheMode.BYPASS` 强制重新获取。

---

通过**懒加载**支持、**wait_for_images**和**scan_full_page**设置，可捕获预期的完整图片库或信息流——即使网站仅在用户滚动时加载它们。结合标准媒体过滤和域名排除策略，形成完整的链接与媒体处理方案。