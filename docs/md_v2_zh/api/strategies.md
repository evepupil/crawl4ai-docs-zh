# 抽取与分块策略 API

本文档涵盖 Crawl4AI 中抽取与分块策略的 API 参考。

## 抽取策略

所有抽取策略都继承自基础的 `ExtractionStrategy` 类，并实现两个关键方法：
- `extract(url: str, html: str) -> List[Dict[str, Any]]`
- `run(url: str, sections: List[str]) -> List[Dict[str, Any]]`

### LLMExtractionStrategy

用于使用语言模型抽取结构化数据。

```python
LLMExtractionStrategy(
    # Required Parameters
    provider: str = DEFAULT_PROVIDER,     # LLM provider (e.g., "ollama/llama2")
    api_token: Optional[str] = None,      # API token
    
    # Extraction Configuration
    instruction: str = None,              # Custom extraction instruction
    schema: Dict = None,                  # Pydantic model schema for structured data
    extraction_type: str = "block",       # "block" or "schema"
    
    # Chunking Parameters
    chunk_token_threshold: int = 4000,    # Maximum tokens per chunk
    overlap_rate: float = 0.1,           # Overlap between chunks
    word_token_rate: float = 0.75,       # Word to token conversion rate
    apply_chunking: bool = True,         # Enable/disable chunking
    
    # API Configuration
    base_url: str = None,                # Base URL for API
    extra_args: Dict = {},               # Additional provider arguments
    verbose: bool = False                # Enable verbose logging
)
```

### RegexExtractionStrategy

使用正则表达式快速抽取基于模式的常见实体。

```python
RegexExtractionStrategy(
    # Pattern Configuration
    pattern: IntFlag = RegexExtractionStrategy.Nothing,  # Bit flags of built-in patterns to use
    custom: Optional[Dict[str, str]] = None,           # Custom pattern dictionary {label: regex}
    
    # Input Format
    input_format: str = "fit_html",                    # "html", "markdown", "text" or "fit_html"
)

# Built-in Patterns as Bit Flags
RegexExtractionStrategy.Email           # Email addresses
RegexExtractionStrategy.PhoneIntl       # International phone numbers 
RegexExtractionStrategy.PhoneUS         # US-format phone numbers
RegexExtractionStrategy.Url             # HTTP/HTTPS URLs
RegexExtractionStrategy.IPv4            # IPv4 addresses
RegexExtractionStrategy.IPv6            # IPv6 addresses
RegexExtractionStrategy.Uuid            # UUIDs
RegexExtractionStrategy.Currency        # Currency values (USD, EUR, etc)
RegexExtractionStrategy.Percentage      # Percentage values
RegexExtractionStrategy.Number          # Numeric values
RegexExtractionStrategy.DateIso         # ISO format dates
RegexExtractionStrategy.DateUS          # US format dates
RegexExtractionStrategy.Time24h         # 24-hour format times
RegexExtractionStrategy.PostalUS        # US postal codes
RegexExtractionStrategy.PostalUK        # UK postal codes
RegexExtractionStrategy.HexColor        # HTML hex color codes
RegexExtractionStrategy.TwitterHandle   # Twitter handles
RegexExtractionStrategy.Hashtag         # Hashtags
RegexExtractionStrategy.MacAddr         # MAC addresses
RegexExtractionStrategy.Iban            # International bank account numbers
Regex极速赛车ExtractionStrategy.CreditCard      # Credit card numbers
RegexExtractionStrategy.All             # All available patterns
```

### CosineStrategy

用于基于内容相似性的抽取和聚类。

```python
Cosine极速赛车Strategy(
    # Content Filtering
    semantic_filter: str = None,        # Topic/keyword filter
    word_count_threshold: int = 10,     # Minimum words per cluster
    sim_threshold: float = 0.3,         # Similarity threshold
    
    # Clustering Parameters
    max_dist: float =极速赛车 0.2,             # Maximum cluster distance
    linkage_method: str = 'ward',       # Clustering method
    top_k: int = 3,                    # Top clusters to return
    
    # Model Configuration
    model_name: str = 'sentence-transformers/all-MiniLM-L6-v2',  # Embedding model
    
    verbose: bool = False              # Enable verbose logging
)
```

