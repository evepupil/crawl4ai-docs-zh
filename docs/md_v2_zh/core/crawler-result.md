# 爬取结果与输出

当你对页面调用 `arun()` 时，Crawl4AI 会返回一个 **`CrawlResult`** 对象，其中包含你可能需要的一切——原始 HTML、清理后的版本、可选的截图或 PDF、结构化提取结果等等。本文档解释了这些字段以及它们如何映射到不同的输出类型。

---

## 1. `CrawlResult` 模型

以下是核心模式。每个字段捕获了爬取结果的不同方面：

```python
class MarkdownGenerationResult(BaseModel):
    raw_markdown: str
    markdown_with_citations: str
    references_markdown: str
    fit_markdown: Optional[str] = None
    fit_html: Optional[str] = None

class CrawlResult(BaseModel):
    url: str
    html: str
    fit_html: Optional[str] = None
    success: bool
    cleaned_html: Optional[str] = None
    media: Dict[str, List[Dict]] = {}
    links: Dict[str, List[Dict]] = {}
    downloaded_files: Optional[List[str]] = None
    js_execution_result: Optional[Dict[str, Any]] = None
    screenshot: Optional[str] = None
    pdf: Optional[bytes] = None
    mhtml: Optional[str] = None
    markdown: Optional[Union[str, MarkdownGenerationResult]] = None
    extracted_content: Optional[str] = None
    metadata: Optional[dict] = None
    error_message: Optional[str] = None
    session_id: Optional[str] = None
    response_headers: Optional[dict] = None
    status_code: Optional[int] = None
    ssl_certificate: Optional[SSLCertificate] = None
    dispatch_result: Optional[DispatchResult] = None
    redirected_url: Optional[str] = None
    network_requests: Optional[List[Dict[str, Any]]] = None
    console_messages: Optional[List[Dict[str, Any]]] = None
    tables: List[Dict] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
```

### 表格：`CrawlResult` 中的关键字段

| 字段（名称和类型）                       | 描述                                                                                         |
|-------------------------------------------|-----------------------------------------------------------------------------------------------------|
| **url (`str`)**                           | 最终或实际爬取的 URL（如果发生重定向）。                                             |
| **html (`str`)**                          | 原始、未修改的页面 HTML。适用于调试或自定义处理。                            |
| **fit_html (`Optional[str]`)**            | 经过预处理、针对提取和内容过滤优化的 HTML。                                    |
| **success (`bool`)**                      | 如果爬取完成且没有重大错误，则为 `True`，否则为 `False`。                                   |
| **cleaned_html (`Optional[str]`)**        | 清理后的 HTML，脚本和样式已移除；如果通过 `excluded_tags` 等配置，可以排除标签。 |
| **media (`Dict[str, List[Dict]]`)**       | 提取的媒体信息（图像、音频等），每个都有 `src`、`alt`、`score` 等属性。   |
| **links (`Dict[str, List[Dict]]`)**       | 提取的链接数据，按 `internal` 和 `external` 分开。每个链接通常有 `href`、`text` 等。 |
| **downloaded_files (`Optional[List[str]]`)** | 如果在 `BrowserConfig` 中 `accept_downloads=True`，则列出已保存下载的文件路径。         |
| **js_execution_result (`Optional[Dict[str, Any]]`)** | 爬取期间执行 JavaScript 的结果。 |
| **screenshot (`Optional[str]`)**          | 页面的截图（base64 编码），如果 `screenshot=True`。                                       |
| **pdf (`Optional[bytes]`)**               | 页面的 PDF，如果 `pdf=True`。                                                                      |
| **mhtml (`Optional[str]`)**               | 页面的 MHTML 快照，如果 `capture_mhtml=True`。包含带有所有资源的完整页面。      |
| **markdown (`Optional[str or MarkdownGenerationResult]`)** | 它包含一个 `MarkdownGenerationResult`。随着时间的推移，这将整合到 `markdown` 中。生成器可以提供原始 markdown、引用、参考文献，以及可选的 `fit_markdown`。 |
| **extracted_content (`Optional[str]`)**   | 结构化提取（基于 CSS/LLM）的输出，存储为 JSON 字符串或其他文本。          |
| **metadata (`Optional[dict]`)**           | 关于爬取或提取数据的附加信息。                                                  |
| **error_message (`Optional[str]`)**       | 如果 `success=False`，包含对出错原因的简短描述。                                |
| **session_id (`Optional[str]`)**          | 用于多页面或持久化爬取的会话 ID。                                   |
| **response_headers (`Optional[dict]`)**   | HTTP 响应头，如果已捕获。                                                                 |
| **status_code (`Optional[int]`)**         | HTTP 状态码（例如，200 表示 OK）。                                                                |
| **ssl_certificate (`Optional[SSLCertificate]`)** | SSL 证书信息，如果 `fetch_ssl_certificate=True`。                                               |
| **dispatch_result (`Optional[DispatchResult]`)** | 在并行爬取 URL 时的附加并发和资源使用信息。               |
| **redirected_url (`Optional[str]`)**      | 经过任何重定向后的 URL（与 `url` 不同，后者是最终 URL）。                          |
| **network_requests (`Optional[List[Dict[str, Any]]]`)** | 如果在爬取期间 `capture_network_requests=True`，则捕获的网络请求、响应和失败的列表。 |
| **console_messages (`Optional[List[Dict[str, Any]]]`)** | 如果在爬取期间 `capture_console_messages=True`，则捕获的浏览器控制台消息列表。       |
| **tables (`List[Dict]`)**                 | 从 HTML 表格中提取的表格数据，结构为 `[{headers, rows, caption, summary}]`。           |

