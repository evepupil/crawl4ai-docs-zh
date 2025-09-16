# 表格提取策略

## 概述

**v0.7.3+ 新增功能**：表格提取现在遵循**策略设计模式**，为处理不同表格结构提供了前所未有的灵活性和能力。别担心——**您现有的代码仍然有效！** 我们在提供新功能的同时保持了完全的向后兼容性。

### 有哪些变化？
- **架构**：表格提取现在使用可插拔策略
- **向后兼容**：您使用 `table_score_threshold` 的现有代码继续有效
- **更强大**：可从多种策略中选择或创建自己的策略
- **相同的默认行为**：默认使用 `DefaultTableExtraction`（与之前相同）

### 关键点
✅ **旧代码仍然有效** - 无破坏性变更  
✅ **相同的默认行为** - 使用经过验证的提取算法  
✅ **新功能** - 需要时可添加 LLM 提取或自定义策略  
✅ **策略模式** - 清晰、可扩展的架构

## 快速开始

### 最简单的方法（与之前一样工作）

如果您已经在使用 Crawl4AI，一切照旧：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def extract_tables():
    async with AsyncWebCrawler() as crawler:
        # 这与之前完全一样 - 内部使用 DefaultTableExtraction
        result = await crawler.arun("https://example.com/data")
        
        # 表格会自动提取并可在 result.tables 中获取
        for table in result.tables:
            print(f"Table with {len(table['rows'])} rows and {len(table['headers'])} columns")
            print(f"Headers: {table['headers']}")
            print(f"First row: {table['rows'][0] if table['rows'] else 'No data'}")

asyncio.run(extract_tables())
```

### 使用旧配置（仍然支持）

您使用 `table_score_threshold` 的现有代码继续有效：

```python
# 这种旧方法仍然有效 - 我们保持向后兼容性
config = CrawlerRunConfig(
    table_score_threshold=7  # 内部创建 DefaultTableExtraction(table_score_threshold=7)
)
result = await crawler.arun(url, config)
```

## 表格提取策略

### 理解策略模式

策略模式允许您在运行时选择不同的表格提取算法。可以将其视为工具箱中的不同工具 - 您为工作选择合适的工具：

- **没有显式策略？** → 自动使用 `DefaultTableExtraction`（与 v0.7.2 及更早版本相同）
- **需要处理复杂表格？** → 选择 `LLMTableExtraction`（需要付费，谨慎使用）
- **想要禁用表格提取？** → 使用 `NoTableExtraction`
- **有特殊需求？** → 创建自定义策略

### 可用策略

| 策略 | 描述 | 使用场景 | 成本 | 何时使用 |
|----------|-------------|----------|------|-------------|
| `DefaultTableExtraction` | **推荐**：与 v0.7.3 之前相同的算法 | 通用目的（默认） | 免费 | **首先使用此策略 - 处理 95% 的情况** |
| `LLMTableExtraction` | AI 驱动的复杂表格提取 | 具有复杂 rowspan/colspan 的表格 | **$$$ 每次 API 调用** | 仅当 DefaultTableExtraction 失败时 |
| `NoTableExtraction` | 禁用表格提取 | 不需要表格时 | 免费 | 仅用于文本提取 |
| 自定义策略 | 用户定义的提取逻辑 | 特殊需求 | 免费 | 领域特定需求 |

> **⚠️ LLMTableExtraction 的关键成本警告**： 
> 
> **除非绝对必要，否则不要使用 `LLMTableExtraction`！**
> 
> - **始终先尝试 `DefaultTableExtraction`** - 它是免费的且能完美处理大多数表格
> - LLM 提取**每次 API 调用都要花钱**
> - 对于大型表格（100+ 行），LLM 提取可能**非常慢**
> - **对于大型表格**：如果必须使用 LLM，请选择快速提供商：
>   - ✅ **Groq**（最快推理）
>   - ✅ **Cerebras**（速度优化）
>   - ⚠️ 避免使用：OpenAI、Anthropic 处理大型表格（较慢）
> 
> **🚧 进行中的工作**： 
> 我们正在积极开发一种**高级非 LLM 算法**，将**免费**处理复杂表格结构（rowspan、colspan、嵌套表格）。这将取代大多数情况下昂贵的 LLM 提取需求。即将推出！

### DefaultTableExtraction

默认策略使用复杂的评分系统来识别数据表格：

```python
from crawl4ai import DefaultTableExtraction, CrawlerRunConfig

