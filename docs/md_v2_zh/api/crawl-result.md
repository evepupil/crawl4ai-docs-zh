# `CrawlResult` 参考文档

**`CrawlResult`** 类封装了单次爬取操作后返回的所有内容。它提供**原始或处理后的内容**、链接和媒体详情，以及可选元数据（如截图、PDF或提取的JSON）。

**位置**：`crawl4ai/crawler/models.py`（供参考）

```python
class CrawlResult(BaseModel):
    url: str
    html: str
    success: bool
    cleaned_html: Optional[str] = None
    fit_html: Optional[str] = None  # 经过预处理优化用于提取的HTML
    media: Dict[str, List[Dict]] = {}
    links: Dict[str, List[Dict]] = {}
    downloaded_files: Optional[List[str]] = None
    screenshot: Optional[str] = None
    pdf : Optional[bytes] = None
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
    ...
```

以下是**逐字段说明**及可能的使用模式。

---

## 1. 基础爬取信息

### 1.1 **`url`** *(str)*  
**作用**：最终爬取的URL（经过所有重定向后）。  
**用法**：
```python
print(result.url)  # 例如："https://example.com/"
```

### 1.2 **`success`** *(bool)*  
**作用**：如果爬取流程未出现重大错误则为`True`；否则为`False`。  
**用法**：
```python
if not result.success:
    print(f"爬取失败: {result.error_message}")
```

### 1.3 **`status_code`** *(Optional[int])*  
**作用**：页面的HTTP状态码（例如200、404）。  
**用法**：
```python
if result.status_code == 404:
    print("页面未找到！")
```

### 1.4 **`error_message`** *(Optional[str])*  
**作用**：如果`success=False`，此处为失败的文字描述。  
**用法**：
```python
if not result.success:
    print("错误:", result.error_message)
```

### 1.5 **`session_id`** *(Optional[str])*  
**作用**：用于在多次调用间复用浏览器上下文的ID。  
**用法**：
```python
# 如果在CrawlerRunConfig中使用了session_id="login_session"，可在此查看：
print("会话:", result.session_id)
```

### 1.6 **`response_headers`** *(Optional[dict])*  
**作用**：最终的HTTP响应头。  
**用法**：
```python
if result.response_headers:
    print("服务器:", result.response_headers.get("Server", "未知"))
```

### 1.7 **`ssl_certificate`** *(Optional[SSLCertificate])*  
**作用**：如果在CrawlerRunConfig中设置了`fetch_ssl_certificate=True`，**`result.ssl_certificate`**会包含一个描述网站证书的[**`SSLCertificate`**](../advanced/ssl-certificate.md)对象。你可以导出多种格式的证书（PEM/DER/JSON）或访问其属性如`issuer`、`subject`、`valid_from`、`valid_until`等。  
**用法**：
```python
if result.ssl_certificate:
    print("颁发者:", result.ssl_certificate.issuer)
```

---

## 2. 原始/清理后的内容

### 2.1 **`html`** *(str)*  
**作用**：最终页面加载的**原始**未修改HTML。  
**用法**：
```python
# 可能很大
print(len(result.html))
```

### 2.2 **`cleaned_html`** *(Optional[str])*  
**作用**：经过清理的HTML版本——根据`CrawlerRunConfig`配置移除了脚本、样式或排除的标签。  
**用法**：
```python
print(result.cleaned_html[:500])  # 显示片段
```

---

## 3. Markdown字段

### 3.1 Markdown生成方法

Crawl4AI可以将HTML转换为Markdown，可选包含：

- **原始**Markdown  
- **链接作为引用**（带有参考文献部分）  
- 如果使用了**内容过滤器**（如Pruning或BM25），则生成**Fit** Markdown


**`MarkdownGenerationResult`**包含：
- **`raw_markdown`** *(str)*：完整的HTML→Markdown转换结果。  
- **`markdown_with_citations`** *(str)*：相同的Markdown，但链接引用以学术风格引用形式呈现。  
- **`references_markdown`** *(str)*：末尾的参考文献列表或脚注。  
- **`fit_markdown`** *(Optional[str])*：如果应用了内容过滤（Pruning/BM25），则为过滤后的"fit"文本。  
- **`fit_html`** *(Optional[str])*：生成`fit_markdown`的HTML。