---

## 2. HTML 变体

### `html`: 原始 HTML

Crawl4AI 将确切的 HTML 保存为 `result.html`。适用于：

- 调试页面问题或检查原始内容。
- 如果需要，执行您自己的专门解析。

### `cleaned_html`: 清理后的 HTML

如果您在 `CrawlerRunConfig` 中指定了任何清理或排除参数（如 `excluded_tags`、`remove_forms` 等），您将在此处看到结果：

```python
config = CrawlerRunConfig(
    excluded_tags=["form", "header", "footer"],
    keep_data_attributes=False
)
result = await crawler.arun("https://example.com", config=config)
print(result.cleaned_html)  # 清除了表单、页眉、页脚、data-* 属性
```

---

## 3. Markdown 生成

### 3.1 `markdown`

- **`markdown`**: 当前详细 markdown 输出的位置，返回一个 **`MarkdownGenerationResult`** 对象。
- **`markdown_v2`**: 自 v0.5 起已弃用。

**`MarkdownGenerationResult`** 字段：

| 字段                   | 描述                                                                    |
|-------------------------|--------------------------------------------------------------------------------|
| **raw_markdown**        | 基本的 HTML→Markdown 转换。                                            |
| **markdown_with_citations** | 包含内联引用的 Markdown，这些引用在末尾引用了链接。        |
| **references_markdown** | 参考文献/引用本身（如果 `citations=True`）。                      |
| **fit_markdown**        | 如果使用了内容过滤器，则为过滤后的/“fit” markdown。                       |
| **fit_html**            | 生成 `fit_markdown` 的过滤后 HTML。                                |

### 3.2 使用 Markdown 生成器的基本示例

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

config = CrawlerRunConfig(
    markdown_generator=DefaultMarkdownGenerator(
        options={"citations": True, "body_width": 80}  # 例如，传递 html2text 样式选项
    )
)
result = await crawler.arun(url="https://example.com", config=config)

md_res = result.markdown  # 或最终使用 'result.markdown'
print(md_res.raw_markdown[:500])
print(md_res.markdown_with_citations)
print(md_res.references_markdown)
```

**注意**：如果您使用像 `PruningContentFilter` 这样的过滤器，您也会得到 `fit_markdown` 和 `fit_html`。

---

## 4. 结构化提取：`extracted_content`

如果您运行基于 JSON 的提取策略（CSS、XPath、LLM 等），结构化数据**不会**存储在 `markdown` 中——它会作为 JSON 字符串（或有时是纯文本）放在 **`result.extracted_content`** 中。

### 示例：使用 `raw://` HTML 进行 CSS 提取

```python
import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai import JsonCssExtractionStrategy

async def main():
    schema = {
        "name": "Example Items",
        "baseSelector": "div.item",
        "fields": [
            {"name": "title", "selector": "h2", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
        ]
    }
    raw_html = "<div class='item'><h2>Item 1</h2><a href='https://example.com/item1'>Link 1</a></div>"

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="raw://" + raw_html,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=JsonCssExtractionStrategy(schema)
            )
        )
        data =极速赛车开奖结果历史记录
        print(data)

if __name__ == "__main__":
    asyncio.run(main())
```

这里：
- `url="raw://..."` 直接传递 HTML 内容，无需网络请求。
- **CSS** 提取策略用 JSON 数组 `[{"title": "...", "link": "..."}]` 填充 `result.extracted_content`。

---

## 5. 更多字段：链接、媒体、表格等

### 5.1 `links`

一个字典，通常包含 `"internal"` 和 `"external"` 列表。每个条目可能有 `href`、`text`、`title` 等。如果您没有禁用链接提取，则会自动捕获此信息。

```python
print(result.links["internal"][:3])  # 显示前 3 个内部链接
```

### 5.2 `media`

类似地，一个包含 `"images"`、`"audio"`、`"video"` 等的字典。如果您的爬虫设置为收集它们，则每个项目可能包括 `src`、`alt`、`score` 等。

```python
images = result.media.get("images", [])
for img in images:
    print("Image URL:", img["src"], "Alt:", img.get("alt"))
```

