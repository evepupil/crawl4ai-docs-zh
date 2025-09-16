# Crawl4AI CLI 指南

## 目录
- [安装](#installation)
- [基本用法](#basic-usage)
- [配置](#configuration)
  - [浏览器配置](#browser-configuration)
  - [爬虫配置](#crawler-configuration)
  - [提取配置](#extraction-configuration)
  - [内容过滤](#content-filtering)
- [高级功能](#advanced-features)
  - [LLM 问答](#llm-qa)
  - [结构化数据提取](#structured-data-extraction)
  - [内容过滤](#content-filtering-1)
- [输出格式](#output-formats)
- [示例](#examples)
- [配置参考](#configuration-reference)
- [最佳实践与技巧](#best-practices--tips)

## 安装
安装 Crawl4AI 库时，Crawl4AI CLI 将自动安装。

## 基本用法

Crawl4AI CLI (`crwl`) 提供了一个简单的库接口：

```bash
# 基本爬取
crwl https://example.com

# 获取 Markdown 输出
crwl https://example.com -o markdown

# 详细 JSON 输出并绕过缓存
crwl https://example.com -o json -v --bypass-cache

# 查看用法示例
crwl --example
```

## 高级用法快速示例

如果克隆仓库并运行以下命令，您将根据 JSON-CSS 模式获得页面的 JSON 格式内容：

```bash
crwl "https://www.infoq.com/ai-ml-data-eng/" -e docs/examples/cli/extract_css.yml -s docs/examples/cli/css_schema.json -o json;
```

## 配置

### 浏览器配置

浏览器设置可以通过 YAML 文件或命令行参数配置：

```yaml
# browser.yml
headless: true
viewport_width: 1280
user_agent_mode: "random"
verbose: true
ignore_https_errors: true
```

```bash
# 使用配置文件
crwl https://example.com -B browser.yml

# 使用直接参数
crwl https://example.com -b "headless=true,viewport_width=1280,user_agent_mode=random"
```

### 爬虫配置

控制爬取行为：

```yaml
# crawler.yml
cache_mode: "bypass"
wait_until: "networkidle"
page_timeout: 30000
delay_before_return_html: 0.5
word_count_threshold: 100
scan_full_page: true
scroll_delay: 0.3
process_iframes: false
remove_overlay_elements: true
magic: true
verbose: true
```

```bash
# 使用配置文件
crwl https://example.com -C crawler.yml

# 使用直接参数
crwl https://example.com -c "css_selector=#main,delay_before_return_html=2,scan_full_page=true"
```

### 提取配置

支持两种类型的提取：

1. 基于 CSS/XPath 的提取：
```yaml
# extract_css.yml
type: "json-css"
params:
  verbose: true
```

```json
// css_schema.json
{
  "name": "ArticleExtractor",
  "baseSelector": ".article",
  "fields": [
    {
      "name": "title",
      "selector": "h1.title",
      "type": "text"
    },
    {
      "name": "link",
      "selector": "a.read-more",
      "type": "attribute",
      "attribute": "href"
    }
  ]
}
```

2. 基于 LLM 的提取：
```yaml
# extract_llm.yml
type: "llm"
provider: "openai/gpt-4"
instruction: "Extract all articles with their titles and links"
api_token: "your-token"
params:
  temperature: 0.3
  max_tokens: 1000
```

```json
// llm_schema.json
{
  "title": "Article",
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "The title of the article"
    },
    "link": {
      "type": "string",
      "description": "URL to the full article"
    }
  }
}
```

## 高级功能

### LLM 问答

关于爬取内容提问：

```bash
# 简单问题
crwl https://example.com -q "讨论的主要主题是什么？"

# 查看内容后提问
crwl https://example.com -o markdown  # 先查看内容
crwl https://example.com -q "总结关键点"
crwl https://example.com -q "结论是什么？"

# 结合高级爬取
crwl https://example.com \
    -B browser.yml \
    -c "css_selector=article,scan_full_page=true" \
    -q "提到了哪些优缺点？"
```

首次设置：
- 提示输入 LLM 提供商和 API 令牌
- 将配置保存在 `~/.crawl4ai/global.yml` 中
- 支持各种提供商（openai/gpt-4、anthropic/claude-3-sonnet 等）
- 对于 `ollama` 的情况，您不需要提供 API 令牌。
- 查看 [LiteLLM 提供商](https://docs.litellm.ai/docs/providers) 获取完整列表

### 结构化数据提取

使用 CSS 选择器提取结构化数据：

```bash
crwl https://example.com \
    -e extract_css.yml \
    -s css_schema.json \
    -o json
```

或使用基于 LLM 的提取：

```bash
crwl https://example.com \
    -e extract_llm.yml \
    -s llm_schema.json \
    -o json
```

### 内容过滤

根据相关性过滤内容：

```yaml
# filter_bm25.yml
type: "bm25"
query: "目标内容"
threshold: 1.0

# filter_pruning.yml
type: "pruning"
query: "焦点主题"
threshold: 0.48
```

```bash
crwl https://example.com -f filter_bm25.yml -o markdown-fit
```

## 输出格式

- `all` - 完整的爬取结果，包括元数据
- `json` - 提取的结构化数据（使用提取时）
- `markdown` / `md` - 原始 Markdown 输出
- `markdown-fit` / `md-fit` - 过滤后的 Markdown，以提高可读性

## 完整示例

1. 基本提取：
```bash
crwl https://example.com \
    -B browser.yml \
    -C crawler.yml \
    -o json
```

2. 结构化数据提取：
```bash
crwl https://example.com \
    -e extract_css.yml \
    -s css_schema.json \
    -o json \
    -v
```

3. 带过滤的 LLM 提取：
```bash
crwl https://example.com \
    -B browser.yml \
    -e extract_llm.yml \
    -s llm_schema.json \
    -f filter_bm25.yml \
    -o json
```

4. 交互式问答：
```bash
# 先爬取并查看
crwl https://example.com -o markdown

# 然后提问
crwl https://example.com -q "主要观点是什么？"
crwl https://example.com -q "总结结论"
```

## 最佳实践与技巧

1. **配置管理**：
   - 将常用配置保存在 YAML 文件中
   - 使用 CLI 参数进行快速覆盖
   - 将敏感数据（API 令牌）存储在 `~/.crawl4ai/global.yml` 中

2. **性能优化**：
   - 使用 `--bypass-cache` 获取最新内容
   - 对无限滚动页面启用 `scan_full_page`
   - 为动态内容调整 `delay_before_return_html`

3. **内容提取**：
   - 对结构化内容使用 CSS 提取
   - 对非结构化内容使用 LLM 提取
   - 结合过滤器以获得聚焦的结果

4. **问答工作流**：
   - 先用 `-o markdown` 查看内容
   - 提出具体问题
   - 使用适当的选择器获取更广泛的上下文

## 回顾

Crawl4AI CLI 提供：
- 通过文件和参数进行灵活配置
- 多种提取策略（CSS、XPath、LLM）
- 内容过滤和优化
- 交互式问答功能
- 各种输出格式