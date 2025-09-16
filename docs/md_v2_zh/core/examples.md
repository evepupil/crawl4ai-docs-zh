正在阅读我无法读取《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/undetected_simple_demo》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/virtual_scroll_example》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/serp_api_project_11_feb》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/identity_based_browsing》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/browser_optimization_example》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/tutorial_dynamic_clicks》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/llm_extraction_openai_pricing》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/ssl_example》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/proxy_rotation_demo》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/README_BUILTIN_BROWSER》、《https://github.com/unclecode/crawl4ai/blob/main/CONTRIBUTORS》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/full_page_screenshot_and_pdf_export》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/network_console_capture_example》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/docker_python_sdk》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/crawler_monitor_example》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/amazon_product_extraction_direct_url》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/quickstart_examples_set_1》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/language_support_example》、《https://github.com/unclecode/crawl4ai/blob/main/docs/examples/crypto_analysis_example》文件的内容。其他文件已阅读并为你总结如下：
# 代码示例

本页面提供了全面的示例脚本列表，展示了Crawl4AI的各种功能和能力。每个示例都旨在展示特定功能，帮助您更轻松地理解如何在项目中实现这些功能。

## 入门示例

| 示例 | 描述 | 链接 |
|---------|-------------|------|
| Hello World | 基础入门示例，展示AsyncWebCrawler的基本用法，包括JavaScript执行和内容过滤。 | [查看代码](链接9) |
| Quickstart | 综合示例集，展示基本爬取、内容清理、链接分析、JavaScript执行、CSS选择器、媒体处理、自定义钩子、代理配置、截图和多种提取策略等功能。 | [查看代码](链接4) |
| Quickstart Set 1 | Crawl4AI入门基础示例。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/quickstart_examples_set_1.py) |
| Quickstart Set 2 | Crawl4AI进阶使用示例。 | [查看代码](链接5) |

## 浏览器与爬取功能

| 示例 | 描述 | 链接 |
|---------|-------------|------|
| 内置浏览器 | 演示如何使用内置浏览器功能。 | [查看代码](链接6) |
| 浏览器优化 | 专注于浏览器性能优化技术。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/browser_optimization_example.py) |
| arun vs arun_many | 比较`arun`和`arun_many`方法在单URL与多URL爬取中的差异。 | [查看代码](链接25) |
| 多URL爬取 | 展示如何异步爬取多个URL。 | [查看代码](链接21) |
| 页面交互 | 通过点击与动态元素交互的指南。 | [查看指南](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/tutorial_dynamic_clicks.md) |
| 爬虫监控 | 展示如何监控爬虫活动和状态。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/crawler_monitor_example.py) |
| 全页截图与PDF | 从大型网页捕获全页截图和PDF的指南。 | [查看指南](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/full_page_screenshot_and_pdf_export.md) |

## 高级爬取与深度爬取

| 示例 | 描述 | 链接 |
|---------|-------------|------|
| 深度爬取 | 深度爬取能力综合教程，展示BFS和BestFirst策略、流式与非流式执行、过滤器、评分器和高级配置。 | [查看代码](链接7) |
| 虚拟滚动 | 处理Twitter、Instagram等网站虚拟化滚动的综合示例。展示本地测试服务器上的不同滚动场景。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/virtual_scroll_example.py) |
| 自适应爬取 | 展示智能爬取，自动判断何时收集到足够信息。 | [查看代码](链接26) |
| 调度器 | 展示如何使用爬取调度器进行高级工作负载管理。 | [查看代码](链接1) |
| 存储状态 | 管理浏览器存储状态实现持久化的教程。 | [查看指南](链接8) |
| 网络控制台捕获 | 演示如何捕获和分析网络请求及控制台日志。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/network_console_capture_example.py) |

## 提取策略

| 示例 | 描述 | 链接 |
|---------|-------------|------|
| 提取策略 | 展示不同提取策略与多种输入格式(markdown、HTML、fit_markdown)和基于JSON的提取器(CSS和XPath)。 | [查看代码](链接15) |
| 爬取策略 | 比较不同爬取策略的性能。 | [查看代码](链接16) |
| LLM提取 | 专门针对OpenAI定价数据的LLM提取演示。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/llm_extraction_openai_pricing.py) |
| LLM Markdown | 展示如何使用LLM从爬取内容生成markdown。 | [查看代码](链接22) |
| 页面摘要 | 展示如何汇总网页内容。 | [查看代码](链接27) |

## 电商与专业爬取