### JsonCssExtractionStrategy

用于基于 CSS 选择器的结构化数据抽取。

```python
JsonCssExtractionStrategy(
    schema: Dict[str, Any],    # Extraction schema
    verbose: bool = False      # Enable verbose logging
)

# Schema Structure
schema = {
    "name": str,              # Schema name
    "baseSelector": str,      # Base CSS selector
    "fields": [               # List of fields to extract
        {
            "name": str,      # Field name
            "selector": str,  # CSS selector
            "type": str,     # Field type: "text", "attribute", "html", "regex"
            "attribute": str, # For type="attribute"
            "pattern": str,  # For type="regex"
            "transform": str, # Optional: "lowercase", "uppercase", "strip"
极速赛车            "default": Any    # Default value if extraction fails
        }
    ]
}
```

## 分块策略

所有分块策略都继承自 `ChunkingStrategy` 并实现 `chunk(text: str) -> list` 方法。

### RegexChunking

基于正则表达式模式分割文本。

```python
RegexChunking(
    patterns: List[str] = None  # Regex patterns for splitting
                               # Default: [r'\n\n']
)
```

### SlidingWindowChunking

使用滑动窗口方法创建重叠块。

```python
SlidingWindowChunking(
    window_size: int = 100,    # Window size in words
    step: int = 50             # Step size between windows
)
```

### OverlappingWindowChunking

创建具有指定重叠的块。

```python
OverlappingWindowChunking(
    window_size: int = 1000,   # Chunk size in words
    overlap: int = 100         # Overlap size in words
)
```

## 使用示例

### LLM 抽取

```python
from pydantic import BaseModel
from crawl4ai import LLMExtractionStrategy
from crawl4ai import LLMConfig

# Define schema
class Article(BaseModel):
    title: str
    content: str
    author: str

# Create strategy
strategy = LLMExtractionStrategy(
    llm_config = LLMConfig(provider="ollama/llama2"),
    schema=Article.schema(),
    instruction="Extract article details"
)

# Use with crawler
result = await crawler.arun(
    url="https://example.com/article",
    extraction_strategy=strategy
)

# Access extracted data
data = json.loads(result.extracted_content)
```

### 正则表达式抽取

```python
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, RegexExtractionStrategy

# Method 1: Use built-in patterns
strategy = RegexExtractionStrategy(
    pattern = RegexExtractionStrategy.Email | RegexExtractionStrategy.Url
)

# Method 2: Use custom patterns
price_pattern = {"usd_price": r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?"}
strategy = RegexExtractionStrategy(custom=price_pattern)

# Method 极速赛车3: Generate pattern with LLM assistance (one-time)
from crawl4ai import LLMConfig

async with AsyncWebCrawler() as crawler:
    # Get sample HTML first
    sample_result = await crawler.arun("https://example.com/products")
    html = sample_result.fit_html
    
    # Generate regex pattern once
    pattern = RegexExtractionStrategy.generate_pattern(
        label="price",
        html=html,
        query="Product prices in USD format",
        llm_config=极速赛车LLMConfig(provider="open极速赛车ai/gpt-4o-mini")
    )
    
    # Save pattern for reuse
    import json
    with open("price_pattern.json", "w") as f:
        json.dump(pattern, f)
    
    # Use pattern for extraction (no LLM calls)
    strategy = RegexExtractionStrategy(custom=pattern)
    result = await crawler.arun(
        url="https://example.com/products",
        config=CrawlerRunConfig(extraction_strategy=strategy)
    )
    
    # Process results
    data = json.loads(result.extracted_content)
    for item in data:
        print(f"{item['label']}: {item['value']}")
```

### CSS 抽取

