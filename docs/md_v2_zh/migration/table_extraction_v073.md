# 迁移指南：表格提取 v0.7.3

## 概述

版本 0.7.3 引入了**表格提取策略模式**，提供了更灵活和可扩展的表格提取方法，同时保持完全向后兼容。

## 新增功能

### 策略模式实现

表格提取现在遵循 Crawl4AI 中使用的相同策略模式：

- **一致的架构**：与提取、分块和 Markdown 策略保持一致
- **可扩展性**：易于创建自定义表格提取策略
- **更好的分离**：表格逻辑从内容抓取移至专用模块
- **完全控制**：对表格检测和提取的细粒度控制

### 新类

```python
from crawl4ai import (
    TableExtractionStrategy,    # 抽象基类
    DefaultTableExtraction,      # 当前实现（默认）
    NoTableExtraction           # 显式禁用提取
)
```

## 向后兼容性

**✅ 所有现有代码无需更改即可继续工作。**

### 无需更改

如果您的代码如下所示，它将继续工作：

```python
# 这仍然完全一样地工作
config = CrawlerRunConfig(
    table_score_threshold=7
)
result = await crawler.arun(url, config)
tables = result.tables  # 相同的结构，相同的数据
```

### 幕后变化

当您未指定 `table_extraction` 策略时：

1. `CrawlerRunConfig` 自动创建 `DefaultTableExtraction`
2. 它使用您的 `table_score_threshold` 参数
3. 表格与之前完全相同的方式提取
4. 结果以相同结构出现在 `result.tables` 中

## 新功能

### 1. 显式策略配置

您现在可以显式配置表格提取：

```python
# 新增：显式控制
strategy = DefaultTableExtraction(
    table_score_threshold=7,
    min_rows=2,              # 新增：最小行过滤器
    min_cols=2,              # 新增：最小列过滤器
    verbose=True             # 新增：详细日志记录
)

config = CrawlerRunConfig(
    table_extraction=strategy
)
```

### 2. 禁用表格提取

在不需要表格时提高性能：

```python
# 新增：完全跳过表格提取
config = CrawlerRunConfig(
    table_extraction=NoTableExtraction()
)
# 不花费 CPU 周期进行表格检测/提取
```

### 3. 自定义提取策略

创建专门的提取器：

```python
class MyTableExtractor(TableExtractionStrategy):
    def extract_tables(self, element, **kwargs):
        # 自定义提取逻辑
        return custom_tables

config = CrawlerRunConfig(
    table_extraction=MyTableExtractor()
)
```

## 迁移场景

### 场景 1：基本用法（无需更改）

**之前 (v0.7.2):**
```python
config = CrawlerRunConfig()
result = await crawler.arun(url, config)
for table in result.tables:
    print(table['headers'])
```

**之后 (v0.7.3):**
```python
# 完全一样 - 无需更改
config = CrawlerRunConfig()
result = await crawler.arun(url, config)
for table in result.tables:
    print(table['headers'])
```

### 场景 2：自定义阈值（无需更改）

**之前 (v0.7.2):**
```python
config = CrawlerRunConfig(
    table_score_threshold=5
)
```

**之后 (v0.7.3):**
```python
# 仍然同样工作
config = CrawlerRunConfig(
    table_score_threshold=5
)

# 或使用新的显式方法获得更多控制
strategy = DefaultTableExtraction(
    table_score_threshold=5,
    min_rows=2  # 额外过滤
)
config = CrawlerRunConfig(
    table_extraction=strategy
)
```

### 场景 3：高级过滤（新功能）

**之前 (v0.7.2):**
```python
# 必须在提取后过滤
config = CrawlerRunConfig(
    table_score_threshold=5
)
result = await crawler.arun(url, config)

# 手动过滤
large_tables = [
    t for t in result.tables 
    if len(t['rows']) >= 5 and len(t['headers']) >= 3
]
```

**之后 (v0.7.3):**
```python
# 在提取过程中过滤（更高效）
strategy = DefaultTableExtraction(
    table_score_threshold=5,
    min_rows=5,
    min_cols=3
)
config = CrawlerRunConfig(
    table_extraction=strategy
)
result = await crawler.arun(url, config)
# result.tables 已经过过滤
```

## 代码组织变更

### 模块结构

**之前 (v0.7.2):**
```
crawl4ai/
  content_scraping_strategy.py
    - LXMLWebScrapingStrategy
      - is_data_table()      # 表格检测
      - extract_table_data() # 表格提取
```

