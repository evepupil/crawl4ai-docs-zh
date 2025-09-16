# Fit Markdown 与剪枝和 BM25 的结合

**Fit Markdown** 是您页面 Markdown 的一个专门**过滤**版本，专注于最相关的内容。默认情况下，Crawl4AI 将整个 HTML 转换为广泛的**raw_markdown**。通过 fit markdown，我们应用**内容过滤**算法（例如**剪枝**或**BM25**）来移除或排名低价值部分——例如重复的侧边栏、浅层文本块或不相关内容——留下简洁的文本“核心”。

---

## 1. “Fit Markdown” 的工作原理

### 1.1 `content_filter`

在 **`CrawlerRunConfig`** 中，您可以指定一个 **`content_filter`** 来在最终 Markdown 生成之前塑造内容的剪枝或排名方式。过滤器的逻辑在 HTML→Markdown 过程**之前**或**期间**应用，产生：

- **`result.markdown.raw_markdown`**（未过滤）
- **`result.markdown.fit_markdown`**（过滤或“fit”版本）
- **`result.markdown.fit_html`**（产生 `fit_markdown` 的对应 HTML 片段）

### 1.2 常见过滤器

1. **PruningContentFilter** – 通过文本密度、链接密度和标签重要性为每个节点评分，丢弃低于阈值的节点。  
2. **BM25ContentFilter** – 使用 BM25 排名专注于文本相关性，如果您有特定的用户查询（例如“机器学习”或“食物营养”），这尤其有用。

---

## 2. PruningContentFilter

**剪枝**基于**文本密度、链接密度和标签重要性**丢弃不太相关的节点。这是一种基于启发式的方法——如果某些部分看起来太“稀疏”或太“垃圾”，它们就会被剪枝。

