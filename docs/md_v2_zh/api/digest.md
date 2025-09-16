正在阅读我无法读取《https://docs.example》、《https://api.example.com/docs》文件的内容。其他文件已阅读并为你总结如下：
# digest()

`digest()` 方法是自适应网络爬取的主要接口。它从给定URL开始，在查询引导下智能爬取网站，并自动判断何时已收集足够信息。

## 方法签名

```python
async def digest(
    start_url: str,
    query: str,
    resume_from: Optional[Union[str, Path]] = None
) -> CrawlState
```

## 参数

### start_url
- **类型**: `str`
- **必填**: 是
- **描述**: 爬取的起始URL。必须是有效的HTTP/HTTPS URL，作为信息收集的入口点。

### query
- **类型**: `str`  
- **必填**: 是
- **描述**: 指导爬取过程的搜索查询。应包含与目标信息相关的关键术语。爬虫用此评估相关性并决定跟踪哪些链接。

### resume_from
- **类型**: `Optional[Union[str, Path]]`
- **默认值**: `None`
- **描述**: 之前保存的爬取状态文件路径。提供时，爬虫会从保存状态恢复而非重新开始。

## 返回值

返回包含以下内容的`CrawlState`对象：

- **crawled_urls** (`Set[str]`): 已爬取的所有URL
- **knowledge_base** (`List[CrawlResult]`): 包含内容的已爬取页面集合
- **pending_links** (`List[Link]`): 已发现但未爬取的链接
- **metrics** (`Dict[str, float]`): 性能和质量指标
- **query** (`str`): 原始查询
- 用于评分的附加统计信息

## 工作原理

`digest()`方法实现智能爬取算法：

1. **初始爬取**: 从提供的URL开始
2. **链接分析**: 评估所有发现链接的相关性
3. **评分**: 使用三个指标评估信息充分性：
   - **覆盖率**: 查询术语的覆盖程度
   - **一致性**: 跨页面信息的连贯性
   - **饱和度**: 收益递减检测
4. **自适应选择**: 选择最有希望的链接跟踪
5. **停止决策**: 当达到置信阈值时自动停止

## 示例

### 基础用法

```python
async with AsyncWebCrawler() as crawler:
    adaptive = AdaptiveCrawler(crawler)
    
    state = await adaptive.digest(
        start_url="链接2",
        query="async await context managers"
    )
    
    print(f"已爬取 {len(state.crawled_urls)} 页")
    print(f"置信度: {adaptive.confidence:.0%}")
```

### 带配置

```python
config = AdaptiveConfig(
    confidence_threshold=0.9,  # 要求高置信度
    max_pages=30,             # 允许更多页面
    top_k_links=3             # 每页跟踪前3个链接
)

adaptive = AdaptiveCrawler(crawler, config=config)

state = await adaptive.digest(
    start_url="https://api.example.com/docs",
    query="authentication endpoints rate limits"
)
```

### 恢复之前爬取

```python
# 首次爬取 - 可能中断
state1 = await adaptive.digest(
    start_url="链接1",
    query="machine learning algorithms"
)

# 保存状态(如果未自动保存)
state1.save("ml_crawl_state.json")

# 之后从保存状态恢复
state2 = await adaptive.digest(
    start_url="链接1",
    query="machine learning algorithms",
    resume_from="ml_crawl_state.json"
)
```

### 带进度监控

```python
state = await adaptive.digest(
    start_url="https://docs.example.com",
    query="api reference"
)

# 监控进度
print(f"已爬取页面: {len(state.crawled_urls)}")
print(f"发现新术语: {state.new_terms_history}")
print(f"最终置信度: {adaptive.confidence:.2%}")

# 查看详细统计
adaptive.print_stats(detailed=True)
```

## 查询最佳实践

1. **具体明确**: 使用目标内容中出现的描述性术语
   ```python
   # 良好
   query = "python async context managers implementation"
   
   # 过于宽泛
   query = "python programming"
   ```

2. **包含关键术语**: 添加预期找到的技术术语
   ```python
   query = "oauth2 jwt refresh tokens authorization"
   ```

3. **多概念组合**: 结合相关概念实现全面覆盖
   ```python
   query = "rest api pagination sorting filtering"
   ```

## 性能考量

- **初始URL**: 选择导航良好的页面(如文档索引)
- **查询长度**: 3-8个术语通常效果最佳
- **链接密度**: 导航清晰的网站爬取效率更高
- **缓存**: 对同一域名的重复爬取启用缓存

## 错误处理

```python
try:
    state = await adaptive.digest(
        start_url="链接1",
        query="search terms"
    )
except Exception as e:
    print(f"爬取失败: {e}")
    # 如果配置中save_state=True，状态会自动保存
```

## 停止条件

满足以下任一条件时爬取停止：

1. **置信阈值**: 达到配置的置信水平
2. **页面限制**: 爬取达到最大页面数
3. **收益递减**: 预期信息增益低于阈值
4. **无相关链接**: 没有可跟踪的有价值链接

## 另请参阅

- [AdaptiveCrawler类](adaptive-crawler.md)
- [自适应爬取指南](../core/adaptive-crawling.md)
- [配置选项](../core/adaptive-crawling.md#configuration-options)