```python
from crawl4ai import JsonCssExtractionStrategy

# Define schema
schema = {
    "name": "Product List",
    "baseSelector": ".product-card",
    "fields": [
        {
            "name": "title",
            "selector": "h2.title",
            "type": "text"
        },
        {
            "name": "price",
            "selector": ".price",
            "type": "text",
            "transform": "strip"
        },
        {
            "name": "image",
            "selector": "img",
            "type": "attribute",
            "attribute": "src"
        }
    ]
}

# Create and use strategy
strategy = JsonCssExtractionStrategy(schema)
result = await crawler.arun(
    url="极速赛车https://example.com/products",
    extraction_strategy=strategy
)
```

### 内容分块

```python
from crawl4ai.chunking_strategy import OverlappingWindowChunking
from crawl4ai import LLMConfig

# Create chunking strategy
chunker = OverlappingWindowChunking(
    window_size=500,  # 500 words per chunk
    overlap=50        # 50 words overlap
)

# Use with extraction strategy
strategy = LLMExtractionStrategy(
    llm_config = LLMConfig(provider="ollama/llama2"),
    chunking_strategy=chunker
)

result = await crawler.arun(
    url="https://example.com/long-article",
    extraction_strategy=strategy
)
```

## 最佳实践

1. **选择正确的策略**
   - 使用 `RegexExtractionStrategy` 处理常见数据类型，如电子邮件、电话、URL、日期
   - 使用 `JsonCssExtractionStrategy` 处理具有一致模式的良好结构化 HTML
   - 使用 `LLMExtractionStrategy` 处理需要推理的复杂非结构化内容
   - 使用 `CosineStrategy` 进行内容相似性和聚类

2. **策略选择指南**
   ```
   目标数据是常见类型（电子邮件/电话/日期/URL）吗？
   → RegexExtractionStrategy
   
   页面是否具有一致的 HTML 结构？
   → JsonCssExtractionStrategy 或 JsonXPathExtractionStrategy
   
   数据在语义上复杂或非结构化吗？
   → LLMExtractionStrategy
   
   需要查找与特定主题相似的内容吗？
   → CosineStrategy
   ```

3. **优化分块**
   ```python
   # 对于长文档
   strategy = LLMExtractionStrategy(
       chunk_token_threshold=2000,  # 更小的块
       overlap_rate=0.1           # 10% 重叠
   )
   ```

4. **结合策略以获得最佳性能**
   ```python
   # 第一遍：使用 CSS 抽取结构
   css_strategy = JsonCssExtractionStrategy(product_schema)
   css_result = await crawler.arun(url, config=CrawlerRunConfig(extraction_strategy=css_strategy))
   product_data = json.loads(css_result.extracted_content)
   
   # 第二遍：使用正则表达式抽取特定字段
   descriptions = [product["description"] for product in product_data]
   regex_strategy = RegexExtractionStrategy(
       pattern=RegexExtractionStrategy.Email | RegexExtractionStrategy.PhoneUS,
       custom={"dimension": r"\d+x\d+x\d+ (?:cm|in)"}
   )
   
   # 使用正则表达式处理描述
   for text in descriptions:
       matches = regex_strategy.extract("", text)  # 直接抽取
   ```

5. **处理错误**
   ```python
   try:
       result = await crawler.arun(
           url="https://example.com",
           extraction_strategy=strategy
       )
       if result.success:
           content = json.loads(result.extracted_content)
   except Exception as e:
       print(f"Extraction failed: {e}")
   ```

6. **监控性能**
   ```python
   strategy = CosineStrategy(
       verbose=True,  # 启用日志记录
       word_count_threshold=20,  # 过滤短内容
       top_k=5  # 限制结果数量
   )
   ```

7. **缓存生成的模式**
   ```python
   # 对于 RegexExtractionStrategy 模式生成
   import json
   from pathlib import Path
   
   cache_dir = Path("./pattern_cache")
   cache_dir.mkdir(exist_ok=True)
   pattern_file = cache_dir / "product_pattern.json"
   
   if pattern_file.exists():
       with open(pattern_file) as f:
           pattern = json.load(f)
   else:
       # 使用 LLM 生成一次
       pattern = RegexExtractionStrategy.generate_pattern(...)
       with open(pattern_file, "w") as f:
           json.dump(pattern, f)
   ```