### 2.1 使用示例

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def main():
    # Step 1: Create a pruning filter
    prune_filter = PruningContentFilter(
        # Lower → more content retained, higher → more content pruned
        threshold=0.45,           
        # "fixed" or "dynamic"
        threshold_type="dynamic",  
        # Ignore nodes with <5 words
        min_word_threshold=5      
    )

    # Step 2: Insert it into a Markdown Generator
    md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)
    
    # Step 3: Pass it to CrawlerRunConfig
    config = CrawlerRunConfig(
        markdown_generator=md_generator
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://news.ycombinator.com", 
            config=config
        )
        
        if result.success:
            # 'fit_markdown' is your pruned content, focusing on "denser" text
            print("Raw Markdown length:", len(result.markdown.raw_markdown))
            print("Fit Markdown length:", len(result.markdown.fit_markdown))
        else:
            print("Error:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
```

### 2.2 关键参数

- **`min_word_threshold`** (int): 如果一个块的单词数少于这个值，它将被剪枝。  
- **`threshold_type`** (str):
  - `"fixed"` → 每个节点必须超过 `threshold`（0–1）。  
  - `"dynamic"` → 节点评分根据标签类型、文本/链接密度等调整。  
- **`threshold`** (float, 默认 ~0.48): 基础或“锚点”截止值。

**算法因素**:

- **文本密度** – 鼓励具有较高文本与整体内容比例的块。  
- **链接密度** – 惩罚主要是链接的部分。  
- **标签重要性** – 例如，`<article>` 或 `<p>` 可能比 `<div>` 更重要。  
- **结构上下文** – 如果一个节点深度嵌套或在疑似侧边栏中，它可能会被降级。

---

## 3. BM25ContentFilter

**BM25** 是一种经典的文本排名算法，常用于搜索引擎。如果您有**用户查询**或依赖页面元数据来推导查询，BM25 可以识别哪些文本块最匹配该查询。

### 3.1 使用示例

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def main():
    # 1) A BM25 filter with a user query
    bm25_filter = BM25ContentFilter(
        user_query="startup fundraising tips",
        # Adjust for stricter or looser results
        bm25_threshold=1.2  
    )

    # 2) Insert into a Markdown Generator
    md_generator = DefaultMarkdownGenerator(content_filter=bm25_filter)
    
    # 3) Pass to crawler config
    config = CrawlerRunConfig(
        markdown_generator=md_generator
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://news.ycombinator.com", 
            config=config
        )
        if result.success:
            print("Fit Markdown (BM25 query-based):")
            print(result.markdown.fit_markdown)
        else:
            print("Error:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
```

### 3.2 参数

- **`user_query`** (str, 可选): 例如 `"machine learning"`。如果为空，过滤器会尝试从页面元数据中收集查询。  
- **`bm25_threshold`** (float, 默认 1.0):  
  - 更高 → 更少的块但更相关。  
  - 更低 → 更包容。  

> 在更高级的场景中，您可能会看到诸如 `language`、`case_sensitive` 或 `priority_tags` 等参数，以优化文本的分词或加权方式。

---

## 4. 访问“Fit”输出

爬取后，您的“fit”内容可以在 **`result.markdown.fit_markdown`** 中找到。

```python
fit_md = result.markdown.fit_markdown
fit_html = result.markdown.fit_html
```

如果内容过滤器是 **BM25**，您可能会在 `fit_markdown` 中看到额外的逻辑或引用，以突出显示相关段。如果是**剪枝**，文本通常会被很好地清理，但不一定与查询匹配。

---

## 5. 代码模式回顾

### 5.1 剪枝

```python
prune_filter = PruningContentFilter(
    threshold=0.5,
    threshold_type="fixed",
    min_word_threshold=10
)
md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)
config = CrawlerRunConfig(markdown_generator=md_generator)
```

### 5.2 BM25

```python
bm25_filter = BM25ContentFilter(
    user_query="health benefits fruit",
    bm25_threshold=1.2
)
md_generator = DefaultMarkdownGenerator(content_filter=bm25_filter)
config = CrawlerRunConfig(markdown_generator=md_generator)
```

---

## 6. 与“word_count_threshold”和排除项结合使用

请记住，您还可以指定：

```python
config = CrawlerRunConfig(
    word_count_threshold=10,
    excluded_tags=["nav", "footer", "header"],
    exclude_external_links=True,
    markdown_generator=DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=0.5)
    )
)
```

因此，**多级**过滤发生：

1. 爬取器的 `excluded_tags` 首先从 HTML 中移除。  
2. 内容过滤器（剪枝、BM25 或自定义）对剩余的文本块进行剪枝或排名。  
3. 最终的“fit”内容在 `result.markdown.fit_markdown` 中生成。

---

## 7. 自定义过滤器

如果您需要不同的方法（如专门的 ML 模型或站点特定的启发式方法），您可以创建一个继承自 `RelevantContentFilter` 的新类，并实现 `filter_content(html)`。然后将其注入到您的**Markdown生成器**中：

```python
from crawl4ai.content_filter_strategy import RelevantContentFilter

class MyCustomFilter(RelevantContentFilter):
    def filter_content(self, html, min_word_threshold=None):
        # parse HTML, implement custom logic
        return [block for block in ... if ... some condition...]

```

**步骤**:

1. 子类化 `RelevantContentFilter`。  
2. 实现 `filter_content(...)`。  
3. 在您的 `DefaultMarkdownGenerator(content_filter=MyCustomFilter(...))` 中使用它。

---

## 8. 最后思考

**Fit Markdown** 是一个关键特性，适用于：

- **摘要**：快速从杂乱页面中获取重要文本。  
- **搜索**：结合 **BM25** 产生与查询相关的内容。  
- **AI 管道**：过滤掉样板内容，以便基于 LLM 的提取或摘要运行在更密集的文本上。

**关键点**:
- **PruningContentFilter**：如果您只想要最“有料”的文本而没有用户查询，这很棒。  
- **BM25ContentFilter**：非常适合基于查询的提取或搜索。  
- 结合 **`excluded_tags`、`exclude_external_links`、`word_count_threshold`** 来优化您的最终“fit”文本。  
- Fit markdown 最终出现在 **`result.markdown.fit_markdown`** 中；未来版本中最终将是 **`result.markdown.fit_markdown`**。

借助这些工具，您可以**聚焦**于真正重要的文本，忽略垃圾或样板内容，并为您的 AI 或数据管道生成简洁、相关的“fit markdown”。祝您剪枝和搜索愉快！

- 最后更新：2025-01-01