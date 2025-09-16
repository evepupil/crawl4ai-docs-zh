# 链接与媒体处理

在本教程中，您将学习如何：

1. 从爬取页面提取链接（内部、外部）  
2. 过滤或排除特定域名（如社交媒体或自定义域名）  
3. 访问和管理爬取结果中的媒体数据（特别是图片）  
4. 配置爬虫排除或优先处理特定图片

> **前提条件**  
> - 您已完成或熟悉[AsyncWebCrawler基础](../core/simple-crawling.md)教程  
> - 能在您的环境（Playwright、Python等）中运行Crawl4AI

---

以下是修订后的**链接提取**和**媒体提取**部分，包含示例数据结构展示链接和媒体项如何存储在`CrawlResult`中。请根据需要调整字段名称或描述以匹配实际输出。

---

## 1. 链接提取

### 1.1 `result.links`

当调用URL的`arun()`或`arun_many()`时，Crawl4AI会自动提取链接并存储在`CrawlResult`的`links`字段中。默认情况下，爬虫会区分**内部**链接（相同域名）和**外部**链接（不同域名）。

**基础示例**：

```python
from crawl4ai import AsyncWebCrawler

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun("https://www.example.com")
    if result.success:
        internal_links = result.links.get("internal", [])
        external_links = result.links.get("external", [])
        print(f"Found {len(internal_links)} internal links.")
        print(f"Found {len(internal_links)} external links.")
        print(f"Found {len(result.media)} media items.")

        # 每个链接通常是包含以下字段的字典：
        # { "href": "...", "text": "...", "title": "...", "base_domain": "..." }
        if internal_links:
            print("Sample Internal Link:", internal_links[0])
    else:
        print("Crawl failed:", result.error_message)
```

**结构示例**：

```python
result.links = {
  "internal": [
    {
      "href": "https://kidocode.com/",
      "text": "",
      "title": "",
      "base_domain": "kidocode.com"
    },
    {
      "href": "https://kidocode.com/degrees/technology",
      "text": "Technology Degree",
      "title": "KidoCode Tech Program",
      "base_domain": "kidocode.com"
    },
    # ...
  ],
  "external": [
    # 可能包含指向第三方站点的其他链接
  ]
}
```

- **`href`**: 原始超链接URL  
- **`text`**: `<a>`标签内的链接文本（如果有）  
- **`title`**: 链接的`title`属性（如果存在）  
- **`base_domain`**: 从`href`提取的域名。有助于按域名过滤或分组

---

## 2. 高级链接头部提取与评分

不仅想提取链接，还想获取这些链接页面的实际内容（标题、描述、元数据）并评分？这正是链接头部提取的功能 - 它从每个发现的链接获取`<head>`部分并使用多种算法进行评分。

### 2.1 为什么需要链接头部提取？

当爬取页面时，会获取数百个链接。但哪些真正有价值？链接头部提取通过以下方式解决：

1. **从每个链接获取头部内容**（标题、描述、元标签）
2. **基于URL质量、文本相关性和上下文对链接进行内在评分**
3. **当提供搜索查询时使用BM25算法进行上下文评分**
4. **智能组合分数**给出最终相关性排名

### 2.2 完整工作示例

以下是可直接复制、粘贴和运行的完整示例：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai import LinkPreviewConfig

