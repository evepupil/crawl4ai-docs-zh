# Markdown 生成基础

Crawl4AI 的核心功能之一是从网页生成**干净、结构化的 markdown**。最初为解决"仅提取实际内容并丢弃样板或噪音"的问题而构建，Crawl4AI 的 markdown 系统仍然是其 AI 工作流程中最吸引人的功能之一。

在本教程中，您将学习：

1. 如何配置**默认 Markdown 生成器**  
2. **内容过滤器**（BM25 或 Pruning）如何帮助优化 markdown 并丢弃无用内容  
3. 原始 markdown (`result.markdown`) 与过滤后 markdown (`fit_markdown`) 的区别  

> **先决条件**  
> - 您已完成或阅读过 [AsyncWebCrawler 基础](../core/simple-crawling.md) 以了解如何运行简单爬取。  
> - 您知道如何配置 `CrawlerRunConfig`。

---

## 1. 快速示例

以下是一个使用 **DefaultMarkdownGenerator** 且不添加额外过滤的最小代码片段：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def main():
    config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator()
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com", config=config)
        
        if result.success:
            print("Raw Markdown Output:\n")
            print(result.markdown)  # 页面未过滤的 markdown
        else:
            print("Crawl failed:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
```

**发生了什么？**  
- `CrawlerRunConfig( markdown_generator = DefaultMarkdownGenerator() )` 指示 Crawl4AI 在每次爬取结束时将最终 HTML 转换为 markdown。  
- 生成的 markdown 可通过 `result.markdown` 访问。

---

## 2. Markdown 生成工作原理

### 2.1 HTML 到文本转换（分叉并修改）

在底层，**DefaultMarkdownGenerator** 使用专门的 HTML 到文本方法，该方法：

- 保留标题、代码块、项目符号等  
- 移除不添加有意义内容的额外标签（脚本、样式）  
- 可选择为链接生成引用或完全跳过它们  

一组**选项**（以字典形式传递）允许您精确自定义 HTML 如何转换为 markdown。这些映射到标准的 html2text 类配置以及您自己的增强功能（例如忽略内部链接、保留某些标签原样或调整行宽）。

### 2.2 链接引用

默认情况下，生成器可以将 `<a href="...">` 元素转换为 `[text][1]` 引用，然后将实际链接放在文档底部。这对于需要结构化引用的研究工作流程非常方便。

### 2.3 可选内容过滤器

在 HTML 到 Markdown 步骤之前或之后，您可以应用**内容过滤器**（如 BM25 或 Pruning）以减少噪音并生成 "fit_markdown"——一个高度修剪的版本，专注于页面的主要文本。我们稍后将介绍这些过滤器。

---

## 3. 配置默认 Markdown 生成器

您可以通过向 `DefaultMarkdownGenerator` 传递 `options` 字典来调整输出。例如：

```python
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def main():
    # 示例：忽略所有链接，不转义 HTML，并将文本换行设置为 80 个字符
    md_generator = DefaultMarkdownGenerator(
        options={
            "ignore_links": True,
            "escape_html": False,
            "body_width": 80
        }
    )

    config = CrawlerRunConfig(
        markdown_generator=md_generator
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com/docs", config=config)
        if result.success:
            print("Markdown:\n", result.markdown[:500])  # 仅显示片段
        else:
            print("Crawl failed:", result.error_message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

一些常用的 `options`：

- **`ignore_links`** (bool)：是否在最终 markdown 中移除所有超链接。  
- **`ignore_images`** (bool)：移除所有 `![image]()` 引用。  
- **`escape_html`** (bool)：将 HTML 实体转换为文本（默认为 `True`）。  
- **`body_width`** (int)：在 N 个字符处换行文本。`0` 或 `None` 表示不换行。  
- **`skip_internal_links`** (bool)：如果为 `True`，则省略 `#localAnchors` 或引用同一页面的内部链接。  
- **`include_sup_sub`** (bool)：尝试以更可读的方式处理 `<sup>` / `<sub>`。

## 4. 选择用于 Markdown 生成的 HTML 源

`content_source` 参数允许您控制将哪个 HTML 内容用作 markdown 生成的输入。这使您可以在转换为 markdown 之前灵活处理 HTML。

```python
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def main():
    # 选项 1：直接使用网页的原始 HTML（未经任何处理）
    raw_md_generator = DefaultMarkdownGenerator(
        content_source="raw_html",
        options={"ignore_links": True}
    )
    
    # 选项 2：使用清理后的 HTML（经过抓取策略处理后 - 默认）
    cleaned_md_generator = DefaultMarkdownGenerator(
        content_source="cleaned_html",  # 这是默认值
        options={"ignore_links": True}
    )
    
    # 选项 3：使用为模式提取优化的预处理 HTML
    fit_md_generator = DefaultMarkdownGenerator(
        content_source="fit_html",
        options={"ignore_links": True}
    )
    
    # 在爬取配置中使用其中一个生成器
    config = CrawlerRunConfig(
        markdown_generator=raw_md_generator  # 尝试每个生成器
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com", config=config)
        if result.success:
            print("Markdown:\n", result.markdown.raw_markdown[:500])
        else:
            print("Crawl failed:", result.error_message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### HTML 源选项

- **`"cleaned_html"`**（默认）：使用经过抓取策略处理后的 HTML。此 HTML 通常更干净，更专注于内容，并移除了一些样板内容。

- **`"raw_html"`**：直接使用网页的原始 HTML，未经任何清理或处理。这会保留更多原始内容，但可能包括导航栏、广告、页脚和其他可能与主要内容无关的元素。

- **`"fit_html"`**：使用为模式提取预处理的 HTML。此 HTML 针对结构化数据提取进行了优化，可能简化或移除了某些元素。

### 何时使用每个选项

- 使用 **`"cleaned_html"`**（默认）以获得内容保留和噪音移除之间的平衡。
- 当您需要保留所有原始内容，或清理过程移除了您实际想要保留的内容时，使用 **`"raw_html"`**。
- 当处理结构化数据或需要针对模式提取优化的 HTML 时，使用 **`"fit_html"`**。

---

## 5. 内容过滤器

**内容过滤器** 在将文本转换为 Markdown 之前有选择地移除或排名文本部分。这在页面包含广告、导航栏或其他不需要的杂乱内容时特别有用。

### 5.1 BM25ContentFilter

如果您有**搜索查询**，BM25 是一个不错的选择：

```python
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import BM25ContentFilter
from crawl4ai import CrawlerRunConfig

bm25_filter = BM25ContentFilter(
    user_query="machine learning",
    bm25_threshold=1.2,
    language="english"
)

md_generator = DefaultMarkdownGenerator(
    content_filter=bm25_filter,
    options={"ignore_links": True}
)

config = CrawlerRunConfig(markdown_generator=md_generator)
```

- **`user_query`**：您希望关注的术语。BM25 尝试仅保留与该查询相关的内容块。  
- **`bm25_threshold`**：提高它以保留更少的块；降低它以保留更多。  
- **`use_stemming`** *（默认为 `True`）*：是否对查询和内容应用词干提取。
- **`language (str)`**：词干提取的语言（默认：'english'）。

**未提供查询？** BM25 尝试从页面元数据中获取上下文，或者您可以简单地将其视为一种彻底的方法，丢弃通用分数低的文本。实际上，为了获得最佳结果，您需要提供一个查询。

### 5.2 PruningContentFilter

如果您**没有**特定查询，或者您只想要一个强大的"垃圾移除器"，请使用 `PruningContentFilter`。它分析文本密度、链接密度、HTML 结构和已知模式（如"nav"、"footer"），系统地修剪多余或重复的部分。

```python
from crawl4ai.content_filter_strategy import PruningContentFilter

prune_filter = PruningContentFilter(
    threshold=0.5,
    threshold_type="fixed",  # 或 "dynamic"
    min_word_threshold=50
)
```

- **`threshold`**：分数边界。低于此分数的块将被移除。  
- **`threshold_type`**：  
    - `"fixed"`：直接比较（`score >= threshold` 保留块）。  
    - `"dynamic"`：过滤器以数据驱动的方式调整阈值。  
- **`min_word_threshold`**：丢弃少于 N 个单词的块，因为它们可能太短或无帮助。

**何时使用 PruningContentFilter**  
- 您希望在没有用户查询的情况下进行广泛的清理。  
- 页面有许多重复的侧边栏、页脚或免责声明，妨碍文本提取。

### 5.3 LLMContentFilter

为了实现智能内容过滤和高质量的 markdown 生成，您可以使用 **LLMContentFilter**。此过滤器利用 LLM 生成相关的 markdown，同时保留原始内容的意义和结构：

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, LLMConfig, DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import LLMContentFilter

async def main():
    # 使用特定指令初始化 LLM 过滤器
    filter = LLMContentFilter(
        llm_config = LLMConfig(provider="openai/gpt-4o",api_token="your-api-token"), #或使用环境变量
        instruction="""
        专注于提取核心教育内容。
        包括：
        - 关键概念和解释
        - 重要代码示例
        - 基本技术细节
        排除：
        - 导航元素
        - 侧边栏
        - 页脚内容
        将输出格式化为带有适当代码块和标题的干净 markdown。
        """,
        chunk_token_threshold=4096,  # 根据您的需求调整
        verbose=True
    )
    md_generator = DefaultMarkdownGenerator(
        content_filter=filter,
        options={"ignore_links": True}
    )
    config = CrawlerRunConfig(
        markdown_generator=md_generator,
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com", config=config)
        print(result.markdown.fit_markdown)  # 过滤后的 markdown 内容
```

**关键特性：**
- **智能过滤**：使用 LLM 理解和提取相关内容，同时保持上下文
- **可定制指令**：通过特定指令定制过滤过程
- **分块处理**：通过处理大文档的分块（由 `chunk_token_threshold` 控制）来处理大文档
- **并行处理**：为了更好的性能，使用较小的 `chunk_token_threshold`（例如 2048 或 4096）以启用内容块的并行处理

**两种常见用例：**

1. **精确内容保留**：
```python
filter = LLMContentFilter(
    instruction="""
    提取主要教育内容，同时完全保留其原始措辞和实质。
    1. 保持精确的语言和术语
    2. 保留所有技术解释和示例
    3. 保留原始流程和结构
    4. 仅移除明显无关的元素，如导航菜单和广告
    """,
    chunk_token_threshold=4096
)
```

2. **专注内容提取**：
```python
filter = LLMContentFilter(
    instruction="""
    专注于提取特定类型的内容：
    - 技术文档
    - 代码示例
    - API 参考
    将内容重新格式化为清晰、结构良好的 markdown
    """,
    chunk_token_threshold=4096
)
```

> **性能提示**：设置较小的 `chunk_token_threshold`（例如 2048 或 4096）以启用内容块的并行处理。默认值为无限，将整个内容作为单个块处理。

---

## 6. 使用 Fit Markdown

当内容过滤器处于活动状态时，库会在 `result.markdown` 中生成两种形式的 markdown：

1. **`raw_markdown`**：完整的未过滤 markdown。  
2. **`fit_markdown`**：一个"fit"版本，其中过滤器已移除或修剪了嘈杂的部分。

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

async def main():
    config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.6),
            options={"ignore_links": True}
        )
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://news.example.com/tech", config=config)
        if result.success:
            print("Raw markdown:\n", result.markdown)
            
            # 如果使用了过滤器，我们还有 .fit_markdown：
            md_object = result.markdown  # 或您的等效对象
            print("Filtered markdown:\n", md_object.fit_markdown)
        else:
            print("Crawl failed:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 7. `MarkdownGenerationResult` 对象

如果您的库将详细的 markdown 输出存储在类似 `MarkdownGenerationResult` 的对象中，您将看到以下字段：

- **`raw_markdown`**：直接的 HTML 到 markdown 转换（无过滤）。  
- **`markdown_with_citations`**：将链接移至参考样式脚注的版本。  
- **`references_markdown`**：包含收集的引用的单独字符串或部分。  
- **`fit_markdown`**：如果您使用了内容过滤器，则为过滤后的 markdown。  
- **`fit_html`**：用于生成 `fit_markdown` 的相应 HTML 片段（有助于调试或高级使用）。

**示例**：

```python
md_obj = result.markdown  # 您的库的命名可能不同
print("RAW:\n", md_obj.raw_markdown)
print("CITED:\n", md_obj.markdown_with_citations)
print("REFERENCES:\n", md_obj.references_markdown)
print("FIT:\n", md_obj.fit_markdown)
```

**为什么这很重要？**  
- 如果您想要整个文本，可以向 LLM 提供 `raw_markdown`。  
- 或者将 `fit_markdown` 输入向量数据库以减少令牌使用。  
- `references_markdown` 可以帮助您跟踪链接来源。

---

以下是"组合过滤器（BM25 + Pruning）"下的**修订部分**，展示了如何在不重新爬取的情况下运行**两次**内容过滤，通过从第一次传递中获取 HTML（或文本）并将其输入到第二个过滤器中。它使用了您为 **BM25ContentFilter** 提供的代码模式，该过滤器直接接受 **HTML** 字符串（并且可以稍作调整以处理纯文本）。

---

## 8. 组合过滤器（BM25 + Pruning）两次传递

您可能希望首先**修剪**嘈杂的样板内容（使用 `PruningContentFilter`），然后**排名**剩余内容与用户查询（使用 `BM25ContentFilter`）。您不必爬取页面两次。而是：

1. **第一次传递**：将 `PruningContentFilter` 直接应用于 `result.html` 中的原始 HTML（爬取器下载的 HTML）。  
2. **第二次传递**：从步骤 1 中获取修剪后的 HTML（或文本），并将其输入到 `BM25ContentFilter` 中，专注于用户查询。

### 两次传递示例

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter
from bs4 import BeautifulSoup

async def main():
    # 1. 使用最小或无 markdown 生成器爬取，仅获取原始 HTML
    config = CrawlerRunConfig(
        # 如果您只需要原始 HTML，可以跳过传递 markdown_generator
        # 或提供一个但在此示例中专注于 .html
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com/tech-article", config=config)

        if not result.success or not result.html:
            print("Crawl failed or no HTML content.")
            return
        
        raw_html = result.html
        
        # 2. 第一次传递：对原始 HTML 应用 PruningContentFilter
        pruning_filter = PruningContentFilter(threshold=0.5, min_word_threshold=50)
        
        # filter_content 返回"文本块"或清理后的 HTML 部分的列表
        pruned_chunks = pruning_filter.filter_content(raw_html)
        # 此列表基本上是修剪后的内容块，可能是 HTML 或文本形式
        
        # 为了演示，让我们将这些块重新组合成一个类似 HTML 的字符串
        # 或者您可以进行进一步处理。这取决于您的管道设计。
        pruned_html = "\n".join(pruned_chunks)
        
        # 3. 第二次传递：使用用户查询的 BM25ContentFilter
        bm25_filter = BM25ContentFilter(
            user_query="machine learning",
            bm25_threshold=1.2,
            language="english"
        )
        
        # 返回文本块列表
        bm25_chunks = bm25_filter.filter_content(pruned_html)  
        
        if not bm25_chunks:
            print("Nothing matched the BM25 query after pruning.")
            return
        
        # 4. 组合或显示最终结果
        final_text = "\n---\n".join(bm25_chunks)
        
        print("==== PRUNED OUTPUT (first pass) ====")
        print(pruned_html[:500], "... (truncated)")  # 预览

        print("\n==== BM25 OUTPUT (second pass) ====")
        print(final_text[:500], "... (truncated)")

if __name__ == "__main__":
    asyncio.run(main())
```

### 发生了什么？

1. **原始 HTML**：我们爬取一次并将原始 HTML 存储在 `result.html` 中。  
2. **PruningContentFilter**：获取 HTML + 可选参数。它提取文本块或部分 HTML，移除被视为"噪音"的标题/部分。它返回**文本块列表**。  
3. **组合或转换**：我们将这些修剪后的块重新组合成一个类似 HTML 的字符串。（或者，您可以将它们存储在列表中以供进一步逻辑使用——适合您的管道。）  
4. **BM25ContentFilter**：我们将修剪后的字符串输入到带有用户查询的 `BM25ContentFilter` 中。第二次传递进一步将内容缩小到与"机器学习"相关的块。

**无需重新爬取**：我们使用了第一次传递中的 `raw_html`，因此无需再次运行 `arun()`——**没有第二次网络请求**。

### 提示与变化

- **纯文本 vs. HTML**：如果您的修剪输出主要是文本，BM25 仍然可以处理；只需记住它需要一个有效的字符串输入。如果您提供部分 HTML（如 `"<p>some text</p>"`），它将解析为 HTML。  
- **在单个管道中链接**：如果您的代码支持，您可以自动链接多个过滤器。否则，手动两次传递过滤（如所示）是直接的。  
- **调整阈值**：如果您在第一步中看到太多或太少的文本，调整 `threshold=0.5` 或 `min_word_threshold=50`。同样，`bm25_threshold=1.2` 可以提高或降低以在第二步中获得更多或更少的块。

### 一次传递组合？

如果您的代码库或管道设计允许在一次传递中应用多个过滤器，您可以这样做。但通常更简单——更透明——是顺序运行它们，分析每个步骤的结果。

**底线**：通过**手动链接**您的过滤逻辑两次传递，您可以对最终内容进行强大的增量控制。首先，使用 Pruning 移除"全局"杂乱，然后使用基于 BM25 的查询相关性进一步优化——而无需进行第二次网络爬取。

---

## 9. 常见陷阱与技巧

1. **没有 Markdown 输出？**  
   - 确保爬取器实际检索到了 HTML。如果网站严重依赖 JS，您可能需要启用动态渲染或等待元素。  
   - 检查您的内容过滤器是否过于激进。降低阈值或禁用过滤器以查看内容是否重新出现。

2. **性能考虑**  
   - 具有多个过滤器的非常大的页面可能会更慢。考虑使用 `cache_mode` 以避免重新下载。  
   - 如果您的最终用例是 LLM 摄入，考虑进一步总结或分块大文本。

3. **利用 `fit_markdown`**  
   - 非常适合 RAG 管道、语义搜索或任何不需要多余样板内容的场景。  
   - 仍然验证文本质量——某些站点在页脚或侧边栏中有关键数据。

4. **调整 `html2text` 选项**  
   - 如果您看到大量原始 HTML 混入文本，请打开 `escape_html`。  
   - 如果代码块看起来混乱，尝试 `mark_code` 或 `handle_code_in_pre`。

---

## 10. 总结与后续步骤

在本**Markdown 生成基础**教程中，您学会了：

- 使用 HTML 到文本选项配置 **DefaultMarkdownGenerator**。  
- 使用 `content_source` 参数选择不同的 HTML 源。  
- 使用 **BM25ContentFilter** 进行特定查询提取或 **PruningContentFilter** 进行一般噪音移除。  
- 区分原始和过滤后的 markdown（`fit_markdown`）。  
- 利用 `MarkdownGenerationResult` 对象处理不同形式的输出（引用、参考等）。

现在，您可以从任何网站生成高质量的 Markdown，专注于您需要的内容——这是为 AI 模型、摘要管道或知识库查询提供支持的关键步骤。

**最后更新**：2025-01-01