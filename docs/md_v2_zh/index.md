# 🚀🤖 Crawl4AI：开源LLM友好型网络爬虫与抓取工具

<div class = "badges" align="center">

  <p>
    <a href="https://trendshift.io/repositories/11716" target="_blank">
      <img src="https://trendshift.io/api/badge/repositories/11716"
           alt="unclecode%2Fcrawl4ai | Trendshift"
           style="width: 250px; height: 55px;"
           width="250" height="55"/>
    </a>

  </p>

  <p>
    <a href="https://github.com/unclecode/crawl4ai/stargazers">
      <img src="https://img.shields.io/github/stars/unclecode/crawl4ai?style=social"
           alt="GitHub Stars"/>
    </a>
    <a href="https://github.com/unclecode/crawl4ai/network/members">
      <img src="https://img.shields.io/github/forks/unclecode/crawl4ai?style=social"
           alt="GitHub Forks"/>
    </a>
    <a href="https://badge.fury.io/py/crawl4ai">
      <img src="https://badge.fury.io/py/crawl4ai.svg"
           alt="PyPI version"/>
    </a>
  </p>

  <p>
    <a href="https://pypi.org/project/crawl4ai/">
      <img src="https://img.shields.io/pypi/pyversions/crawl4ai"
           alt="Python Version"/>
    </a>
    <a href="https://pepy.tech/project/crawl4ai">
      <img src="https://static.pepy.tech/badge/crawl4ai/month"
           alt="Downloads"/>
    </a>
    <a href="https://github.com/unclecode/crawl4ai/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/unclecode/crawl4ai"
           alt="License"/>
    </a>
  </p>
  <p align="center">
    <a href="https://x.com/crawl4ai">
      <img src="https://img.shields.io/badge/关注X平台-000000?style=for-the-badge&logo=x&logoColor=white" alt="Follow on X" />
    </a>
    <a href="https://www.linkedin.com/company/crawl4ai">
      <img src="https://img.shields.io/badge/关注LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="Follow on LinkedIn" />
    </a>
    <a href="https://discord.gg/jP8KfhDhyN">
      <img src="https://img.shields.io/badge/加入Discord社区-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Join our Discord" />
    </a>
  </p>
  
</div>

Crawl4AI是GitHub趋势榜第一的开源项目，由活跃社区持续维护。它为大型语言模型、AI代理和数据管道提供极速、AI就绪的网络爬取方案。完全开源、灵活且为实时性能而构建的**Crawl4AI**，赋予开发者无与伦比的速度、精度和部署便捷性。

> **注意**：如需查看旧版文档，请访问[此处](https://old.docs.crawl4ai.com)。

## 🎯 新功能：自适应网络爬取
Crawl4AI现配备智能自适应爬取功能，懂得何时停止！通过先进的信息觅食算法，它能判断何时已收集足够信息来回答您的查询。

[了解自适应爬取详情→](core/adaptive-crawling.md)


## 快速开始
以下示例展示如何轻松使用Crawl4AI的异步功能：

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    # 创建AsyncWebCrawler实例
    async with AsyncWebCrawler() as crawler:
        # 对URL运行爬虫
        result = await crawler.arun(url="https://crawl4ai.com")

        # 打印提取内容
        print(result.markdown)

# 运行异步主函数
asyncio.run(main())
```

---

## 视频教程

<div align="center">
  <iframe width="560" height="315" src="https://www.youtube.com/embed/xo3qK6Hg9AA?start=15" title="Crawl4AI教程" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

---

## Crawl4AI能做什么？

Crawl4AI是一款功能丰富的爬虫和抓取工具，旨在：

1. **生成纯净Markdown**：完美适配RAG管道或直接输入LLM。  
2. **结构化提取**：通过CSS、XPath或基于LLM的解析提取重复模式。  
3. **高级浏览器控制**：钩子、代理、隐身模式、会话复用——精细控制。  
4. **高性能**：并行爬取、分块提取、实时用例支持。  
5. **开源**：无强制API密钥、无付费墙——人人可访问数据。  

**核心理念**：
- **数据民主化**：免费使用、透明且高度可配置。  
- **LLM友好**：最小化处理、结构良好的文本/图像/元数据，便于AI模型消费。

---

## 文档结构
为帮助您快速入门，我们将文档分为清晰章节：

- **安装指南**  
  通过pip或Docker安装Crawl4AI的基础说明。  
- **快速开始**  
  实践入门指南，展示首次爬取、生成Markdown和简单提取。  
- **核心功能**  
  深入讲解单页爬取、高级浏览器/爬虫参数、内容过滤和缓存。  
- **进阶指南**  
  探索链接与媒体处理、懒加载、钩子与认证、代理、会话管理等。  
- **提取技术**  
  无LLM（CSS/XPath）与基于LLM策略的详细参考，分块与聚类方法。  
- **API参考**  
  查阅`AsyncWebCrawler`、`arun()`和`CrawlResult`等类与方法的专业技术细节。

各章节均提供可**直接复制粘贴**的代码示例。如有遗漏或疑问，请提交issue或PR。

---

## 支持方式

- **加星 & Fork**：若Crawl4AI对您有帮助，请在GitHub加星或fork添加新特性。  
- **提交Issue**：遇到bug或缺少功能？提交issue让我们改进。  
- **发起PR**：无论是小修复、大功能还是文档优化——欢迎贡献。  
- **加入Discord**：与社区交流爬取技巧、AI工作流。  
- **口碑传播**：在博客、演讲或社交媒体推荐Crawl4AI。  

**我们的使命**：赋能学生、研究者、创业者和数据科学家——以速度、成本效益和创作自由访问、解析和塑造世界数据。

---

## 快速链接

- **[GitHub仓库](https://github.com/unclecode/crawl4ai)**  
- **[安装指南](./core/installation.md)**  
- **[快速入门](./core/quickstart.md)**  
- **[API参考](./api/async-webcrawler.md)**  
- **[更新日志](https://github.com/unclecode/crawl4ai/blob/main/CHANGELOG.md)**  

感谢您加入这段旅程。让我们共同构建**开放、民主**的数据提取与AI方案。

爬取愉快！  
— *Unclecode，Crawl4AI创始人兼维护者*