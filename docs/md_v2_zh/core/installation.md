# 安装与设置（2023版）

## 1. 基础安装

```bash
pip install crawl4ai
```

这将安装 **核心** Crawl4AI 库及其基本依赖项。 **不包含** 高级功能（如 transformers 或 PyTorch）。

## 2. 初始设置与诊断

### 2.1 运行设置命令
安装完成后，执行：

```bash
crawl4ai-setup
```

**功能说明：**
- 安装或更新常规模式和隐身模式所需的浏览器依赖
- 执行操作系统级检查（例如 Linux 缺失的库）
- 确认您的环境已准备好进行爬取

### 2.2 诊断
可选运行 **诊断** 以确认一切正常：

```bash
crawl4ai-doctor
```

此命令将尝试：
- 检查 Python 版本兼容性
- 验证 Playwright 安装
- 检查环境变量或库冲突

如发现问题，请按照提示操作（例如安装额外的系统包）并重新运行 `crawl4ai-setup`。

---

## 3. 验证安装：简单爬取（如已运行 `crawl4ai-doctor` 可跳过此步骤）

以下是一个展示 **基础** 爬取的 Python 脚本示例。它使用了新的 **`BrowserConfig`** 和 **`CrawlerRunConfig`** 以保持清晰，尽管本例中未传递自定义设置：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.example.com",
        )
        print(result.markdown[:300])  # 显示提取文本的前300个字符

if __name__ == "__main__":
    asyncio.run(main())
```

**预期** 结果：
- 无头浏览器会话加载 `example.com`
- Crawl4AI 返回约300个字符的 markdown 文本  
如遇错误，请重新运行 `crawl4ai-doctor` 或手动确保 Playwright 安装正确。

---

## 4. 高级安装（可选）

**警告**：仅在 **确实需要** 时安装。这些选项会引入大型依赖项（包括大模型），可能显著增加磁盘使用和内存负载。

### 4.1 Torch、Transformers 或全部功能

- **文本聚类（Torch）**  
  ```bash
  pip install crawl4ai[torch]
  crawl4ai-setup
  ```
  安装基于 PyTorch 的功能（如余弦相似度或高级语义分块）。

- **Transformers**  
  ```bash
  pip install crawl4ai[transformer]
  crawl4ai-setup
  ```
  添加基于 Hugging Face 的摘要或生成策略。

- **全部功能**  
  ```bash
  pip install crawl4ai[all]
  crawl4ai-setup
  ```

#### （可选）预下载模型
```bash
crawl4ai-download-models
```
此步骤将大型模型缓存到本地（如需要）。 **仅在** 工作流需要时执行。

---

## 5. Docker（实验性）

我们提供 **临时** Docker 方案用于测试。 **此方案不稳定，未来版本可能失效**。我们计划在 2025 年第一季度发布稳定的 Docker 版本。如仍想尝试：

```bash
docker pull unclecode/crawl4ai:basic
docker run -p 11235:11235 unclecode/crawl4ai:basic
```

之后可向 `http://localhost:11235/crawl` 发送 POST 请求执行爬取。 **不建议** 在生产环境中使用，直至新的 Docker 方案就绪（计划于 2025 年 1 月或 2 月发布）。

---

## 6. 本地服务器模式（旧版）

部分旧文档提到将 Crawl4AI 作为本地服务器运行。此方法已 **部分被** 新的 Docker 原型和即将发布的稳定服务器版本取代。您可以尝试，但预计会有重大变化。官方本地服务器说明将在新 Docker 架构完成后发布。

---

## 总结

1. **安装**：执行 `pip install crawl4ai` 并运行 `crawl4ai-setup`。
2. **诊断**：如遇错误，使用 `crawl4ai-doctor`。
3. **验证**：使用最小化的 `BrowserConfig` + `CrawlerRunConfig` 爬取 `example.com`。
4. **高级** 功能（Torch、Transformers）为 **可选**——如非必需请避免安装（会显著增加资源消耗）。
5. **Docker** 为 **实验性**——稳定版本发布前请谨慎使用。
6. 旧文档中的 **本地服务器** 引用已基本弃用；新方案正在开发中。

**有问题？** 查看 [GitHub issues](https://github.com/unclecode/crawl4ai/issues) 获取更新或向社区提问！