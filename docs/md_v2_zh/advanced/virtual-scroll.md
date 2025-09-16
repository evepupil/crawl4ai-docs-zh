# 虚拟滚动

现代网站越来越多地使用**虚拟滚动**（也称为窗口化渲染或视口渲染）来高效处理大型数据集。这种技术只在DOM中渲染可见项，随着用户滚动替换内容。流行的例子包括Twitter的时间线、Instagram的feed和许多数据表格。

Crawl4AI的虚拟滚动功能自动检测并处理这些场景，确保您捕获**所有内容**，而不仅仅是初始可见的部分。

## 理解虚拟滚动

### 问题

传统的无限滚动**追加**新内容到现有内容。虚拟滚动**替换**内容以保持性能：

```
传统滚动:          虚拟滚动:
┌─────────────┐             ┌─────────────┐
│ 项目1       │             │ 项目11      │  <- 项目1-10已被移除
│ 项目2       │             │ 项目12      │  <- 只有可见项目
│ ...         │             │ 项目13      │     在DOM中
│ 项目10      │             │ 项目14      │
│ 项目11 新增 │             │ 项目15      │
│ 项目12 新增 │             └─────────────┘
└─────────────┘             
DOM持续增长                DOM大小保持恒定
```

如果没有正确处理，爬虫只能捕获当前可见的项目，错过其余内容。

### 三种滚动场景

Crawl4AI的虚拟滚动检测并处理三种场景：

1. **无变化** - 滚动时内容不更新（静态页面或已到达末尾）
2. **内容追加** - 新项目添加到现有项目中（传统无限滚动）  
3. **内容替换** - 项目被新项目替换（真正的虚拟滚动）

只有场景3需要特殊处理，虚拟滚动会自动完成。

## 基本用法

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, VirtualScrollConfig

# 配置虚拟滚动
virtual_config = VirtualScrollConfig(
    container_selector="#feed",      # 可滚动容器的CSS选择器
    scroll_count=20,                 # 要执行的滚动次数
    scroll_by="container_height",    # 每次滚动的距离
    wait_after_scroll=0.5           # 每次滚动后的等待时间（秒）
)

# 在爬虫配置中使用
config = CrawlerRunConfig(
    virtual_scroll_config=virtual_config
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url="https://example.com", config=config)
    # result.html包含来自虚拟滚动的所有项目
```

## 配置参数

### VirtualScrollConfig

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `container_selector` | `str` | 必需 | 可滚动容器的CSS选择器 |
| `scroll_count` | `int` | `10` | 要执行的最大滚动次数 |
| `scroll_by` | `str` 或 `int` | `"container_height"` | 每次滚动的距离 |
| `wait_after_scroll` | `float` | `0.5` | 每次滚动后等待的秒数 |

### 滚动距离选项

- `"container_height"` - 按容器的可见高度滚动
- `"page_height"` - 按视口高度滚动
- `500` (整数) - 按精确像素距离滚动

## 实际示例

### 类似Twitter的时间线

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, VirtualScrollConfig, BrowserConfig

async def crawl_twitter_timeline():
    # Twitter在滚动时替换推文
    virtual_config = VirtualScrollConfig(
        container_selector="[data-testid='primaryColumn']",
        scroll_count=30,
        scroll_by="container_height",
        wait_after_scroll=1.0  # Twitter需要时间加载
    )
    
    browser_config = BrowserConfig(headless=True)  # 设置为False可以观察运行过程
    config = CrawlerRunConfig(
        virtual_scroll_config=virtual_config
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://twitter.com/search?q=AI",
            config=config
        )
        
        # 提取推文数量
        import re
        tweets = re.findall(r'data-testid="tweet"', result.html)
        print(f"捕获了 {len(tweets)} 条推文")
```

### Instagram网格

```python
async def crawl_instagram_grid():
    # Instagram使用虚拟化网格提高性能
    virtual_config = VirtualScrollConfig(
        container_selector="article",  # 主feed容器
        scroll_count=50,               # 网格布局需要更多滚动
        scroll_by=800,                 # 固定像素滚动
        wait_after_scroll=0.8
    )
    
    config = CrawlerRunConfig(
        virtual_scroll_config=virtual_config,
        screenshot=True  # 捕获最终状态
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.instagram.com/explore/tags/photography/",
            config=config
        )
        
        # 计算帖子数量
        posts = result.html.count('class="post"')
        print(f"从虚拟化网格中捕获了 {posts} 个帖子")
```

### 混合内容（新闻feed）

有些网站混合了静态和虚拟化内容：

