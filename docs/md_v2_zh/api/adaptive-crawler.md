# AdaptiveCrawler

`AdaptiveCrawler` 类实现了智能网页爬取功能，能自动判断何时已收集足够信息来回答查询。它采用三层评分系统来评估覆盖率、一致性和饱和度。

## 构造函数

```python
AdaptiveCrawler(
    crawler: AsyncWebCrawler,
    config: Optional[AdaptiveConfig] = None
)
```

### 参数

- **crawler** (`AsyncWebCrawler`): 用于获取页面的底层网页爬虫实例
- **config** (`Optional[AdaptiveConfig]`): 自适应爬取行为的配置设置。如未提供，则使用默认设置。

## 主要方法

### digest()

从指定URL和查询开始执行自适应爬取的主要方法。

```python
async def digest(
    start_url: str,
    query: str,
    resume_from: Optional[Union[str, Path]] = None
) -> CrawlState
```

#### 参数

- **start_url** (`str`): 爬取的起始URL
- **query** (`str`): 指导爬取过程的搜索查询
- **resume_from** (`Optional[Union[str, Path]]`): 用于恢复爬取状态的保存文件路径

#### 返回值

- **CrawlState**: 包含所有已爬取URL、知识库和指标的最终爬取状态

#### 示例

```python
async with AsyncWebCrawler() as crawler:
    adaptive = AdaptiveCrawler(crawler)
    state = await adaptive.digest(
        start_url="https://docs.python.org",
        query="async context managers"
    )
```

## 属性

### confidence

当前置信度分数(0-1)，表示信息充分程度。

```python
@property
def confidence(self) -> float
```

### coverage_stats

包含详细覆盖率统计数据的字典。

```python
@property  
def coverage_stats(self) -> Dict[str, float]
```

返回值:
- **coverage**: 查询词覆盖率分数
- **consistency**: 信息一致性分数  
- **saturation**: 内容饱和度分数
- **confidence**: 总体置信度分数

### is_sufficient

布尔值，表示是否已收集足够信息。

```python
@property
def is_sufficient(self) -> bool
```

### state

访问当前爬取状态。

```python
@property
def state(self) -> CrawlState
```

## 方法

### get_relevant_content()

从知识库中检索最相关的内容。

```python
def get_relevant_content(
    self,
    top_k: int = 5
) -> List[Dict[str, Any]]
```

#### 参数

- **top_k** (`int`): 要返回的最相关文档数量（默认：5）

#### 返回值

包含以下内容的字典列表：
- **url**: 页面URL
- **content**: 页面内容
- **score**: 相关性分数
- **metadata**: 附加页面元数据

### print_stats()

以格式化输出显示爬取统计信息。

```python
def print_stats(
    self,
    detailed: bool = False
) -> None
```

#### 参数

- **detailed** (`bool`): 为True时显示带颜色的详细指标，为False时显示摘要表格

### export_knowledge_base()

将收集的知识库导出到JSONL文件。

```python
def export_knowledge_base(
    self,
    path: Union[str, Path]
) -> None
```

#### 参数

- **path** (`Union[str, Path]`): JSONL导出的输出文件路径

#### 示例

```python
adaptive.export_knowledge_base("my_knowledge.jsonl")
```

### import_knowledge_base()

导入先前导出的知识库。

```python
def import_knowledge_base(
    self,
    path: Union[str, Path]
) -> None
```

#### 参数

- **path** (`Union[str, Path]`): 要导入的JSONL文件路径

## 配置

`AdaptiveConfig` 类控制自适应爬取的行为：

```python
@dataclass
class AdaptiveConfig:
    confidence_threshold: float = 0.8      # 当置信度达到此值时停止
    max_pages: int = 50                    # 最大爬取页面数
    top_k_links: int = 5                   # 每个页面跟踪的链接数
    min_gain_threshold: float = 0.1        # 继续爬取的最小预期增益
    save_state: bool = False               # 自动保存爬取状态
    state_path: Optional[str] = None       # 状态持久化路径
```

### 自定义配置示例

```python
config = AdaptiveConfig(
    confidence_threshold=0.7,
    max_pages=20,
    top_k_links=3
)

adaptive = AdaptiveCrawler(crawler, config=config)
```

## 完整示例

```python
import asyncio
from crawl4ai import AsyncWebCrawler, AdaptiveCrawler, AdaptiveConfig

async def main():
    # 配置自适应爬取
    config = AdaptiveConfig(
        confidence_threshold=0.75,
        max_pages=15,
        save_state=True,
        state_path="my_crawl.json"
    )
    
    async with AsyncWebCrawler() as crawler:
        adaptive = AdaptiveCrawler(crawler, config)
        
        # 开始爬取
        state = await adaptive.digest(
            start_url="https://example.com/docs",
            query="authentication oauth2 jwt"
        )
        
        # 检查结果
        print(f"Confidence achieved: {adaptive.confidence:.0%}")
        adaptive.print_stats()
        
        # 获取最相关页面
        for page in adaptive.get_relevant_content(top_k=3):
            print(f"- {page['url']} (score: {page['score']:.2f})")
        
        # 导出供后续使用
        adaptive.export_knowledge_base("auth_knowledge.jsonl")

if __name__ == "__main__":
    asyncio.run(main())
```

## 另请参阅

- [digest() 方法参考](digest.md)
- [自适应爬取指南](../core/adaptive-crawling.md)
- [高级自适应策略](../advanced/adaptive-strategies.md)