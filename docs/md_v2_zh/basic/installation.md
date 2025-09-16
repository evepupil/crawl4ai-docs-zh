# 安装 💻

Crawl4AI 提供灵活的安装选项以满足各种使用场景。您可以将其安装为 Python 包、与 Docker 一起使用，或作为本地服务器运行。

## 选项 1：Python 包安装（推荐）

Crawl4AI 现已上线 PyPI，安装比以往更加简便。请根据您的需求选择最合适的选项：

### 基础安装

适用于基础网页爬取和抓取任务：

```bash
pip install crawl4ai
playwright install # 安装 Playwright 依赖
```

### 安装含 PyTorch 版本

适用于高级文本聚类（包含 CosineSimilarity 聚类策略）：

```bash
pip install crawl4ai[torch]
```

### 安装含 Transformers 版本

适用于文本摘要和 Hugging Face 模型：

```bash
pip install crawl4ai[transformer]
```

### 完整安装

获取所有功能：

```bash
pip install crawl4ai[all]
```

### 开发安装

适用于计划修改源代码的贡献者：

```bash
git clone https://github.com/unclecode/crawl4ai.git
cd crawl4ai
pip install -e ".[all]"
playwright install # 安装 Playwright 依赖
```

💡 使用 "torch"、"transformer" 或 "all" 选项安装后，建议运行以下 CLI 命令来加载所需模型：

```bash
crawl4ai-download-models
```

此步骤为可选，但将提升爬虫的性能和速度。安装后只需执行一次。

## Ubuntu 系统 Playwright 安装说明

如果在 Ubuntu 上安装 Playwright 时遇到问题，可能需要安装额外的依赖项：

```bash
sudo apt-get install -y \
    libwoff1 \
    libopus0 \
    libwebp7 \
    libwebpdemux2 \
    libenchant-2-2 \
    libgudev-1.0-0 \
    libsecret-1-0 \
    libhyphen0 \
    libgdk-pixbuf2.0-0 \
    libegl1 \
    libnotify4 \
    libxslt1.1 \
    libevent-2.1-7 \
    libgles2 \
    libxcomposite1 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libepoxy0 \
    libgtk-3-0 \
    libharfbuzz-icu0 \
    libgstreamer-gl1.0-0 \
    libgstreamer-plugins-bad1.0-0 \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    libxt6 \
    libxaw7 \
    xvfb \
    fonts-noto-color-emoji \
    libfontconfig \
    libfreetype6 \
    xfonts-cyrillic \
    xfonts-scalable \
    fonts-liberation \
    fonts-ipafont-gothic \
    fonts-wqy-zenhei \
    fonts-tlwg-loma-otf \
    fonts-freefont-ttf
```

## 选项 2：使用 Docker（即将推出）

Crawl4AI 的 Docker 支持目前正在开发中，即将推出。这将允许您在容器化环境中运行 Crawl4AI，确保在不同系统间的一致性。

## 选项 3：本地服务器安装

对于希望将 Crawl4AI 作为本地服务器运行的用户，将在 Docker 实现完成后提供相关说明。

## 验证安装

安装完成后，您可以通过运行一个简单的 Python 脚本来验证 Crawl4AI 是否正常工作：

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url="https://www.example.com")
        print(result.markdown[:500])  # 打印前 500 个字符

if __name__ == "__main__":
    asyncio.run(main())
```

此脚本应能成功爬取示例网站并打印提取内容的前 500 个字符。

## 获取帮助

如果在安装或使用过程中遇到任何问题，请查阅[文档](https://docs.crawl4ai.com/)或在 [GitHub 仓库](https://github.com/unclecode/crawl4ai/issues)提交问题。

祝您爬取愉快！ 🕷️🤖