```python
async def crawl_mixed_feed():
    # 特色文章保持不动，常规文章虚拟化
    virtual_config = VirtualScrollConfig(
        container_selector=".main-feed",
        scroll_count=25,
        scroll_by="container_height",
        wait_after_scroll=0.5
    )
    
    config = CrawlerRunConfig(
        virtual_scroll_config=virtual_config
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://news.example.com",
            config=config
        )
        
        # 特色文章在整个过程中保持不变
        featured = result.html.count('class="featured-article"')
        regular = result.html.count('class="regular-article"')
        
        print(f"特色文章（静态）: {featured}")
        print(f"常规文章（虚拟化）: {regular}")
```

## 虚拟滚动 vs scan_full_page

两种功能都处理动态内容，但用途不同：

| 功能 | 虚拟滚动 | scan_full_page |
|---------|---------------|----------------|
| **目的** | 捕获滚动时被替换的内容 | 加载滚动时追加的内容 |
| **用例** | Twitter、Instagram、虚拟表格 | 传统无限滚动、懒加载图片 |
| **DOM行为** | 替换元素 | 添加元素 |
| **内存使用** | 高效（合并内容） | 可能变得很大 |
| **配置** | 需要容器选择器 | 适用于整个页面 |

### 何时使用哪种？

使用**虚拟滚动**当：
- 内容在滚动时消失（Twitter时间线）
- DOM元素数量保持相对恒定
- 需要虚拟化列表中的所有项目
- 基于容器的滚动（非全页）

使用**scan_full_page**当：
- 内容在滚动时累积
- 图片懒加载
- 简单的"加载更多"行为
- 全页滚动

## 与提取功能结合

虚拟滚动与提取策略无缝协作：

```python
from crawl4ai import LLMExtractionStrategy, LLMConfig

# 定义提取模式
schema = {
    "type": "array",
    "items": {
        "type": "object", 
        "properties": {
            "author": {"type": "string"},
            "content": {"type": "string"},
            "timestamp": {"type": "string"}
        }
    }
}

# 同时配置虚拟滚动和提取
config = CrawlerRunConfig(
    virtual_scroll_config=VirtualScrollConfig(
        container_selector="#timeline",
        scroll_count=20
    ),
    extraction_strategy=LLMExtractionStrategy(
        llm_config=LLMConfig(provider="openai/gpt-4o-mini"),
        schema=schema
    )
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url="...", config=config)
    
    # 从所有滚动内容中提取数据
    import json
    posts = json.loads(result.extracted_content)
    print(f"从虚拟滚动中提取了 {len(posts)} 个帖子")
```

## 性能提示

1. **容器选择**：选择器要具体。使用正确的容器可提高性能。

2. **滚动次数**：从保守开始，根据需要增加：
   ```python
   # 从较少的滚动开始
   virtual_config = VirtualScrollConfig(
       container_selector="#feed",
       scroll_count=10  # 先用10测试，根据需要增加
   )
   ```

3. **等待时间**：根据网站速度调整：
   ```python
   # 快速网站
   wait_after_scroll=0.2
   
   # 较慢网站或内容较重
   wait_after_scroll=1.5
   ```

4. **调试模式**：设置`headless=False`观察滚动：
   ```python
   browser_config = BrowserConfig(headless=False)
   async with AsyncWebCrawler(config=browser_config) as crawler:
       # 观察滚动过程
   ```

## 内部工作原理

1. **检测阶段**：滚动并比较HTML以检测行为
2. **捕获阶段**：对于被替换的内容，存储每个位置的HTML块
3. **合并阶段**：合并所有块，基于文本内容去重
4. **结果**：包含所有唯一项目的完整HTML

去重使用标准化文本（小写，无空格/符号）以确保准确合并，避免误判。

## 错误处理

虚拟滚动优雅地处理错误：

```python
# 如果找不到容器或滚动失败
result = await crawler.arun(url="...", config=config)

if result.success:
    # 虚拟滚动成功或不需要
    print(f"捕获了 {len(result.html)} 个字符")
else:
    # 爬取完全失败
    print(f"错误: {result.error_message}")
```

如果找不到容器，爬虫会正常继续而不使用虚拟滚动。

## 完整示例

查看我们的[综合示例](/docs/examples/virtual_scroll_example.py)，展示：
- 类似Twitter的feed
- Instagram网格  
- 传统无限滚动
- 混合内容场景
- 性能比较

```bash
# 运行示例
cd docs/examples
python virtual_scroll_example.py
```

该示例包括一个本地测试服务器，提供不同的滚动行为供实验。