**用法**：
```python
if result.markdown:
    md_res = result.markdown
    print("原始MD:", md_res.raw_markdown[:300])
    print("引用MD:", md_res.markdown_with_citations[:300])
    print("参考文献:", md_res.references_markdown)
    if md_res.fit_markdown:
        print("修剪后的文本:", md_res.fit_markdown[:300])
```

### 3.2 **`markdown`** *(Optional[Union[str, MarkdownGenerationResult]])*  
**作用**：保存`MarkdownGenerationResult`。  
**用法**：
```python
print(result.markdown.raw_markdown[:200])
print(result.markdown.fit_markdown)
print(result.markdown.fit_html)
```
**重要**："Fit"内容（位于`fit_markdown`/`fit_html`）仅在`MarkdownGenerationStrategy`中使用了**过滤器**（如**PruningContentFilter**或**BM25ContentFilter**）时存在于result.markdown中。

---

## 4. 媒体与链接

### 4.1 **`media`** *(Dict[str, List[Dict]])*  
**作用**：包含发现的图片、视频或音频信息。通常键为`"images"`、`"videos"`、`"audios"`。  
**每个项目的常见字段**：

- `src` *(str)*：媒体URL  
- `alt`或`title` *(str)*：描述性文本  
- `score` *(float)*：如果爬虫启发式算法认为其"重要"时的相关性分数  
- `desc`或`description` *(Optional[str])*：从周围文本提取的额外上下文  

**用法**：
```python
images = result.media.get("images", [])
for img in images:
    if img.get("score", 0) > 5:
        print("高价值图片:", img["src"])
```

### 4.2 **`links`** *(Dict[str, List[Dict]])*  
**作用**：保存内部和外部链接数据。通常有两个键：`"internal"`和`"external"`。  
**常见字段**：

- `href` *(str)*：链接目标  
- `text` *(str)*：链接文本  
- `title` *(str)*：标题属性  
- `context` *(str)*：周围文本片段  
- `domain` *(str)*：如果是外部链接，则为域名

**用法**：
```python
for link in result.links["internal"]:
    print(f"内部链接 {link['href']} 的文本为 {link['text']}")
```

---

## 5. 额外字段

### 5.1 **`extracted_content`** *(Optional[str])*  
**作用**：如果使用了**`extraction_strategy`**（CSS、LLM等），则为结构化输出（JSON）。  
**用法**：
```python
if result.extracted_content:
    data = json.loads(result.extracted_content)
    print(data)
```

### 5.2 **`downloaded_files`** *(Optional[List[str]])*  
**作用**：如果在`BrowserConfig`中设置了`accept_downloads=True` + `downloads_path`，则列出下载项的本地文件路径。  
**用法**：
```python
if result.downloaded_files:
    for file_path in result.downloaded_files:
        print("已下载:", file_path)
```

### 5.3 **`screenshot`** *(Optional[str])*  
**作用**：如果在`CrawlerRunConfig`中设置了`screenshot=True`，则为Base64编码的截图。  
**用法**：
```python
import base64
if result.screenshot:
    with open("page.png", "wb") as f:
        f.write(base64.b64decode(result.screenshot))
```

### 5.4 **`pdf`** *(Optional[bytes])*  
**作用**：如果在`CrawlerRunConfig`中设置了`pdf=True`，则为原始PDF字节。  
**用法**：
```python
if result.pdf:
    with open("page.pdf", "wb") as f:
        f.write(result.pdf)
```

### 5.5 **`mhtml`** *(Optional[str])*  
**作用**：如果在`CrawlerRunConfig`中设置了`capture_mhtml=True`，则为页面的MHTML快照。MHTML（MIME HTML）格式将整个网页及其所有资源（CSS、图片、脚本等）保存在单一文件中。  
**用法**：
```python
if result.mhtml:
    with open("page.mhtml", "w", encoding="utf-8") as f:
        f.write(result.mhtml)
```