async def extract_link_heads_example():
    """
    展示带评分的链接头部提取的完整示例。
    这将爬取文档站点并提取内部链接的头部内容。
    """
    
    # 配置链接头部提取
    config = CrawlerRunConfig(
        # 启用带详细配置的链接头部提取
        link_preview_config=LinkPreviewConfig(
            include_internal=True,           # 从内部链接提取
            include_external=False,          # 本示例跳过外部链接
            max_links=10,                   # 演示限制为10个链接
            concurrency=5,                  # 同时处理5个链接
            timeout=10,                     # 每个链接10秒超时
            query="API documentation guide", # 上下文评分查询
            score_threshold=0.3,            # 仅包含评分高于0.3的链接
            verbose=True                    # 显示详细进度
        ),
        # 启用内在评分（URL质量、文本相关性）
        score_links=True,
        # 保持输出简洁
        only_text=True,
        verbose=True
    )
    
    async with AsyncWebCrawler() as crawler:
        # 爬取文档站点（非常适合测试）
        result = await crawler.arun("https://docs.python.org/3/", config=config)
        
        if result.success:
            print(f"✅ 成功爬取: {result.url}")
            print(f"📄 页面标题: {result.metadata.get('title', '无标题')}")
            
            # 访问链接（现在增强为包含头部数据和分数）
            internal_links = result.links.get("internal", [])
            external_links = result.links.get("external", [])
            
            print(f"\n🔗 找到 {len(internal_links)} 个内部链接")
            print(f"🌍 找到 {len(external_links)} 个外部链接")
            
            # 计算有头部数据的链接数量
            links_with_head = [link for link in internal_links 
                             if link.get("head_data") is not None]
            print(f"🧠 提取到头部数据的链接: {len(links_with_head)}")
            
            # 显示前3个评分最高的链接
            print(f"\n🏆 带完整评分的前3个链接:")
            for i, link in enumerate(links_with_head[:3]):
                print(f"\n{i+1}. {link['href']}")
                print(f"   链接文本: '{link.get('text', '无文本')[:50]}...'")
                
                # 显示所有三种评分类型
                intrinsic = link.get('intrinsic_score')
                contextual = link.get('contextual_score') 
                total = link.get('total_score')
                
                if intrinsic is not None:
                    print(f"   📊 内在评分: {intrinsic:.2f}/10.0 (URL质量及上下文)")
                if contextual is not None:
                    print(f"   🎯 上下文评分: {contextual:.3f} (BM25相关性)")
                if total is not None:
                    print(f"   ⭐ 总评分: {total:.3f} (组合最终分数)")
                
                # 显示提取的头部数据
                head_data = link.get("head_data", {})
                if head_data:
                    title = head_data.get("title", "无标题")
                    description = head_data.get("meta", {}).get("description", "无描述")
                    
                    print(f"   📰 标题: {title[:60]}...")
                    if description:
                        print(f"   📝 描述: {description[:80]}...")
                    
                    # 显示提取状态
                    status = link.get("head_extraction_status", "未知")
                    print(f"   ✅ 提取状态: {status}")
        else:
            print(f"❌ 爬取失败: {result.error_message}")

# 运行示例
if __name__ == "__main__":
    asyncio.run(extract_link_heads_example())
```

**预期输出：**
```
✅ 成功爬取: https://docs.python.org/3/
📄 页面标题: 3.13.5 Documentation
🔗 找到 53 个内部链接
🌍 找到 1 个外部链接
🧠 提取到头部数据的链接: 10

🏆 带完整评分的前3个链接:

1. https://docs.python.org/3.15/
   链接文本: 'Python 3.15 (in development)...'
   📊 内在评分: 4.17/10.0 (URL质量及上下文)
   🎯 上下文评分: 1.000 (BM25相关性)
   ⭐ 总评分: 5.917 (组合最终分数)
   📰 标题: 3.15.0a0 Documentation...
   📝 描述: The official Python documentation...
   ✅ 提取状态: valid
```

### 2.3 配置详解

`LinkPreviewConfig`类支持以下选项：

```python
from crawl4ai import LinkPreviewConfig

link_preview_config = LinkPreviewConfig(
    # 基础设置
    verbose=True,                    # 显示详细日志（推荐学习时使用）
    
    # 链接过滤
    include_internal=True,           # 包含同域名链接
    include_external=True,           # 包含不同域名链接
    max_links=50,                   # 最大处理链接数（防止过载）
    
    # 模式过滤
    include_patterns=[               # 仅处理匹配这些模式的链接
        "*/docs/*", 
        "*/api/*", 
        "*/reference/*"
    ],
    exclude_patterns=[               # 跳过匹配这些模式的链接
        "*/login*",
        "*/admin*"
    ],
    
    # 性能设置
    concurrency=10,                  # 同时处理多少链接
    timeout=5,                      # 每个链接等待秒数
    
    # 相关性评分
    query="machine learning API",    # BM25上下文评分查询
    score_threshold=0.3,            # 仅包含高于此评分的链接
)
```

### 2.4 理解三种评分类型

每个提取的链接获得三种不同评分：

#### 1. **内在评分 (0-10)** - URL和内容质量
基于URL结构、链接文本质量和页面上下文：

```python
# 高内在评分指标：
# ✅ 干净的URL结构（docs.python.org/api/reference）
# ✅ 有意义的链接文本（"API参考指南"）
# ✅ 与页面上下文相关
# ✅ 不深埋在导航中