| 示例 | 描述 | 链接 |
|---------|-------------|------|
| 亚马逊产品提取 | 演示如何使用CSS选择器从亚马逊搜索结果提取结构化产品数据。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/amazon_product_extraction_direct_url.py) |
| 亚马逊与钩子 | 展示在亚马逊产品提取中使用钩子。 | [查看代码](链接28) |
| 亚马逊与JavaScript | 演示使用自定义JavaScript进行亚马逊产品提取。 | [查看代码](链接29) |
| 加密货币分析 | 演示如何爬取和分析加密货币数据。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/crypto_analysis_example.py) |
| SERP API | 演示在搜索引擎结果页面中使用Crawl4AI。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/serp_api_project_11_feb.py) |

## 反爬虫与隐身功能

| 示例 | 描述 | 链接 |
|---------|-------------|------|
| 隐身模式快速入门 | 五个实用示例，展示如何使用隐身模式绕过基本爬虫检测。 | [查看代码](链接13) |
| 隐身模式综合 | 隐身模式功能的综合演示，包括爬虫检测测试和比较。 | [查看代码](链接17) |
| 无痕浏览器 | 简单示例展示如何使用无痕浏览器适配器。 | [查看代码](链接30) |
| 无痕浏览器演示 | 常规与无痕浏览器模式对比的基础演示。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/undetected_simple_demo.py) |
| 无痕测试 | 在各种爬虫检测服务上比较常规与无痕浏览器的进阶测试。 | [查看文件夹](链接14) |

## 定制化与安全

| 示例 | 描述 | 链接 |
|---------|-------------|------|
| 钩子 | 展示如何在爬取过程的不同阶段使用钩子进行高级定制。 | [查看代码](链接18) |
| 基于身份的浏览 | 展示真实浏览体验的基于身份的浏览配置。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/identity_based_browsing.py) |
| 代理轮换 | 展示如何通过代理轮换进行网页爬取并避免IP封禁。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/proxy_rotation_demo.py) |
| SSL证书 | 展示SSL证书处理和验证。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/ssl_example.py) |
| 语言支持 | 展示爬取过程中如何处理不同语言。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/language_support_example.py) |
| 地理位置 | 演示如何使用地理位置功能。 | [查看代码](链接10) |

## Docker与部署

| 示例 | 描述 | 链接 |
|---------|-------------|------|
| Docker配置 | 演示如何创建和使用Docker配置对象。 | [查看代码](链接19) |
| Docker基础 | Docker部署测试套件，通过Docker API展示各种功能。 | [查看代码](链接20) |
| Docker REST API | 展示如何使用REST API与Crawl4AI Docker交互。 | [查看代码](链接23) |
| Docker SDK | 演示使用Python SDK操作Crawl4AI Docker。 | [查看代码](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/docker_python_sdk.py) |

## 应用示例

| 示例 | 描述 | 链接 |
|---------|-------------|------|
| 研究助手 | 演示如何使用Crawl4AI构建研究助手。 | [查看代码](链接11) |
| REST调用 | 展示如何使用Crawl4AI进行REST API调用。 | [查看代码](链接2) |
| Chainlit集成 | 展示如何将Crawl4AI与Chainlit集成。 | [查看指南](链接31) |
| Crawl4AI vs FireCrawl | 比较Crawl4AI与FireCrawl库。 | [查看代码](链接12) |

## 内容生成与Markdown

| 示例 | 描述 | 链接 |
|---------|-------------|------|
| 内容源 | 演示在markdown生成中如何处理不同内容源。 | [查看代码](链接24) |
| 内容源(简化版) | 内容源使用的简化版本。 | [查看代码](链接3) |
| 内置浏览器指南 | 使用内置浏览器功能的指南。 | [查看指南](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/README_BUILTIN_BROWSER.md) |

## 运行示例

要运行这些示例，您需要先安装Crawl4AI：

```bash
pip install crawl4ai
```

然后可以像这样运行示例脚本：

```bash
python -m docs.examples.hello_world
```

对于需要额外依赖或环境变量的示例，请参考每个文件顶部的注释。

部分示例可能需要：
- API密钥(用于基于LLM的示例)
- Docker设置(用于Docker相关示例)
- 额外依赖(在示例文件中指定)

## 贡献新示例

如果您创建了展示Crawl4AI独特用例或功能的示例，欢迎贡献到我们的示例集合。请参阅[贡献指南](https://github.com/unclecode/crawl4ai/blob/main/CONTRIBUTORS.md)获取更多信息。