### 5.6 **`metadata`** *(Optional[dict])*  
**作用**：如果发现页面级元数据（标题、描述、OG数据等）。  
**用法**：
```python
if result.metadata:
    print("标题:", result.metadata.get("title"))
    print("作者:", result.metadata.get("author"))
```

---

## 6. `dispatch_result`（可选）

当并行爬取URL时（例如通过`arun_many()`与自定义分发器），`DispatchResult`对象提供额外的并发和资源使用信息。它包含：

- **`task_id`**：并行任务的唯一标识符。
- **`memory_usage`** (float)：完成时使用的内存（MB）。
- **`peak_memory`** (float)：任务执行期间记录的内存峰值（MB）。
- **`start_time`** / **`end_time`** (datetime)：此爬取任务的时间范围。
- **`error_message`** (str)：遇到的任何分发器或并发相关错误。

```python
# 示例用法：
for result in results:
    if result.success and result.dispatch_result:
        dr = result.dispatch_result
        print(f"URL: {result.url}, 任务ID: {dr.task_id}")
        print(f"内存: {dr.memory_usage:.1f} MB (峰值: {dr.peak_memory:.1f} MB)")
        print(f"持续时间: {dr.end_time - dr.start_time}")
```

> **注意**：此字段通常在搭配**分发器**（如`MemoryAdaptiveDispatcher`或`SemaphoreDispatcher`）使用`arun_many(...)`时填充。如果未使用并发或分发器，`dispatch_result`可能保持为`None`。

---

## 7. 网络请求与控制台消息

当在`CrawlerRunConfig`中通过`capture_network_requests=True`和`capture_console_messages=True`启用网络和控制台消息捕获时，`CrawlResult`将包含以下字段：

### 7.1 **`network_requests`** *(Optional[List[Dict[str, Any]]])*
**作用**：包含爬取期间捕获的所有网络请求、响应和失败信息的字典列表。
**结构**：
- 每个项都有一个`event_type`字段，可以是`"request"`、`"response"`或`"request_failed"`。
- 请求事件包括`url`、`method`、`headers`、`post_data`、`resource_type`和`is_navigation_request`。
- 响应事件包括`url`、`status`、`status_text`、`headers`和`request_timing`。
- 失败请求事件包括`url`、`method`、`resource_type`和`failure_text`。
- 所有事件都包含一个`timestamp`字段。

**用法**：
```python
if result.network_requests:
    # 统计不同类型的事件
    requests = [r for r in result.network_requests if r.get("event_type") == "request"]
    responses = [r for r in result.network_requests if r.get("event_type") == "response"]
    failures = [r for r in result.network_requests if r.get("event_type") == "request_failed"]
    
    print(f"捕获了 {len(requests)} 个请求, {len(responses)} 个响应, 和 {len(failures)} 个失败")
    
    # 分析API调用
    api_calls = [r for r in requests if "api" in r.get("url", "")]
    
    # 识别失败的资源
    for failure in failures:
        print(f"加载失败: {failure.get('url')} - {failure.get('failure_text')}")
```

### 7.2 **`console_messages`** *(Optional[List[Dict[str, Any]]])*
**作用**：包含爬取期间捕获的所有浏览器控制台消息的字典列表。
**结构**：
- 每个项都有一个`type`字段，指示消息类型（如`"log"`、`"error"`、`"warning"`等）。
- `text`字段包含实际的消息文本。
- 某些消息包括`location`信息（URL、行、列）。
- 所有消息都包含一个`timestamp`字段。

**用法**：
```python
if result.console_messages:
    # 按类型统计消息
    message_types = {}
    for msg in result.console_messages:
        msg_type = msg.get("type", "unknown")
        message_types[msg_type] = message_types.get(msg_type, 0) + 1
    
    print(f"消息类型统计: {message_types}")
    
    # 显示错误（通常最重要）
    for msg in result.console_messages:
        if msg.get("type") == "error":
            print(f"错误: {msg.get('text')}")
```