# 低内在评分指标：
# ❌ 随机URL（site.com/x7f9g2h）
# ❌ 无链接文本或通用文本（"点击这里"）
# ❌ 与页面内容无关
```

#### 2. **上下文评分 (0-1)** - 与查询的BM25相关性
仅在提供`query`时可用。使用BM25算法对比头部内容：

```python
# 示例：query = "machine learning tutorial"
# 高上下文评分：链接到"Complete Machine Learning Guide"
# 低上下文评分：链接到"隐私政策"
```

#### 3. **总评分** - 智能组合
智能组合内在和上下文评分并提供回退：

```python
# 当两者都可用时：(内在 * 0.3) + (上下文 * 0.7)
# 仅内在时：使用内在评分
# 仅上下文时：使用上下文评分
# 都没有时：不计算
```

### 2.5 实际用例

#### 用例1：研究助手
查找最相关的文档页面：

```python
async def research_assistant():
    config = CrawlerRunConfig(
        link_preview_config=LinkPreviewConfig(
            include_internal=True,
            include_external=True,
            include_patterns=["*/docs/*", "*/tutorial/*", "*/guide/*"],
            query="machine learning neural networks",
            max_links=20,
            score_threshold=0.5,  # 仅高相关性链接
            verbose=True
        ),
        score_links=True
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://scikit-learn.org/", config=config)
        
        if result.success:
            # 获取高评分链接
            good_links = [link for link in result.links.get("internal", [])
                         if link.get("total_score", 0) > 0.7]
            
            print(f"🎯 找到 {len(good_links)} 个高相关性链接:")
            for link in good_links[:5]:
                print(f"⭐ {link['total_score']:.3f} - {link['href']}")
                print(f"   {link.get('head_data', {}).get('title', '无标题')}")
```

#### 用例2：内容发现
查找所有API端点和引用：

```python
async def api_discovery():
    config = CrawlerRunConfig(
        link_preview_config=LinkPreviewConfig(
            include_internal=True,
            include_patterns=["*/api/*", "*/reference/*"],
            exclude_patterns=["*/deprecated/*"],
            max_links=100,
            concurrency=15,
            verbose=False  # 简洁输出
        ),
        score_links=True
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://docs.example-api.com/", config=config)
        
        if result.success:
            api_links = result.links.get("internal", [])
            
            # 按端点类型分组
            endpoints = {}
            for link in api_links:
                if link.get("head_data"):
                    title = link["head_data"].get("title", "")
                    if "GET" in title:
                        endpoints.setdefault("GET", []).append(link)
                    elif "POST" in title:
                        endpoints.setdefault("POST", []).append(link)
            
            for method, links in endpoints.items():
                print(f"\n{method} 端点 ({len(links)}):")
                for link in links[:3]:
                    print(f"  • {link['href']}")
```

#### 用例3：链接质量分析
分析网站结构和内容质量：

```python
async def quality_analysis():
    config = CrawlerRunConfig(
        link_preview_config=LinkPreviewConfig(
            include_internal=True,
            max_links=200,
            concurrency=20,
        ),
        score_links=True
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://your-website.com/", config=config)
        
        if result.success:
            links = result.links.get("internal", [])
            
            # 分析内在评分
            scores = [link.get('intrinsic_score', 0) for link in links]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            print(f"📊 链接质量分析:")
            print(f"   平均内在评分: {avg_score:.2f}/10.0")
            print(f"   高质量链接 (>7.0): {len([s for s in scores if s > 7.0])}")
            print(f"   低质量链接 (<3.0): {len([s for s in scores if s < 3.0])}")
            
            # 查找有问题的链接
            bad_links = [link for link in links 
                        if link.get('intrinsic_score', 0) < 2.0]
            
            if bad_links:
                print(f"\n⚠️  需要注意的链接:")
                for link in bad_links[:5]:
                    print(f"   {link['href']} (评分: {link.get('intrinsic_score', 0):.1f})")
```

### 2.6 性能提示

1. **从小开始**：从`max_links: 10`开始了解功能
2. **使用模式**：用`include_patterns`过滤以专注于相关部分
3. **调整并发**：更高并发=更快但资源使用更多
4. **设置超时**：使用`timeout: 5`防止在慢速站点上挂起
5. **使用评分阈值**：用`score_threshold`过滤低质量链接

### 2.7 故障排除

**没有提取到头部数据？**
```python
# 检查配置：
config = CrawlerRunConfig(
    link_preview_config=LinkPreviewConfig(
        verbose=True   # ← 启用以查看发生了什么
    )
)
```

**评分显示为None？**
```python
# 确保评分已启用：
config = CrawlerRunConfig(
    score_links=True,  # ← 启用内在评分
    link_preview_config=LinkPreviewConfig(
        query="your search terms"  # ← 用于上下文评分
    )
)
```

**处理时间过长？**
```python
# 优化性能：
link_preview_config = LinkPreviewConfig(
    max_links=20,      # ← 减少数量
    concurrency=10,    # ← 增加并行度
    timeout=3,         # ← 更短超时
    include_patterns=["*/important/*"]  # ← 专注于关键区域
)
```

---

## 3. 域名过滤

某些网站包含数百个第三方或联盟链接。您可以在**爬取时**通过配置爬虫过滤掉某些域名。`CrawlerRunConfig`中最相关的参数是：

- **`exclude_external_links`**: 如果为`True`，丢弃指向根域名外的任何链接  
- **`exclude_social_media_domains`**: 提供社交媒体平台列表（如`["facebook.com", "twitter.com"]`）从爬取中排除  
- **`exclude_social_media_links`**: 如果为`True`，自动跳过已知社交平台  
- **`exclude_domains`**: 提供要排除的自定义域名列表（如`["spammyads.com", "tracker.net"]`）

### 3.1 示例：排除外部和社交媒体链接

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    crawler_cfg = CrawlerRunConfig(
        exclude_external_links=True,          # 无主域名外的链接
        exclude_social_media_links=True       # 跳过Twitter、Facebook等
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            "https://www.example.com",
            config=crawler_cfg
        )
        if result.success:
            print("[OK] 爬取:", result.url)
            print("内部链接数量:", len(result.links.get("internal", [])))
            print("外部链接数量:", len(result.links.get("external", [])))  
            # 在exclude_external_links=True时可能为零
        else:
            print("[ERROR]", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
```

### 3.2 示例：排除特定域名

如果想保留外部链接但专门排除某个域名（如`suspiciousads.com`），这样做：

```python
crawler_cfg = CrawlerRunConfig(
    exclude_domains=["suspiciousads.com"]
)
```

当您仍想要外部链接但需要屏蔽某些被视为垃圾的站点时，这种方法很方便。

---

## 4. 媒体提取

### 4.1 访问`result.media`

默认情况下，Crawl4AI收集在页面上找到的图片、音频和视频URL。它们存储在`result.media`中，这是一个按媒体类型（如`images`、`videos`、`audio`）键控的字典。
**注意：表格已从`result.media["tables"]`移至新的`result.tables`格式，以便更好地组织和直接访问。**

**基础示例**：

```python
if result.success:
    # 获取图片
    images_info = result.media.get("images", [])
    print(f"共找到 {len(images_info)} 张图片。")
    for i, img in enumerate(images_info[:3]):  # 仅检查前3张
        print(f"[图片 {i}] URL: {img['src']}")
        print(f"           Alt文本: {img.get('alt', '')}")
        print(f"           评分: {img.get('score')}")
        print(f"           描述: {img.get('desc', '')}\n")
```

**结构示例**：

```python
result.media = {
  "images": [
    {
      "src": "https://cdn.prod.website-files.com/.../Group%2089.svg",
      "alt": "coding school for kids",
      "desc": "Trial Class Degrees degrees All Degrees AI Degree Technology ...",
      "score": 3,
      "type": "image",
      "group_id": 0,
      "format": None,
      "width": None,
      "height": None
    },
    # ...
  ],
  "videos": [
    # 类似结构但带有视频特定字段
  ],
  "audio": [
    # 类似结构但带有音频特定字段
  ],
}
```

根据您的Crawl4AI版本或爬取策略，这些字典可以包含以下字段：

- **`src`**: 媒体URL（如图片源）  
- **`alt`**: 图片的alt文本（如果存在）  
- **`desc`**: 附近文本片段或简短描述（可选）  
- **`score`**: 如果使用内容评分功能，则为启发式相关性评分  
- **`width`**, **`height`**: 如果爬虫检测到图片/视频的尺寸  
- **`type`**: 通常为`"image"`、`"video"`或`"audio"`  
- **`group_id`**: 如果分组相关媒体项，爬虫可能会分配ID  

有了这些细节，您可以轻松过滤或专注于某些图片（例如，忽略评分很低或不同域名的图片），或收集元数据进行分析。

### 4.2 排除外部图片

如果处理重页面或想跳过第三方图片（例如广告），可以开启：

```python
crawler_cfg = CrawlerRunConfig(
    exclude_external_images=True
)
```

此设置尝试丢弃来自主域名外的图片，仅保留您爬取站点的图片。

### 4.3 其他媒体配置

- **`screenshot`**: 设为`True`如果您想要全页截图以`base64`格式存储在`result.screenshot`中  
- **`pdf`**: 设为`True`如果您想要页面的PDF版本存储在`result.pdf`中  
- **`capture_mhtml`**: 设为`True`如果您想要页面的MHTML快照存储在`result.mhtml`中。此格式将所有资源（CSS、图片、脚本）保存在单个文件中，非常适合存档或离线查看
- **`wait_for_images`**: 如果为`True`，尝试等待图片完全加载后再进行最终提取

#### 示例：捕获页面为MHTML

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def main():
    crawler_cfg = CrawlerRunConfig(
        capture_mhtml=True  # 启用MHTML捕获
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com", config=crawler_cfg)
        
        if result.success and result.mhtml:
            # 将MHTML快照保存到文件
            with open("example.mhtml", "w", encoding="utf-8") as f:
                f.write(result.mhtml)
            print("MHTML快照已保存为example.mhtml")
        else:
            print("捕获MHTML失败:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
```

MHTML格式特别有用因为：
- 它捕获包括所有资源的完整页面状态
- 可在大多数现代浏览器中离线打开查看
- 精确保留爬取时的页面状态
- 是单个文件，便于存储和传输

---

## 5. 综合应用：链接和媒体过滤

以下是组合示例，展示如何过滤外部链接、跳过某些域名并排除外部图片：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    # 假设我们只想保留内部链接，移除某些域名，
    # 并从最终爬取数据中丢弃外部图片
    crawler_cfg = CrawlerRunConfig(
        exclude_external_links=True,
        exclude_domains=["spammyads.com"],
        exclude_social_media_links=True,   # 跳过Twitter、Facebook等
        exclude_external_images=True,      # 仅保留主域名图片
        wait_for_images=True,             # 确保图片加载
        verbose=True
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://www.example.com", config=crawler_cfg)

        if result.success:
            print("[OK] 爬取:", result.url)
            
            # 1. 链接
            in_links = result.links.get("internal", [])
            ext_links = result.links.get("external", [])
            print("内部链接数量:", len(in_links))
            print("外部链接数量:", len(ext_links))  # exclude_external_links=True时应为零
            
            # 2. 图片
            images = result.media.get("images", [])
            print("找到图片数量:", len(images))
            
            # 查看这些图片的片段
            for i, img in enumerate(images[:3]):
                print(f"  - {img['src']} (alt={img.get('alt','')}, score={img.get('score','N/A')})")
        else:
            print("[ERROR] 爬取失败。原因:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 6. 常见陷阱与技巧

1. **冲突标志**：  
   - `exclude_external_links=True`但同时指定`exclude_social_media_links=True`通常没问题，但要理解第一个设置已经丢弃*所有*外部链接。第二个变得有些多余。  
   - `exclude_external_images=True`但想保留某些外部图片？目前没有针对图片的部分基于域名的设置，因此可能需要自定义方法或挂钩逻辑。

2. **相关性评分**：  
   - 如果您的Crawl4AI版本或爬取策略包含`img["score"]`，它通常是基于大小、位置或内容分析的启发式。如果依赖它，请仔细评估。

3. **性能**：  
   - 排除某些域名或外部图片可以加速爬取，特别是对于大型、媒体密集型页面。  
   - 如果想要"完整"链接地图，*不要*排除它们。相反，可以在自己的代码中进行后过滤。

4. **社交媒体列表**：  
   - `exclude_social_media_links=True`通常引用已知社交域名的内部列表，如Facebook、Twitter、LinkedIn等。如果需要添加或删除，请查找库设置或本地配置文件（取决于您的版本）。

---

**这就是链接和媒体分析的全部内容！** 您现在已准备好过滤不需要的站点，并专注于对项目重要的图片和视频。