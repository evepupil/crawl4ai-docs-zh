# LLM上下文协议：为什么你的AI助手需要记忆、推理和示例

*发布于 2025 年 1 月 24 日 • 阅读时间 8 分钟*

---

## 教机器人编程的问题

想象一下：你递给某人一本字典，然后让他们写诗。他们认识每个单词，知道拼写和定义——但他们知道词语如何共舞吗？知道某些组合能唤起情感而另一些却平淡无奇吗？这正是当我们把API文档扔给AI助手并期待奇迹时所做的事情。

我花了无数个小时看着我的AI编程助手在我自己的库 Crawl4AI 上挣扎。尽管提供了全面的文档，它生成的代码在*技术*上是正确的，但实际上毫无用处。就像一个拿着短语手册说话的游客——语法正确，文化上却格格不入。

## 引入三维上下文协议

如果我们不是简单地倾倒信息，而是提供*智慧*呢？不仅仅是“是什么”，还有“如何”和“为什么”？这让我开发了所谓的**LLM上下文协议**——一种结构化方法，反映了人类真正掌握库的方式。

可以把它看作是AI上下文的HTTP。就像HTTP不规定你的网站内容，但为通信提供了可靠的结构一样，该协议不规定*如何*编写文档——它提供了一个框架，说明你的AI需要什么才能真正理解你的代码。

### 库智慧的三大支柱

<div style="background-color: #1a1a1c; border: 1px solid #3f3f44; padding: 20px; margin: 20px 0;">

#### 🧠 **记忆：基础**
```markdown
# AsyncWebCrawler.arun() - Memory Context

## Signature
async def arun(
    url: str,
    config: CrawlerConfig = None,
    session_id: str = None,
    **kwargs
) -> CrawlResult

## Parameters
- url: Target URL to crawl
- config: Optional configuration object
- session_id: Optional session identifier for caching
...
```

这是你的API参考——事实、参数、返回类型。这是最容易生成的部分，但讽刺的是，孤立来看也是最没用的。就像记住了字典却不理解语法。

</div>

<div style="background-color: #1a1a1c; border: 1px solid #3f3f44; padding: 20px; margin: 20px 0;">

#### 🎯 **推理：灵魂**
```markdown
# AsyncWebCrawler Design Philosophy - Reasoning Context

## Why Async-First Architecture?

Crawl4AI uses AsyncWebCrawler as its primary interface because modern web 
scraping demands concurrency. Here's the thinking:

1. **Network I/O is slow**: Waiting synchronously wastes 90% of execution time
2. **Modern sites are complex**: Multiple resources load in parallel
3. **Scale matters**: You're rarely crawling just one page

## When to Use Session Management

Session management isn't just about performance—it's about appearing human:
- Use sessions when crawling multiple pages from the same domain
- Reuse browser contexts to maintain cookies and local storage
- But don't overdo it: too long sessions look suspicious

## The Cache Strategy Decision Tree
if static_content and infrequent_updates:
    use_cache_mode('read_write')
elif dynamic_content and real_time_needed:
    use_cache_mode('bypass')
else:
    use_cache_mode('read_only')  # Safe default
```

这是库创建者哲学所在的地方。它不仅仅是库*做什么*，而是*为什么*要这样做。这是最难写的部分，因为它需要真正的理解——当一个库缺少它时，这是一个危险信号。

</div>

<div style="background-color: #1a1a1c; border: 1px solid #3f3f44; padding: 20px; margin: 20px 0;">

#### 💻 **示例：实践**
```python
# Crawling with JavaScript execution
result = await crawler.arun(
    url="https://example.com",
    js_code="window.scrollTo(0, document.body.scrollHeight);",
    wait_for="css:.lazy-loaded-content"
)

# Extracting structured data with CSS selectors
result = await crawler.arun(
    url="https://shop.example.com",
    extraction_strategy=CSSExtractionStrategy({
        "prices": "span.price::text",
        "titles": "h2.product-title::text"
    })
)

# Session-based crawling with custom headers
async with crawler:
    result1 = await crawler.arun(url1, session_id="product_scan")
    result2 = await crawler.arun(url2, session_id="product_scan")
```