### 5.3 `tables`

`tables` 字段包含从爬取页面上找到的 HTML 表格中提取的结构化数据。表格根据各种标准进行分析，以确定它们是否是实际的数据表格（与布局表格相对），包括：

- thead 和 tbody 部分的存在
- 使用 th 元素作为表头
- 列的一致性
- 文本密度
- 以及其他因素

得分高于阈值（默认值：7）的表格会被提取并存储在 result.tables 中。

### 访问表格数据：
```python
import asyncio
极速赛车开奖结果历史记录

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.w3schools.com/html/html_tables.asp",
            config=CrawlerRunConfig(
                table_score_threshold=7  # 表格检测的最低分数
            )
        )

        if result.success and result.tables:
            print(f"Found {len(result.tables)} tables")

            for i, table in enumerate(result.tables):
                print(f"\nTable {i+1}:")
                print(f"Caption: {table.get('caption', 'No caption')}")
                print(f"Headers: {table['headers']}")
                print(f"Rows: {极速赛车开奖结果历史记录)}")

                # 打印前几行作为示例
                for j, row in enumerate(table['rows'][:3]):
                    print(f"  Row {j+1}: {row}")

if __name__ == "__main__":
    asyncio.run(main())

```

### 配置表格提取：

您可以通过以下方式调整表格检测算法的灵敏度：

```python
config = CrawlerRunConfig(
    table_score_threshold=5  # 值越低 = 检测到的表格越多（默认值：7）
)
```

每个提取的表格包含：

- `headers`: 列标题名称
- `rows`: 行列表，每行包含单元格值
- `caption`: 表格标题文本（如果可用）
- `summary`: 表格摘要属性（如果指定）

### 表格提取技巧

- 并非所有 HTML 表格都会被提取 - 只有那些被检测为“数据表格”而非布局表格的表格才会被提取。
- 单元格计数不一致、嵌套表格或纯粹用于布局的表格可能会被跳过。
- 如果您缺少表格，请尝试将 `table_score_threshold` 调整为较低的值（默认值为 7）。

表格检测算法根据一致列、表头存在、文本密度等特征对表格进行评分。得分高于阈值的表格被认为是值得提取的数据表格。


### 5.4 `screenshot`、`pdf` 和 `mhtml`

如果您在 **`CrawlerRunConfig`** 中设置了 `screenshot=True`、`pdf=True` 或 `capture_mhtml=True`，那么：

- `result.screenshot` 包含一个 base64 编码的 PNG 字符串。
- `result.pdf` 包含原始 PDF 字节（您可以将它们写入文件）。
- `result.mhtml` 包含页面的 MHTML 快照作为字符串（您可以将其写入 .mhtml 文件）。

```python
# 保存 PDF
with open("page.pdf", "wb") as f:
    f.write(result.pdf)

# 保存 MHTML
if result.mhtml:
    with open("page.mhtml", "w", encoding="utf-8") as f:
        f.write(result.mhtml)
```

MHTML（MIME HTML）格式特别有用，因为它将整个网页及其所有资源（CSS、图像、脚本等）捕获在一个文件中，非常适合存档或离线查看。

### 5.5 `ssl_certificate`

如果 `fetch_ssl_certificate=True`，`result.ssl_certificate` 包含有关站点 SSL 证书的详细信息，例如颁发者、有效期等。

---

## 6. 访问这些字段

在您运行之后：

```python
result = await crawler.arun(url="https://example.com", config=some_config)
```

检查任何字段：

```python
if result.success:
    print(result.status_code, result.response_headers)
    print("Links found:", len(result.links.get("internal", [])))
    if result.markdown:
        print("Markdown snippet:", result.markdown.raw_markdown[:200])
    if result.extracted_content:
        print("Structured JSON:", result.extracted_content)
else:
    print("Error:", result.error_message)
```

**弃用**：自 v0.5 起，`result.markdown_v2`、`result.fit_html`、`result.fit_markdown` 已弃用。请改用 `result.markdown`！它包含 `MarkdownGenerationResult`，其中包括 `fit_html` 和 `fit_markdown` 作为其属性。


---

## 7. 后续步骤

- **Markdown 生成**：深入了解如何配置 `DefaultMarkdownGenerator` 和各种过滤器。
- **内容过滤**：学习如何使用 `BM25ContentFilter` 和 `PruningContentFilter`。
- **会话和钩子**：如果您想跨多个 `arun()` 调用操作页面或保持状态，请参阅钩子或会话文档。
- **LLM 提取**：对于需要 AI 驱动解析的复杂或非结构化内容，请查看基于 LLM 的策略文档。

**尽情享受**探索 `CrawlResult` 提供的一切——无论您需要原始 HTML、清理后的输出、markdown 还是完全结构化的数据，Crawl4AI 都能满足您的需求！