# 自定义默认提取
table_strategy = DefaultTableExtraction(
    table_score_threshold=7,  # 评分阈值（默认：7）
    min_rows=2,               # 所需最小行数
    min_cols=2,               # 所需最小列数
    verbose=True              # 启用详细日志记录
)

config = CrawlerRunConfig(
    table_extraction=table_strategy
)
```

#### 评分系统

评分系统评估多个因素：

| 因素 | 分数影响 | 描述 |
|--------|--------------|-------------|
| 有 `<thead>` | +2 | 语义表格结构 |
| 有 `<tbody>` | +1 | 有组织的表格主体 |
| 有 `<th>` 元素 | +2 | 存在标题单元格 |
| 标题位置正确 | +1 | 正确的语义结构 |
| 一致的列数 | +2 | 规则的数据结构 |
| 有标题 | +2 | 描述性标题 |
| 有摘要 | +1 | 摘要属性 |
| 高文本密度 | +2 到 +3 | 内容丰富的单元格 |
| 数据属性 | 每个 +0.5 | Data-* 属性 |
| 嵌套表格 | -3 | 通常表示布局 |
| Role="presentation" | -3 | 明确非数据 |
| 行数太少 | -2 | 数据不足 |

### LLMTableExtraction（谨慎使用！）

**⚠️ 警告**：仅当 `DefaultTableExtraction` 无法处理复杂表格时使用！

LLMTableExtraction 使用 AI 来理解传统解析器难以处理的复杂表格结构。它通过智能分块和并行处理自动处理大型表格：

```python
from crawl4ai import LLMTableExtraction, LLMConfig, CrawlerRunConfig

# 配置 LLM（每次调用都要花钱！）
llm_config = LLMConfig(
    provider="groq/llama-3.3-70b-versatile",  # 大型表格的快速提供商
    api_token="your_api_key",
    temperature=0.1
)

# 创建具有智能分块的 LLM 提取策略
table_strategy = LLMTableExtraction(
    llm_config=llm_config,
    max_tries=3,                      # 如果提取失败，最多重试 3 次
    css_selector="table",             # 可选：专注于特定表格
    enable_chunking=True,             # 自动分块大型表格（默认：True）
    chunk_token_threshold=3000,       # 超过此值时拆分表格（默认：3000 tokens）
    min_rows_per_chunk=10,            # 每个分块的最小行数（默认：10）
    max_parallel_chunks=5,            # 最多并行处理 5 个分块（默认：5）
    verbose=True
)

config = CrawlerRunConfig(
    table_extraction=table_strategy
)

result = await crawler.arun(url, config)
```

#### 何时使用 LLMTableExtraction

✅ **仅在以下情况下使用**：
- 表格有复杂的合并单元格（rowspan/colspan）导致 DefaultTableExtraction 失败
- 需要语义理解的嵌套表格
- 结构不规则的表格
- 您已尝试 DefaultTableExtraction 但失败了

❌ **绝不使用的情况**：
- DefaultTableExtraction 有效（99% 的情况）
- 表格简单或结构良好
- 您正在处理许多页面（成本累积！）
- 表格有 100+ 行（非常慢）

#### 智能分块工作原理

LLMTableExtraction 通过智能分块自动处理大型表格：

1. **自动检测**：超过 token 阈值的表格会自动拆分
2. **智能拆分**：在行边界创建分块，保留表格结构
3. **标题保留**：每个分块包含原始标题以提供上下文
4. **并行处理**：同时处理多个分块以提高速度
5. **智能合并**：结果合并回一个完整的表格

**分块参数**：
- `enable_chunking`（默认：`True`）：自动处理大型表格
- `chunk_token_threshold`（默认：`3000`）：何时拆分表格
- `min_rows_per_chunk`（默认：`10`）：确保有意义的分块大小
- `max_parallel_chunks`（默认：`5`）：并发处理以提高速度

分块完全透明 - 无论表格是单块处理还是多块处理，您都会获得相同的输出格式。

#### LLMTableExtraction 的性能优化

**按表格大小推荐的提供商**：

| 表格大小 | 推荐提供商 | 原因 |
|------------|----------------------|-----|
| 小（<50 行） | 任何提供商 | 足够快 |
| 中（50-200 行） | Groq、Cerebras | 优化推理 |
| 大（200+ 行） | **Groq**（最佳）、Cerebras | 最快推理 + 自动分块 |
| 非常大（500+ 行） | 带分块的 Groq | 并行处理保持快速 |

### NoTableExtraction

在不需要表格时禁用表格提取以提高性能：

```python
from crawl4ai import NoTableExtraction, CrawlerRunConfig

