# 提取 JSON（LLM）

在某些情况下，你需要从网页中提取**复杂或非结构化**的信息，而这些信息难以通过简单的 CSS/XPath 模式解析。或者你需要**AI**驱动的洞察、分类或摘要。针对这些场景，Crawl4AI 提供了一种**基于 LLM 的提取策略**，该策略：

1. 支持 [LiteLLM](https://github.com/BerriAI/litellm) 支持的任何大型语言模型（Ollama、OpenAI、Claude 等）。  
2. 根据需要自动将内容分块以处理令牌限制，然后合并结果。  
3. 允许你定义一个**模式**（如 Pydantic 模型）或更简单的“块”提取方法。

**重要提示**：基于 LLM 的提取可能比基于模式的方法更慢且成本更高。如果你的页面数据高度结构化，请首先考虑使用 [`JsonCssExtractionStrategy`](./no-llm-strategies.md) 或 [`JsonXPathExtractionStrategy`](./no-llm-strategies.md)。但如果你需要 AI 来解释或重组内容，请继续阅读！

---

## 1. 为什么使用 LLM？

- **复杂推理**：如果网站的数据是非结构化的、分散的或充满自然语言上下文。  
- **语义提取**：需要理解能力的摘要、知识图谱或关系数据。  
- **灵活**：你可以向模型传递指令以执行更高级的转换或分类。

---

## 2. 通过 LiteLLM 实现提供商无关性

你可以使用 LlmConfig 快速配置多种 LLM 变体并进行实验，以找到最适合你用例的模型。你可以在[此处](/api/parameters)阅读更多关于 LlmConfig 的信息。

```python
llmConfig = LlmConfig(provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY"))
```

Crawl4AI 使用“提供商字符串”（例如 `"openai/gpt-4o"`、`"ollama/llama2.0"`、`"aws/titan"`）来标识你的 LLM。LiteLLM 支持的任何模型都可以使用。你只需提供：

- **`provider`**：`<provider>/<model_name>` 标识符（例如 `"openai/gpt-4"`、`"ollama/llama2"`、`"huggingface/google-flan"` 等）。  
- **`api_token`**：如果需要（对于 OpenAI、HuggingFace 等）；本地模型或 Ollama 可能不需要。  
- **`base_url`**（可选）：如果你的提供商有自定义端点。  

这意味着你不会被锁定在单一的 LLM 供应商中。可以轻松切换或实验。

---

## 3. LLM 提取的工作原理

### 3.1 流程

1. **分块**（可选）：如果 HTML 或 markdown 内容非常长，则将其分割成较小的片段（基于 `chunk_token_threshold`、重叠等）。  
2. **提示构建**：对于每个块，库会形成一个提示，其中包括你的**`instruction`**（以及可能的模式或示例）。  
3. **LLM 推理**：每个块被并行或顺序发送到模型（取决于你的并发设置）。  
4. **合并**：每个块的结果被合并并解析为 JSON。

### 3.2 `extraction_type`

- **`"schema"`**：模型尝试返回符合你的基于 Pydantic 模式的 JSON。  
- **`"block"`**：模型返回自由格式的文本或较小的 JSON 结构，由库收集。  

对于结构化数据，推荐使用 `"schema"`。你提供 `schema=YourPydanticModel.model_json_schema()`。

---

## 4. 关键参数

以下是重要的 LLM 提取参数概述。所有参数通常在 `LLMExtractionStrategy(...)` 中设置。然后你将此策略放入 `CrawlerRunConfig(..., extraction_strategy=...)` 中。

1. **`llmConfig`** (LlmConfig)：例如 `"openai/gpt-4"`、`"ollama/llama2"`。    
2. **`schema`** (dict)：描述你所需字段的 JSON 模式。通常由 `YourModel.model_json_schema()` 生成。  
3. **`extraction_type`** (str)：`"schema"` 或 `"block"`。  
4. **`instruction`** (str)：提示文本，告诉 LLM 你想要提取什么。例如，“将这些字段提取为 JSON 数组。”  
5. **`chunk_token_threshold`** (int)：每个块的最大令牌数。如果你的内容很大，可以将其拆分以供 LLM 处理。  
6. **`overlap_rate`** (float)：相邻块之间的重叠率。例如，`0.1` 表示每个块有 10% 的文本重复，以保持上下文连续性。  
7. **`apply_chunking`** (bool)：设置为 `True` 以自动分块。如果希望单次处理，设置为 `False`。  
8. **`input_format`** (str)：确定将**哪个**爬取结果传递给 LLM。选项包括：  
   - `"markdown"`：原始 markdown（默认）。  
   - `"fit_markdown"`：如果你使用了内容过滤器，则为过滤后的“fit”markdown。  
   - `"html"`：清理过的或原始的 HTML。  
9. **`extra_args`** (dict)：额外的 LLM 参数，如 `temperature`、`max_tokens`、`top_p` 等。  
10. **`show_usage()`**：你可以调用的方法，用于打印使用信息（每个块的令牌使用情况，总成本（如果已知））。  

**示例**：

```python
extraction_strategy = LLMExtractionStrategy(
    llm_config = LLMConfig(provider="openai/gpt-4", api_token="YOUR_OPENAI_KEY"),
    schema=MyModel.model_json_schema(),
    extraction_type="schema",
    instruction="Extract a list of items from the text with 'name' and 'price' fields.",
    chunk_token_threshold=1200,
    overlap_rate=0.1,
    apply_chunking=True,
    input_format="html",
    extra_args={"temperature": 0.1, "max_tokens": 1000},
    verbose=True
)
```

---

## 5. 将其放入 `CrawlerRunConfig`

**重要提示**：在 Crawl4AI 中，所有策略定义都应放在 `CrawlerRunConfig` 中，而不是直接作为 `arun()` 的参数。以下是一个完整示例：

```python
import os
import asyncio
import json
from pydantic import BaseModel, Field
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai import LLMExtractionStrategy

class Product(BaseModel):
    name: str
    price: str

async def main():
    # 1. Define the LLM extraction strategy
    llm_strategy = LLMExtractionStrategy(
        llm_config = LLMConfig(provider="openai/gpt-4o-mini", api_token=os.getenv('OPENAI_API_KEY')),
        schema=Product.schema_json(), # Or use model_json_schema()
        extraction_type="schema",
        instruction="Extract all product objects with 'name' and 'price' from the content.",
        chunk_token_threshold=1000,
        overlap_rate=0.0,
        apply_chunking=True,
        input_format="markdown",   # or "html", "fit_markdown"
        extra_args={"temperature": 0.0, "max_tokens": 800}
    )

    # 2. Build the crawler config
    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        cache_mode=CacheMode.BYPASS
    )

    # 3. Create a browser config if needed
    browser_cfg = BrowserConfig(headless=True)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # 4. Let's say we want to crawl a single page
        result = await crawler.arun(
            url="https://example.com/products",
            config=crawl_config
        )

        if result.success:
            # 5. The extracted content is presumably JSON
            data = json.loads(result.extracted_content)
            print("Extracted items:", data)
            
            # 极狐. Show usage stats
            llm_strategy.show_usage()  # prints token usage
        else:
            print("Error:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 6. 分块详情

### 6.1 `chunk_token_threshold`

如果你的页面很大，可能会超出 LLM 的上下文窗口。**`chunk_token_threshold`** 设置了每个块的近似最大令牌数。库使用 `word_token_rate`（通常默认为 ~0.75）计算单词→令牌比率。如果启用了分块（`apply_chunking=True`），文本将被分割成片段。

### 6.2 `overlap_rate`

为了保持块之间的上下文连续性，我们可以让它们重叠。例如，`overlap_rate=0.1` 表示每个后续块包含前一个块文本的 10%。如果你需要的信息可能跨越块边界，这会很有帮助。

### 6.3 性能与并行性

通过分块，你可以根据并发设置和 LLM 提供商，并行处理多个块。如果网站很大或有很多部分，这可以减少总时间。

---

## 7. 输入格式

默认情况下，**LLMExtractionStrategy** 使用 `input_format="markdown"`，这意味着将**爬取器的最终 markdown** 输入给 LLM。你可以更改为：

- **`html`**：清理过的 HTML 或原始 HTML（取决于你的爬取器配置）进入 LLM。  
- **`fit_markdown`**：如果你使用了例如 `PruningContentFilter`，则使用 markdown 的“fit”版本。如果你信任过滤器，这可以大幅减少令牌数。  
- **`markdown`**：来自爬取器 `markdown_generator` 的标准 markdown 输出。

此设置至关重要：如果 LLM 指令依赖于 HTML 标签，选择 `"html"`。如果你更喜欢基于文本的方法，选择 `"markdown"`。

```python
LLMExtractionStrategy(
    # ...
    input_format="html",  # Instead of "markdown" or "fit_markdown"
)
```

---

## 8. 令牌使用情况与显示使用情况

为了跟踪令牌和成本，每个块都通过 LLM 调用进行处理。我们在以下位置记录使用情况：

- **`usages`** (list)：每个块或调用的令牌使用情况。  
- **`total_usage`**：所有块调用的总和。  
- **`show_usage()`**：打印使用报告（如果提供商返回使用数据）。

```python
llm_strategy = LLMExtractionStrategy(...)
# ...
llm_strategy.show_usage()
# e.g. “Total usage: 1241 tokens across 2 chunk calls”
```

如果你的模型提供商不返回使用信息，这些字段可能部分为空。

---

## 9. 示例：构建知识图谱

以下是一个结合 **`LLMExtractionStrategy`** 和用于知识图谱的 Pydantic 模式的代码片段。注意我们如何传递**`instruction`** 来告诉模型要解析什么。

```python
import os
import json
import asyncio
from typing import List
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai import LLMExtractionStrategy

class Entity(BaseModel):
    name: str
    description: str

class Relationship(BaseModel):
    entity1: Entity
    entity2: Entity
    description: str
    relation_type: str

class KnowledgeGraph(BaseModel):
    entities: List[Entity]
    relationships: List[Relationship]

async def main():
    # LLM extraction strategy
    llm_strat = LLMExtractionStrategy(
        llmConfig = LLMConfig(provider="openai/gpt-4", api_token=os.getenv('OPENAI_API_KEY')),
        schema=KnowledgeGraph.model_json_schema(),
        extraction_type="schema",
        instruction="Extract entities and relationships from the content. Return valid JSON.",
        chunk_token_threshold=极狐00,
        apply极狐unking=True,
        input_format="html",
        extra_args={"temperature": 0.1, "max_tokens": 1500}
    )

    crawl_config = Crawler极狐nConfig(
        extraction_strategy=llm_strat,
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
        # Example page
        url = "https://www.nbcnews.com/business"
        result = await crawler.arun(url=url, config=crawl_config)

        print("--- LLM RAW RESPONSE ---")
        print(result.extracted_content)
        print("--- END LLM RAW RESPONSE ---")

        if result.success:
            with open("kb_result.json", "w", encoding="utf-8") as f:
                f.write(result.extracted_content)
            llm_strat.show_usage()
        else:
            print("Crawl failed:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
```

**关键观察**：

- **`extraction_type="schema"`** 确保我们获得符合 `KnowledgeGraph` 的 JSON。  
- **`input_format="html"`** 意味着我们将 HTML 提供给模型。  
- **`instruction`** 指导模型输出结构化的知识图谱。  

---

## 10. 最佳实践与注意事项

1. **成本与延迟**：LLM 调用可能缓慢或昂贵。如果你只需要部分数据，请考虑分块或减少覆盖范围。  
2. **模型令牌限制**：如果你的页面 + 指令超出上下文窗口，分块是必不可少的。  
3. **指令工程**：精心设计的指令可以显著提高输出可靠性。  
4. **模式严格性**：`"schema"` 提取尝试将模型输出解析为 JSON。如果模型返回无效 JSON，可能会发生部分提取，或者你可能会收到错误。  
5. **并行与串行**：库可以并行处理多个块，但你必须注意某些提供商的速率限制。  
6. **检查输出**：有时，LLM 可能会省略字段或产生多余文本。你可能希望使用 Pydantic 进行后验证或进行额外的清理。

---

## 11. 结论

Crawl4AI 中的**基于 LLM 的提取**是**提供商无关的**，允许你通过 LiteLLM 从数百个模型中选择。它非常适合**语义复杂**的任务或生成高级结构（如知识图谱）。然而，它比基于模式的方法**更慢**且可能成本更高。请记住以下提示：

- 将你的 LLM 策略放在 **`CrawlerRunConfig`** 中。  
- 使用 **`input_format`** 选择 LLM 看到的形式（markdown、HTML、fit_markdown）。  
- 调整 **`chunk_token_threshold`**、**`overlap_rate`** 和 **`apply_chunking`** 以高效处理大内容。  
- 使用 `show_usage()` 监控令牌使用情况。

如果你网站的数据一致或重复，首先考虑 [`JsonCssExtractionStrategy`](./no-llm-strategies.md) 以获得速度和简单性。但如果你需要**AI 驱动**的方法，`LLMExtractionStrategy` 提供了一个灵活的多提供商解决方案，用于从任何网站提取结构化 JSON。

**后续步骤**：

1. **尝试不同的提供商**  
   - 尝试切换 `provider`（例如 `"ollama/llama2"`、`"openai/gpt-4o"` 等）以查看速度、准确性或成本方面的差异。  
   - 传递不同的 `extra_args`，如 `temperature`、`top_p` 和 `max_tokens` 以微调结果。

2. **性能调优**  
   - 如果页面很大，调整 `chunk_token_threshold`、`overlap_rate` 或 `apply_chunking` 以优化吞吐量。  
   - 使用 `show_usage()` 检查使用日志，以关注令牌消耗并识别潜在瓶颈。

3. **验证输出**  
   - 如果使用 `extraction_type="schema"`，使用 Pydantic 模型解析 LLM 的 JSON 进行最终验证步骤。  
   - 优雅地记录或处理任何解析错误，尤其是当模型偶尔返回格式错误的 JSON 时。

4. **探索钩子与自动化**  
   - 将 LLM 提取与[钩子](../advanced/hooks-auth.md)集成以进行复杂的前/后处理。  
   - 使用多步骤管道：爬取、过滤、LLM 提取，然后存储或索引结果以进行进一步分析。

**最后更新**：2025-01-01

---

这就是**提取 JSON（LLM）**的全部内容——现在你可以利用 AI 来解析、分类或重组网络数据。祝你爬取愉快！