纯代码。没有废话。只有实践中的模式。因为有时候，你只需要看看它是怎么做的。

</div>

## 为什么这很重要（尤其是对于较小的LLM）

关于AI助手有一点：较小的模型根本无法思考。它们就像热心的实习生——充满潜力但需要清晰的指导。当你依赖大型语言模型从原始API文档中“弄清楚”时，你是在要求它从头开始重新发明你的库的哲学。每。一。次。

通过在这三个维度上提供结构化上下文，我们不仅仅是在记录——我们是在教学。我们传递的不仅仅是知识，还有智慧。

## 你的库的文化DNA

<div style="display: flex; align-items: center; background-color: #3f3f44; padding: 20px; margin: 20px 0; border-left: 4px solid #09b5a5;">
<div style="font-size: 48px; margin-right: 20px;">🧬</div>
<div>
<strong>你的库的推理就是它的文化DNA。</strong><br>
它反映了你的品味、你的架构决策、你关于事情应该如何完成的观点。一个没有推理的库就像一个没有技巧的食谱——当然，你有食材，但祝你好运做出能吃的东西。
</div>
</div>

想想看：当你学习一个新库时，你真正追求的是什么？你想要精通。而精通来自于理解：
- **记忆**告诉你什么是可能的
- **推理**告诉你什么是明智的
- **示例**向你展示什么是实用的

它们共同创造了智慧。

## 超越手动文档

现在，有趣的部分来了。我没有为 Crawl4AI 手工编写数千行结构化文档。谁有那么多时间？相反，我构建了一个工具，可以：

1. 分析你的代码库
2. 提取API签名和结构（记忆）
3. 识别模式和架构决策（推理）
4. 从测试和示例中收集实际用法（示例）
5. 生成结构化的LLM上下文文件

美妙之处在于？这个工具正在成为 Crawl4AI 本身的一部分。因为如果我们要彻底改变AI理解我们代码的方式，我们不妨自动化它。

## 协议，而非规定

记住：这是一个协议，而不是规定。就像HTTP不告诉你建什么网站一样，LLM上下文协议也不规定你的文档风格。它只是说：

> “如果你想让AI真正理解你的库，它需要三样东西：事实、哲学和模式。”

你如何交付这些取决于你。该协议只是确保在翻译过程中不会丢失任何重要内容。

## 亲自尝试

有兴趣为你自己的库实现这个吗？上下文生成工具将作为 Crawl4AI 的一部分开源。如果你对早期访问感兴趣或想讨论这种方法，请在 X [@unclecode](https://twitter.com/unclecode) 上给我发私信。

因为让我们面对现实：如果我们要生活在一个AI编写我们一半代码的世界里，我们不妨好好教它。

---

## 最后的思考

<div style="text-align: center; padding: 40px; background-color: #1a1a1c; border: 1px dashed #3f3f44; margin: 30px 0;">
<div style="font-size: 24px; color: #09b5a5; margin-bottom: 10px;">
记忆 + 推理 + 示例 = 智慧
</div>
<div style="color: #a3abba;">
而智慧，而非信息，才是造就伟大开发者的关键——无论是人类还是人工智能。
</div>
</div>

---

*想看看实际效果吗？查看 [Crawl4AI LLM Context Builder](/core/llmtxt/)，体验结构化上下文带来的不同。*

<style>
/* Custom styles for this article */
.markdown-body pre {
    background-color: #1e1e1e !important;
    border: 1px solid #3f3f44;
}

.markdown-body code {
    background-color: #3f3f44;
    color: #50ffff;
    padding: 2px 6px;
    border-radius: 3px;
}

.markdown-body pre code {
    background-color: transparent;
    color: #e8e9ed;
    padding: 0;
}

.markdown-body blockquote {
    border-left: 4px solid #09b5a5;
    background-color: #1a1a1c;
    padding: 15px 20px;
    margin: 20px 0;
}

.markdown-body h2 {
    color: #50ffff;
    border-bottom: 1px dashed #3f3f44;
    padding-bottom: 10px;
}

.markdown-body h3 {
    color: #09b5a5;
}

.markdown-body strong {
    color: #50ffff;
}
</style>