config = CrawlerRunConfig(
    table_extraction=NoTableExtraction()
)

# 不会提取表格，提高性能
result = await crawler.arun(url, config)
assert len(result.tables) == 0
```

## 提取的表格结构

每个提取的表格包含：

```python
{
    "headers": ["列 1", "列 2", ...],  # 列标题
    "rows": [                                   # 数据行
        ["行 1 列 1", "行 1 列 2", ...],
        ["行 2 列 1", "行 2 列 2", ...],
    ],
    "caption": "表格标题",                # 如果存在
    "summary": "表格摘要",                # 如果存在
    "metadata": {
        "row_count": 10,                       # 行数
        "column_count": 3,                      # 列数
        "has_headers": True,                    # 检测到标题
        "has_caption": True,                    # 存在标题
        "has_summary": False,                   # 存在摘要
        "id": "data-table-1",                   # 表格 ID（如果存在）
        "class": "financial-data"               # 表格类（如果存在）
    }
}
```

## 配置选项

### 基本配置

```python
config = CrawlerRunConfig(
    # 表格提取设置
    table_score_threshold=7,      # 默认阈值（向后兼容）
    table_extraction=strategy,     # 可选：自定义策略
    
    # 过滤要处理的内容
    css_selector="main",          # 专注于特定区域
    excluded_tags=["nav", "aside"] # 排除页面部分
)
```

### 高级配置

```python
from crawl4ai import DefaultTableExtraction, CrawlerRunConfig

# 微调提取
strategy = DefaultTableExtraction(
    table_score_threshold=5,      # 更低 = 更宽松
    min_rows=3,                   # 至少需要 3 行
    min_cols=2,                   # 至少需要 2 列
    verbose=True                  # 详细日志记录
)

config = CrawlerRunConfig(
    table_extraction=strategy,
    css_selector="article.content", # 目标特定内容
    exclude_domains=["ads.com"],   # 排除广告域名
    cache_mode=CacheMode.BYPASS    # 全新提取
)
```

## 处理提取的表格

### 转换为 Pandas DataFrame

```python
import pandas as pd