这些字段提供了对页面网络活动和浏览器控制台的深度可见性，对于调试、安全分析和理解复杂Web应用程序非常宝贵。

有关网络和控制台捕获的更多详情，请参阅[网络与控制台捕获文档](../advanced/network-console-capture.md)。

---

## 8. 示例：访问所有内容

```python
async def handle_result(result: CrawlResult):
    if not result.success:
        print("爬取错误:", result.error_message)
        return
    
    # 基础信息
    print("爬取的URL:", result.url)
    print("状态码:", result.status_code)
    
    # HTML
    print("原始HTML大小:", len(result.html))
    print("清理后的HTML大小:", len(result.cleaned_html or ""))
    
    # Markdown输出
    if result.markdown:
        print("原始Markdown:", result.markdown.raw_markdown[:300])
        print("引用Markdown:", result.markdown.markdown_with_citations[:300])
        if result.markdown.fit_markdown:
            print("Fit Markdown:", result.markdown.fit_markdown[:200])

    # 媒体与链接
    if "images" in result.media:
        print("图片数量:", len(result.media["images"]))
    if "internal" in result.links:
        print("内部链接数量:", len(result.links["internal"]))

    # 提取策略结果
    if result.extracted_content:
        print("结构化数据:", result.extracted_content)
    
    # 截图/PDF/MHTML
    if result.screenshot:
        print("截图长度:", len(result.screenshot))
    if result.pdf:
        print("PDF字节长度:", len(result.pdf))
    if result.mhtml:
        print("MHTML长度:", len(result.mhtml))
        
    # 网络和控制台捕获
    if result.network_requests:
        print(f"捕获的网络请求: {len(result.network_requests)}")
        # 分析请求类型
        req_types = {}
        for req in result.network_requests:
            if "resource_type" in req:
                req_types[req["resource_type"]] = req_types.get(req["resource_type"], 0) + 1
        print(f"资源类型: {req_types}")
        
    if result.console_messages:
        print(f"捕获的控制台消息: {len(result.console_messages)}")
        # 按消息类型统计
        msg_types = {}
        for msg in result.console_messages:
            msg_types[msg.get("type", "unknown")] = msg_types.get(msg.get("type", "unknown"), 0) + 1
        print(f"消息类型: {msg_types}")
```

---

## 9. 关键点与未来

1. **CrawlResult的废弃旧属性**  
   - `markdown_v2` - 在v0.5中废弃。只需使用`markdown`。它现在保存`MarkdownGenerationResult`！
   - `fit_markdown`和`fit_html` - 在v0.5中废弃。现在可以通过`result.markdown`中的`MarkdownGenerationResult`访问。例如：`result.markdown.fit_markdown`和`result.markdown.fit_html`

2. **Fit内容**  
   - **`fit_markdown`**和**`fit_html`**仅在**MarkdownGenerationStrategy**中使用了内容过滤器（如**PruningContentFilter**或**BM25ContentFilter**）或直接设置它们时出现在MarkdownGenerationResult中。  
   - 如果未使用过滤器，它们保持为`None`。

3. **参考文献与引用**  
   - 如果在`DefaultMarkdownGenerator`中启用链接引用（`options={"citations": True}`），你将看到`markdown_with_citations`加上一个**`references_markdown`**块。这有助于大型语言模型或学术风格的引用。

4. **链接与媒体**  
   - `links["internal"]`和`links["external"]`按域名分组发现的锚点。  
   - `media["images"]` / `["videos"]` / `["audios"]`存储提取的媒体元素及可选的评分或上下文。

5. **错误情况**  
   - 如果`success=False`，检查`error_message`（例如超时、无效URL）。  
   - 如果我们在HTTP响应前失败，`status_code`可能为`None`。

使用**`CrawlResult`**获取所有最终输出，并将其输入到你的数据管道、AI模型或存档中。通过正确配置的**BrowserConfig**和**CrawlerRunConfig**的协同作用，爬虫可以在**`CrawlResult`**中生成健壮、结构化的结果。