**之后 (v0.7.3):**
```
crawl4ai/
  content_scraping_strategy.py
    - LXMLWebScrapingStrategy
      # 表格方法已移除，使用策略
  
  table_extraction.py (新增)
    - TableExtractionStrategy    # 基类
    - DefaultTableExtraction      # 移动的逻辑
    - NoTableExtraction          # 新选项
```

### 导入变更

**新的导入可用（可选）：**
```python
# 这些现在可用，但现有代码不需要
from crawl4ai import (
    TableExtractionStrategy,
    DefaultTableExtraction,
    NoTableExtraction
)
```

## 性能影响

### 无性能影响

对于现有代码，性能保持相同：
- 相同的提取逻辑
- 相同的评分算法
- 相同的处理时间

### 可用的性能改进

新选项可实现更好的性能：

```python
# 完全跳过表格（更快）
config = CrawlerRunConfig(
    table_extraction=NoTableExtraction()
)

# 仅处理特定区域（更快）
config = CrawlerRunConfig(
    css_selector="main.content",
    table_extraction=DefaultTableExtraction(
        min_rows=5,  # 跳过小表格
        min_cols=3
    )
)
```

## 测试您的迁移

### 验证脚本

运行此脚本以验证您的提取是否仍然有效：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def verify_extraction():
    url = "your_url_here"
    
    async with AsyncWebCrawler() as crawler:
        # Test 1: 旧方法
        config_old = CrawlerRunConfig(
            table_score_threshold=7
        )
        result_old = await crawler.arun(url, config_old)
        
        # Test 2: 新的显式方法
        from crawl4ai import DefaultTableExtraction
        config_new = CrawlerRunConfig(
            table_extraction=DefaultTableExtraction(
                table_score_threshold=7
            )
        )
        result_new = await crawler.arun(url, config_new)
        
        # 比较结果
        assert len(result_old.tables) == len(result_new.tables)
        print(f"✓ 两种方法都提取了 {len(result_old.tables)} 个表格")
        
        # 验证结构
        for old, new in zip(result_old.tables, result_new.tables):
            assert old['headers'] == new['headers']
            assert old['rows'] == new['rows']
        
        print("✓ 表格内容相同")

asyncio.run(verify_extraction())
```

## 弃用说明

### 无弃用

- 所有现有参数继续有效
- `CrawlerRunConfig` 中的 `table_score_threshold` 仍然受支持
- 无破坏性变更

### 内部变更（对用户透明）

- `LXMLWebScrapingStrategy.is_data_table()` - 移至 `DefaultTableExtraction`
- `LXMLWebScrapingStrategy.extract_table_data()` - 移至 `DefaultTableExtraction`

这些方法是内部的，不属于公共 API。

## 升级的好处

虽然不是必需的，但使用新模式提供：

1. **更好的控制**：在提取过程中过滤表格，而不是之后
2. **性能选项**：不需要时跳过提取
3. **可扩展性**：为特定需求创建自定义提取器
4. **一致性**：与其他 Crawl4AI 策略相同的模式
5. **面向未来**：为即将到来的高级策略做好准备

## 故障排除

### 问题：表格数量不同

**原因**：阈值或过滤差异

**解决方案**：
```python
# 确保相同的阈值
strategy = DefaultTableExtraction(
    table_score_threshold=7,  # 匹配您的旧设置
    min_rows=0,               # 无过滤（默认）
    min_cols=0                # 无过滤（默认）
)
```

### 问题：导入错误

**原因**：使用新类但未导入

**解决方案**：
```python
# 如果使用新功能，请添加导入
from crawl4ai import (
    DefaultTableExtraction,
    NoTableExtraction,
    TableExtractionStrategy
)
```

### 问题：自定义策略不工作

**原因**：方法签名不正确

**解决方案**：
```python
class CustomExtractor(TableExtractionStrategy):
    def extract_tables(self, element, **kwargs):  # 正确的签名
        # 不是：extract_tables(self, html)
        # 不是：extract(self, element)
        return tables_list
```

## 获取帮助

如果遇到问题：

1. 检查您的 `table_score_threshold` 是否与之前的设置匹配
2. 如果使用新类，请验证导入
3. 启用详细日志记录：`DefaultTableExtraction(verbose=True)`
4. 查看[表格提取文档](../core/table_extraction.md)
5. 检查[示例](../examples/table_extraction_example.py)

## 总结

- ✅ **完全向后兼容** - 无需代码更改
- ✅ **相同的结果** - 默认情况下相同的提取行为
- ✅ **新选项** - 需要时提供额外控制
- ✅ **更好的架构** - 与 Crawl4AI 模式一致
- ✅ **面向未来** - 为高级策略奠定基础

迁移到 v0.7.3 是无缝的，无需任何更改，同时为需要的人提供新功能。