async def tables_to_dataframes(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        
        dataframes = []
        for table_data in result.tables:
            # 创建 DataFrame
            if table_data['headers']:
                df = pd.DataFrame(
                    table_data['rows'],
                    columns=table_data['headers']
                )
            else:
                df = pd.DataFrame(table_data['rows'])
            
            # 添加元数据作为 DataFrame 属性
            df.attrs['caption'] = table_data.get('caption', '')
            df.attrs['metadata'] = table_data.get('metadata', {})
            
            dataframes.append(df)
        
        return dataframes
```

### 按条件过滤表格

```python
async def extract_large_tables(url):
    async with AsyncWebCrawler() as crawler:
        # 配置最小尺寸要求
        strategy = DefaultTableExtraction(
            min_rows=10,
            min_cols=3,
            table_score_threshold=6
        )
        
        config = CrawlerRunConfig(
            table_extraction=strategy
        )
        
        result = await crawler.arun(url, config)
        
        # 进一步过滤结果
        large_tables = [
            table for table in result.tables
            if table['metadata']['row_count'] > 10
            and table['metadata']['column_count'] > 3
        ]
        
        return large_tables
```

### 导出表格到不同格式

```python
import json
import csv

async def export_tables(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        
        for i, table in enumerate(result.tables):
            # 导出为 JSON
            with open(f'table_{i}.json', 'w') as f:
                json.dump(table, f, indent=2)
            
            # 导出为 CSV
            with open(f'table_{i}.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                if table['headers']:
                    writer.writerow(table['headers'])
                writer.writerows(table['rows'])
            
            # 导出为 Markdown
            with open(f'table_{i}.md', 'w') as f:
                # 写入标题
                if table['headers']:
                    f.write('| ' + ' | '.join(table['headers']) + ' |\n')
                    f.write('|' + '---|' * len(table['headers']) + '\n')
                
                # 写入行
                for row in table['rows']:
                    f.write('| ' + ' | '.join(str(cell) for cell in row) + ' |\n')
```

## 创建自定义策略

扩展 `TableExtractionStrategy` 以创建自定义提取逻辑：

### 示例：财务表格提取器

```python
from crawl4ai import TableExtractionStrategy
from typing import List, Dict, Any
import re

class FinancialTableExtractor(TableExtractionStrategy):
    """提取包含财务数据的表格。"""
    
    def __init__(self, currency_symbols=None, require_numbers=True, **kwargs):
        super().__init__(**kwargs)
        self.currency_symbols = currency_symbols or ['$', '€', '£', '¥']
        self.require_numbers = require_numbers
        self.number_pattern = re.compile(r'\d+[,.]?\d*')
    
    def extract_tables(self, element, **kwargs):
        tables_data = []
        
        for table in element.xpath(".//table"):
            # 检查表格是否包含财务指标
            table_text = ''.join(table.itertext())
            
            # 必须包含货币符号
            has_currency = any(sym in table_text for sym in self.currency_symbols)
            if not has_currency:
                continue
            
            # 如果需要，必须包含数字
            if self.require_numbers:
                numbers = self.number_pattern.findall(table_text)
                if len(numbers) < 3:  # 任意最小值
                    continue
            
            # 提取表格数据
            table_data = self._extract_financial_data(table)
            if table_data:
                tables_data.append(table_data)
        
        return tables_data
    
    def极_extract_financial_data(self, table):
        """从表格中提取并清理财务数据。"""
        headers = []
        rows = []
        
        # 提取标题
        for th in table极xpath(".//thead//th | .//tr[1]//th"):
            headers.append(th.text_content().strip())
        
        # 提取并清理行
        for tr in table极xpath(".//tbody//tr | .//tr[position()>1]"):
            row = []
            for td in tr极xpath(".//td"):
                text = td.text_content().strip()
                # 清理货币格式
                text = re.sub(r'[$€£¥,]', '', text)
                row.append(text)
            if row:
                rows.append(row)
        
        return {
            "headers": headers,
            "rows": rows,
            "caption": self._get_caption(table),
            "summary": table.get("summary", ""),
            "metadata": {
                "type": "financial",
                "row_count": len(rows),
                "column_count": len(headers) or len(rows[0]) if rows else 0
            }
        }
    
    def _get_caption(self, table):
        caption = table极xpath(".//caption/text()")
        return caption[0].strip() if caption else ""

# 用法
strategy = FinancialTableExtractor(
    currency_symbols=['$', 'EUR'],
    require_numbers=True
)

config = CrawlerRunConfig(
    table_extraction=strategy
)
```

### 示例：特定表格提取器

```python
class SpecificTableExtractor(TableExtractionStrategy):
    """仅提取符合特定条件的表格。"""
    
    def __init__(self, 
                 required_headers=None, 
                 id_pattern=None,
                 class_pattern=None,
                 **kwargs):
        super().__init__(**kwargs)
极       self.required_headers = required_headers or []
        self.id_pattern = id_pattern
        self.class_pattern = class_pattern
    
    def extract_tables(self, element, **kwargs):
        tables极data = []
        
        for table in element极xpath(".//table"):
            # 检查 ID 模式
            if self.id_pattern:
                table_id = table.get('id', '')
                if not re.match(self.id_pattern, table_id):
                    continue
            
            # 检查类模式
            if self.class_pattern:
                table_class = table.get('class', '')
                if not re.match(self.class_pattern, table_class):
                    continue
            
            # 提取标题以检查要求
            headers = self._extract_headers(table)
            
            # 检查是否有所需标题
            if self.required_headers:
                if not all(req in headers for req in self.required_headers):
                    continue
            
            # 提取完整表格数据
            table_data = self._extract_table_data(table, headers)
            tables_data.append(table_data)
        
        return tables_data
```

## 与其他策略结合使用

表格提取与其他 Crawl4AI 策略无缝协作：

```python
from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    DefaultTableExtraction,
    LLMExtractionStrategy,
    JsonCssExtractionStrategy
)

async def combined_extraction(url):
    async with AsyncWebCrawler() as crawler:
        config = Crawler极RunConfig(
            # 表格提取
            table_extraction=DefaultTableExtraction(
                table_score_threshold=6,
                min_rows=2
            ),
            
            # 基于 CSS 的特定元素提取
            extraction_strategy=JsonCssExtractionStrategy({
                "title": "h1",
                "summary": "p.summary",
                "date": "time"
            }),
            
            # 专注于主要内容
            css_selector="main.content"
        )
        
        result = await crawler.arun(url, config)
        
        # 访问不同的提取结果
        tables = result.tables  # 表格数据
        structured = json.loads(result.extracted_content)  # CSS 提取
        
        return {
            "tables": tables,
            "structured_data": structured,
            "markdown": result.markdown
        }
```

## 性能考虑

### 优化技巧

1. **不需要时禁用**：如果不需要表格，使用 `NoTableExtraction`
2. **目标特定区域**：使用 `css_selector` 限制处理范围
3. **设置最小阈值**：尽早过滤掉小/不相关的表格
4. **缓存结果**：使用适当的缓存模式进行重复提取

```python
# 大型页面的优化配置
config = CrawlerRunConfig(
    # 仅处理主要内容区域
    css_selector="article.main-content",
    
    # 排除导航和侧边栏
    excluded_tags=["nav", "aside", "footer"],
    
    # 更高阈值以进行更严格过滤
    table_extraction=DefaultTableExtraction(
        table_score_threshold=8,
       极 min_rows=5,
        min_cols=3
    ),
    
    # 启用缓存以重复访问
    cache_mode=CacheMode.ENABLED
)
```

## 迁移指南

### 重要：您的代码仍然有效！

**无需更改！** 向策略模式的过渡是**完全向后兼容的**。

### 内部工作原理

#### v0.7.2 及更早版本
```python
# 旧方式 - 直接传递 table_score_threshold
config = CrawlerRunConfig(
    table_score_threshold=7
)
# 内部：无策略模式，直接实现
```

#### v0.7.3+（当前）
```python
# 旧方式仍然有效 - 我们在内部处理
config = CrawlerRunConfig(
    table_score_threshold=7
)
# 内部：自动创建 DefaultTableExtraction(table_score_threshold=7)
```

### 利用新功能

虽然您的旧代码有效，但您现在可以使用策略模式获得更多控制：

```python
# 选项 1：继续使用旧方式（完全可以！）
config = CrawlerRunConfig(
    table_score_threshold=7  # 仍然支持
)

# 选项 2：使用新策略模式（更灵活）
from crawl4ai import DefaultTableExtraction

strategy = DefaultTableExtraction(
    table_score_threshold=7,
    min_rows=2,  # 新功能！
    min_cols=2   # 新功能！
)

config = CrawlerRunConfig(
    table_extraction=strategy
)

# 选项 3：需要时使用高级策略
from crawl4ai import LLMTableExtraction, LLMConfig

# 仅用于 DefaultTableExtraction 无法处理的复杂表格
# 通过智能分块自动处理大型表格
llm_strategy = LLMTableExtraction(
    llm_config=LLMConfig(
        provider="groq/llama-3.3-70b-versatile",
        api_token="your_key"
    ),
    max_tries=3,
    enable_chunking=True,  # 自动分块大型表格
    chunk_token_threshold=3000,  # 超过 3000 tokens 时分块
    max_parallel_chunks=5  # 最多并行处理 5 个分块
)

config = CrawlerRunConfig(
    table_extraction=llm_strategy  # 具有自动分块的高级提取
)
```

### 总结

- ✅ **无破坏性变更** - 旧代码照常工作
- ✅ **相同的默认值** - 自动使用 DefaultTableExtraction
- ✅ **逐步采用** - 需要时使用新功能
- ✅ **完全兼容** - result.tables 结构不变

## 最佳实践

### 1. 选择正确的策略（成本意识方法）

**决策流程**：
```
1. 您需要表格吗？
   → 否：使用 NoTableExtraction
   → 是：继续到 #2

2. 首先尝试 DefaultTableExtraction（免费）
   → 有效？完成！ ✅
   → 失败？继续到 #3

3. 表格是否关键且复杂？
   → 否：接受 DefaultTableExtraction 结果
   → 是：继续到 #4

4. 使用 LLMTableExtraction（花钱）
   → 小表格（<50 行）：任何 LLM 提供商
   → 大表格（50+ 行）：使用 Groq 或 Cerebras
   → 非常大的表格（500+ 行）：重新考虑 - 也许分块页面
```

**策略选择指南**：
- **DefaultTableExtraction**：用于 99% 的情况 - 免费且有效
- **LLMTableExtraction**：仅用于 DefaultTableExtraction 无法处理的具有合并单元格的复杂表格
- **NoTableExtraction**：当您只需要文本/markdown 内容时
- **自定义策略**：用于特殊需求（财务、科学等）

### 2. 验证提取的数据

```python
def validate_table(table):
    """验证表格数据质量。"""
    # 检查结构
    if not table.get('rows'):
        return False
    
    # 检查一致性
    if table.get('headers'):
        expected_cols = len(table['headers'])
        for row in table['rows']:
            if len(row) != expected_cols:
                return False
    
    # 检查最小内容
    total_cells = sum(len(row) for row in table['rows'])
    non_empty = sum(1 for row in table['rows'] 
                    for cell in row if cell.strip())
    
    if non_empty / total_cells < 0.5:  # 少于 50% 非空
        return False
    
    return True

# 过滤有效表格
valid_t极ables = [t for t in result.tables if validate_table(t)]
```

### 3. 处理边缘情况

```python
async def robust_table_extraction(url):
    """具有错误处理的表格提取。"""
    async with AsyncWebCrawler() as crawler:
        try:
            config = CrawlerRunConfig(
                table_extraction=DefaultTableExtraction(
                    table_score_threshold=6,
                    verbose=True
                )
            )
            
            result = await crawler.arun(url, config)
            
            if not result.success:
                print(f"Crawl failed: {result.error}")
                return []
            
            # 安全处理表格
            processed_tables = []
            for table in result.tables:
                try:
                    # 验证和处理
                    if validate_table(table):
                        processed_tables.append(table)
                except Exception as e:
                    print(f"Error processing table: {e}")
                    continue
            
            return processed_tables
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return []
```

## 故障排除

### 常见问题和解决方案

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| 未提取表格 | 分数太高 | 降低 `table_score_threshold` |
| 包含布局表格 | 分数太低 | 增加 `table_score_threshold` |
| 缺失表格 | CSS 选择器太具体 | 扩大或移除 `css_selector` |
| 数据不完整 | 复杂表格结构 | 创建自定义策略 |
| 性能问题 | 处理整个页面 | 使用 `css_selector` 限制范围 |

### 调试日志记录

启用详细日志记录以了解提取决策：

```python
import logging

# 配置日志记录
logging.basicConfig(level=logging.DEBUG)

# 在策略中启用详细模式
strategy = DefaultTableExtraction(
    table_score_threshold=7,
    verbose=True  # 详细提取日志
)

config = CrawlerRunConfig(
    table_extraction=strategy,
    verbose=True  # 通用爬虫日志
)
```

## 另请参阅

- [提取策略](extraction-strategies.md) - 所有提取策略概述
- [内容选择](content-selection.md) - 使用 CSS 选择器和过滤器
- [性能优化](../optimization/performance-tuning.md) - 加速提取
- [示例](../examples/table_extraction_example.py) - 完整工作示例