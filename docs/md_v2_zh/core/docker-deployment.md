正在阅读我无法读取《http://localhost:11235/crawl》、《http://localhost:11235/crawl/stream》、《http://localhost:11235》、《http://localhost:11235/mcp/sse》、《https://discord.gg/crawl4ai》、《http://localhost:11235/mcp/schema》、《http://localhost:11235/playground》、《http://localhost:11235/health》文件的内容。其他文件已阅读并为你总结如下：
# Crawl4AI Docker 指南 🐳

## 目录
- [先决条件](#先决条件)
- [安装](#安装)
  - [选项1：使用预构建的 Docker Hub 镜像（推荐）](#选项1-使用预构建的docker-hub镜像推荐)
  - [选项2：使用 Docker Compose](#选项2-使用docker-compose)
  - [选项3：手动本地构建与运行](#选项3-手动本地构建运行)
- [Dockerfile 参数](#dockerfile参数)
- [使用 API](#使用api)
  - [Playground 界面](#playground界面)
  - [Python SDK](#python-sdk)
  - [理解请求模式](#理解请求模式)
  - [REST API 示例](#rest-api示例)
- [附加 API 端点](#附加api端点)
  - [HTML 提取端点](#html提取端点)
  - [截图端点](#截图端点)
  - [PDF 导出端点](#pdf导出端点)
  - [JavaScript 执行端点](#javascript执行端点)
  - [库上下文端点](#库上下文端点)
- [MCP（模型上下文协议）支持](#mcp模型上下文协议支持)
  - [什么是 MCP？](#什么是mcp)
  - [通过 MCP 连接](#通过mcp连接)
  - [与 Claude Code 一起使用](#与claude-code一起使用)
  - [可用的 MCP 工具](#可用的mcp工具)
  - [测试 MCP 连接](#测试mcp连接)
  - [MCP 模式](#mcp模式)
- [指标与监控](#指标与监控)
- [部署场景](#部署场景)
- [完整示例](#完整示例)
- [服务器配置](#服务器配置)
  - [理解 config.yml](#理解configyml)
  - [JWT 认证](#jwt认证)
  - [配置技巧与最佳实践](#配置技巧与最佳实践)
  - [自定义配置](#自定义配置)
  - [配置建议](#配置建议)
- [获取帮助](#获取帮助)
- [总结](#总结)

## 先决条件

开始之前，请确保您已具备：
- 已安装并运行 Docker（版本 20.10.0 或更高），包括 `docker compose`（通常与 Docker Desktop 捆绑）。
- `git` 用于克隆仓库。
- 至少 4GB 可用内存（重度使用推荐更多）。
- Python 3.10+（如果使用 Python SDK）。
- Node.js 16+（如果使用 Node.js 示例）。

> 💡 **专业提示**：运行 `docker info` 检查 Docker 安装和可用资源。

## 安装

我们提供多种方式运行 Crawl4AI 服务器。最快的方法是使用我们预构建的 Docker Hub 镜像。

### 选项1：使用预构建的 Docker Hub 镜像（推荐）

直接从 Docker Hub 拉取并运行镜像，无需本地构建。

#### 1. 拉取镜像

最新版本为 `0.7.3`。镜像支持多架构，Docker 会自动为您的系统拉取正确版本。

> 💡 **注意**：`latest` 标签指向稳定的 `0.7.3` 版本。

```bash
# 拉取最新版本
docker pull unclecode/crawl4ai:0.7.3

# 或使用 latest 标签拉取
docker pull unclecode/crawl4ai:latest
```

#### 2. 设置环境（API 密钥）

如果计划使用 LLM，在工作目录创建 `.llm.env` 文件：

```bash
# 创建包含 API 密钥的 .llm.env 文件
cat > .llm.env << EOL
# OpenAI
OPENAI_API_KEY=sk-your-key

# Anthropic
ANTHROPIC_API_KEY=your-anthropic-key

# 其他提供商按需添加
# DEEPSEEK_API_KEY=your-deepseek-key
# GROQ_API_KEY=your-groq-key
# TOGETHER_API_KEY=your-together-key
# MISTRAL_API_KEY=your-mistral-key
# GEMINI_API_TOKEN=your-gemini-token
EOL
```
> 🔑 **注意**：保护您的 API 密钥！切勿将 `.llm.env` 提交到版本控制。

#### 3. 运行容器

*   **基本运行：**
    ```bash
    docker run -d \
      -p 11235:11235 \
      --name crawl4ai \
      --shm-size=1g \
      unclecode/crawl4ai:latest
    ```

*   **支持 LLM：**
    ```bash
    # 确保当前目录有 .llm.env 文件
    docker run -d \
      -p 11235:11235 \
      --name crawl4ai \
      --env-file .llm.env \
      --shm-size=1g \
      unclecode/crawl4ai:latest
    ```

> 服务器将在 `http://localhost:11235` 可用。访问 `/playground` 使用交互式测试界面。

#### 4. 停止容器

```bash
docker stop crawl4ai && docker rm crawl4ai
```

#### Docker Hub 版本说明

*   **镜像名称：** `unclecode/crawl4ai`
*   **标签格式：** `LIBRARY_VERSION[-SUFFIX]`（如 `0.7.3`）
    *   `LIBRARY_VERSION`：核心 `crawl4ai` Python 库的语义版本
    *   `SUFFIX`：可选标签，用于发布候选（``）和修订（`r1`）
*   **`latest` 标签：** 指向最新的稳定版本
*   **多架构支持：** 所有镜像通过单一标签支持 `linux/amd64` 和 `linux/arm64` 架构

### 选项2：使用 Docker Compose

Docker Compose 简化了服务的构建和运行，特别适合本地开发和测试。

#### 1. 克隆仓库

```bash
git clone 链接4
cd crawl4ai
```

#### 2. 环境设置（API 密钥）

如果计划使用 LLM，复制示例环境文件并添加 API 密钥。此文件应位于**项目根目录**。

```bash
# 确保在 'crawl4ai' 根目录
cp deploy/docker/.llm.env.example .llm.env

# 编辑 .llm.env 并添加 API 密钥
```

**灵活的 LLM 提供商配置：**

Docker 设置现在通过三种方法支持灵活的 LLM 提供商配置：

1. **环境变量**（最高优先级）：设置 `LLM_PROVIDER` 覆盖默认值
   ```bash
   export LLM_PROVIDER="anthropic/claude-3-opus"
   # 或在 .llm.env 文件中：
   # LLM_PROVIDER=anthropic/claude-3-opus
   ```

2. **API 请求参数**：按请求指定提供商
   ```json
   {
     "url": "链接3",
     "f": "llm",
     "provider": "groq/mixtral-8x7b"
   }
   ```

3. **配置文件默认值**：回退到 `config.yml`（默认：`openai/gpt-4o-mini`）

系统根据配置文件中设置的 `api_key_env` 自动选择相应的 API 密钥。

#### 3. 使用 Compose 构建和运行

项目根目录的 `docker-compose.yml` 文件提供了简化方法，使用 buildx 自动处理架构检测。

*   **从 Docker Hub 运行预构建镜像：**
    ```bash
    # 从 Docker Hub 拉取并运行发布候选
    # 自动选择正确的架构
    IMAGE=unclecode/crawl4ai:latest docker compose up -d
    ```

*   **本地构建并运行：**
    ```bash
    # 使用 Dockerfile 本地构建镜像并运行
    # 自动为您的机器使用正确的架构
    docker compose up --build -d
    ```

*   **自定义构建：**
    ```bash
    # 构建包含所有功能的镜像（包括 torch 和 transformers）
    INSTALL_TYPE=all docker compose up --build -d
    
    # 构建支持 GPU 的镜像（适用于 AMD64 平台）
    ENABLE_GPU=true docker compose up --build -d
    ```

> 服务器将在 `http://localhost:11235` 可用。

#### 4. 停止服务

```bash
# 停止服务
docker compose down
```

### 选项3：手动本地构建与运行

如果您希望不使用 Docker Compose，直接控制构建和运行过程。

#### 1. 克隆仓库并设置环境

按照 Docker Compose 部分中的步骤 1 和 2（克隆仓库，`cd crawl4ai`，在根目录创建 `.llm.env`）。

#### 2. 构建镜像（多架构）

使用 `docker buildx` 构建镜像。Crawl4AI 现在使用 buildx 自动处理多架构构建。

```bash
# 确保在 'crawl4ai' 根目录
# 为当前架构构建并加载到 Docker
docker buildx build -t crawl4ai-local:latest --load .

# 或为多种架构构建（适用于发布）
docker buildx build --platform linux/amd64,linux/arm64 -t crawl4ai-local:latest --load .

# 使用附加选项构建
docker buildx build \
  --build-arg INSTALL_TYPE=all \
  --build-arg ENABLE_GPU=false \
  -t crawl4ai-local:latest --load .
```

#### 3. 运行容器

*   **基本运行（不支持 LLM）：**
    ```bash
    docker run -d \
      -p 11235:11235 \
      --name crawl4ai-standalone \
      --shm-size=1g \
      crawl4ai-local:latest
    ```

*   **支持 LLM：**
    ```bash
    # 确保当前目录有 .llm.env 文件（项目根目录）
    docker run -d \
      -p 11235:11235 \
      --name crawl4ai-standalone \
      --env-file .llm.env \
      --shm-size=1g \
      crawl4ai-local:latest
    ```

> 服务器将在 `http://localhost:11235` 可用。

#### 4. 停止手动容器

```bash
docker stop crawl4ai-standalone && docker rm crawl4ai-standalone
```

---

## MCP（模型上下文协议）支持

Crawl4AI 服务器包含对模型上下文协议（MCP）的支持，允许您将服务器的功能直接连接到 MCP 兼容客户端，如 Claude Code。

### 什么是 MCP？

MCP 是一种开放协议，标准化了应用程序如何向 LLM 提供上下文。它允许 AI 模型通过标准化接口访问外部工具、数据源和服务。

### 通过 MCP 连接

Crawl4AI 服务器公开两个 MCP 端点：

- **服务器发送事件（SSE）**：`http://localhost:11235/mcp/sse`
- **WebSocket**：`ws://localhost:11235/mcp/ws`

### 与 Claude Code 一起使用

您可以通过简单命令将 Crawl4AI 添加为 Claude Code 中的 MCP 工具提供商：

```bash
# 将 Crawl4AI 服务器添加为 MCP 提供商
claude mcp add --transport sse c4ai-sse http://localhost:11235/mcp/sse

# 列出所有 MCP 提供商以验证是否添加成功
claude mcp list
```

连接后，Claude Code 可以直接使用 Crawl4AI 的功能，如截图捕获、PDF 生成和 HTML 处理，无需单独进行 API 调用。

### 可用的 MCP 工具

通过 MCP 连接时，以下工具可用：

- `md` - 从网页内容生成 Markdown
- `html` - 提取预处理后的 HTML
- `screenshot` - 捕获网页截图
- `pdf` - 生成 PDF 文档
- `execute_js` - 在网页上运行 JavaScript
- `crawl` - 执行多 URL 爬取
- `ask` - 查询 Crawl4AI 库上下文

### 测试 MCP 连接

您可以使用仓库中包含的测试文件测试 MCP WebSocket 连接：

```bash
# 从仓库根目录
python tests/mcp/test_mcp_socket.py
```

### MCP 模式

访问 `http://localhost:11235/mcp/schema` 获取每个工具参数和功能的详细信息。

---

## 附加 API 端点

除了核心的 `/crawl` 和 `/crawl/stream` 端点外，服务器还提供几个专用端点：

### HTML 提取端点

```
POST /html
```

爬取 URL 并返回预处理后的 HTML，优化用于模式提取。

```json
{
  "url": "链接3"
}
```

### 截图端点

```
POST /screenshot
```

捕获指定 URL 的全页 PNG 截图。

```json
{
  "url": "链接3",
  "screenshot_wait_for": 2,
  "output_path": "/path/to/save/screenshot.png"
}
```

- `screenshot_wait_for`：捕获前的可选延迟（秒，默认：2）
- `output_path`：保存截图的可选路径（推荐）

### PDF 导出端点

```
POST /pdf
```

生成指定 URL 的 PDF 文档。

```json
{
  "url": "链接3",
  "output_path": "/path/to/save/document.pdf"
}
```

- `output_path`：保存 PDF 的可选路径（推荐）

### JavaScript 执行端点

```
POST /execute_js
```

在指定 URL 上执行 JavaScript 片段并返回完整的爬取结果。

```json
{
  "url": "链接3",
  "scripts": [
    "return document.title",
    "return Array.from(document.querySelectorAll('a')).map(a => a.href)"
  ]
}
```

- `scripts`：按顺序执行的 JavaScript 片段列表

---

## Dockerfile 参数

您可以使用构建参数（`--build-arg`）自定义镜像构建过程。这些通常通过 `docker buildx build` 或在 `docker-compose.yml` 文件中使用。

```bash
# 示例：使用 buildx 构建包含 'all' 功能的镜像
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --build-arg INSTALL_TYPE=all \
  -t yourname/crawl4ai-all:latest \
  --load \
  . # 从根上下文构建
```

### 构建参数说明

| 参数         | 描述                              | 默认值   | 选项                            |
| :----------- | :-------------------------------- | :-------- | :----------------------------- |
| INSTALL_TYPE | 功能集                            | `default` | `default`, `all`, `torch`, `transformer` |
| ENABLE_GPU   | GPU 支持（AMD64 的 CUDA）         | `false`   | `true`, `false`                |
| APP_HOME     | 容器内的安装路径（高级）          | `/app`    | 任何有效路径                 |
| USE_LOCAL    | 从本地源安装库                    | `true`    | `true`, `false`                |
| GITHUB_REPO  | 如果 USE_LOCAL=false 时克隆的 Git 仓库 | *(见 Dockerfile)* | 任何 git URL                  |
| GITHUB_BRANCH| 如果 USE_LOCAL=false 时克隆的 Git 分支 | `main`    | 任何分支名称                  |

*(注意：PYTHON_VERSION 由 Dockerfile 中的 `FROM` 指令固定)*

### 构建最佳实践

1.  **选择正确的安装类型**
    *   `default`：基本安装，镜像最小。适用于大多数标准网页抓取和 Markdown 生成。
    *   `all`：完整功能，包括 `torch` 和 `transformers`，用于高级提取策略（如 CosineStrategy、某些 LLM 过滤器）。镜像显著增大。确保您需要这些额外功能。
2.  **平台考虑**
    *   使用 `buildx` 构建多架构镜像，特别是推送到注册表时。
    *   使用 `docker compose` 配置文件（`local-amd64`、`local-arm64`）轻松进行特定平台的本地构建。
3.  **性能优化**
    *   镜像自动包含平台特定优化（AMD64 的 OpenMP，ARM64 的 OpenBLAS）。

---

## 使用 API

通过 REST API（默认为 `http://localhost:11235`）与运行的 Docker 服务器通信。您可以使用 Python SDK 或直接进行 HTTP 请求。

### Playground 界面

内置的 web playground 在 `http://localhost:11235/playground` 可用，用于测试和生成 API 请求。Playground 允许您：

1. 使用主库的 Python 语法配置 `CrawlerRunConfig` 和 `BrowserConfig`
2. 直接从界面测试爬取操作
3. 根据您的配置生成相应的 JSON REST API 请求

这是在构建集成时将 Python 配置转换为 JSON 请求的最简单方法。

### Python SDK

安装 SDK：`pip install crawl4ai`

```python
import asyncio
from crawl4ai.docker_client import Crawl4aiDockerClient
from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode # 假设您已安装 crawl4ai

async def main():
    # 指向正确的服务器端口
    async with Crawl4aiDockerClient(base_url="http://localhost:11235", verbose=True) as client:
        # 如果服务器启用了 JWT，首先进行认证：
        # await client.authenticate("user@example.com") # 参见服务器配置部分

        # 示例非流式爬取
        print("--- 运行非流式爬取 ---")
        results = await client.crawl(
            ["链接5"],
            browser_config=BrowserConfig(headless=True), # 使用库类辅助配置
            crawler_config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
        )
        if results: # client.crawl 失败时返回 None
          print(f"非流式结果成功：{results.success}")
          if results.success:
              for result in results: # 遍历 CrawlResultContainer
                  print(f"URL: {result.url}, 成功: {result.success}")
        else:
            print("非流式爬取失败。")


        # 示例流式爬取
        print("\n--- 运行流式爬取 ---")
        stream_config = CrawlerRunConfig(stream=True, cache_mode=CacheMode.BYPASS)
        try:
            async for result in await client.crawl( # client.crawl 返回异步生成器用于流式处理
                ["链接5", "链接6"],
                browser_config=BrowserConfig(headless=True),
                crawler_config=stream_config
            ):
                print(f"流式结果: URL: {result.url}, 成功: {result.success}")
        except Exception as e:
            print(f"流式爬取失败: {e}")


        # 示例获取模式
        print("\n--- 获取模式 ---")
        schema = await client.get_schema()
        print(f"收到模式: {bool(schema)}") # 打印是否收到模式

if __name__ == "__main__":
    asyncio.run(main())
```

*(SDK 参数如 timeout、verify_ssl 等保持不变)*

### 第二种方法：直接 API 调用

关键的是，当直接通过 JSON 发送配置时，任何非原始值（如配置对象或策略）**必须**遵循 `{"type": "ClassName", "params": {...}}` 结构。字典必须包装为 `{"type": "dict", "value": {...}}`。

*(保留配置结构、基本模式、简单与复杂、策略模式、复杂嵌套示例、快速语法概述、重要规则、专业提示的详细解释)*

#### 更多示例 *(确保模式示例使用 type/value 包装)*

**高级爬取器配置**
*(保留示例，确保 cache_mode 使用有效枚举值如 "bypass")*

**提取策略**
```json
{
    "crawler_config": {
        "type": "CrawlerRunConfig",
        "params": {
            "extraction_strategy": {
                "type": "JsonCssExtractionStrategy",
                "params": {
                    "schema": {
                        "type": "dict",
                        "value": {
                           "baseSelector": "article.post",
                           "fields": [
                               {"name": "title", "selector": "h1", "type": "text"},
                               {"name": "content", "selector": ".content", "type": "html"}
                           ]
                         }
                    }
                }
            }
        }
    }
}
```

**LLM 提取策略** *(保留示例，确保模式使用 type/value 包装)*
*(保留深度爬取器示例)*

### REST API 示例

将 URL 更新为使用端口 `11235`。

#### 简单爬取

```python
import requests

# 配置对象转换为所需的 JSON 结构
browser_config_payload = {
    "type": "BrowserConfig",
    "params": {"headless": True}
}
crawler_config_payload = {
    "type": "CrawlerRunConfig",
    "params": {"stream": False, "cache_mode": "bypass"} # 使用枚举的字符串值
}

crawl_payload = {
    "urls": ["链接5"],
    "browser_config": browser_config_payload,
    "crawler_config": crawler_config_payload
}
response = requests.post(
    "http://localhost:11235/crawl", # 更新端口
    # headers={"Authorization": f"Bearer {token}"},  # 如果启用了 JWT
    json=crawl_payload
)
print(f"状态码: {response.status_code}")
if response.ok:
    print(response.json())
else:
    print(f"错误: {response.text}")

```

#### 流式结果

```python
import json
import httpx # 使用 httpx 进行异步流式示例

async def test_stream_crawl(token: str = None): # 使 token 可选
    """测试 /crawl/stream 端点与多个 URL。"""
    url = "http://localhost:11235/crawl/stream" # 更新端口
    payload = {
        "urls": [
            "链接5",
            "链接6",
        ],
        "browser_config": {
            "type": "BrowserConfig",
            "params": {"headless": True, "viewport": {"type": "dict", "value": {"width": 1200, "height": 800}}} # Viewport 需要 type:dict
        },
        "crawler_config": {
            "type": "CrawlerRunConfig",
            "params": {"stream": True, "cache_mode": "bypass"}
        }
    }

    headers = {}
    # if token:
    #    headers = {"Authorization": f"Bearer {token}"} # 如果启用了 JWT

    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, headers=headers, timeout=120.0) as response:
                print(f"状态: {response.status_code} (预期: 200)")
                response.raise_for_status() # 错误状态码引发异常

                # 逐行读取流式响应（NDJSON）
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            # 检查完成标记
                            if data.get("status") == "completed":
                                print("流式完成。")
                                break
                            print(f"流式结果: {json.dumps(data, indent=2)}")
                        except json.JSONDecodeError:
                            print(f"警告: 无法解码 JSON 行: {line}")

    except httpx.HTTPStatusError as e:
         print(f"HTTP 错误发生: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"流式爬取测试错误: {str(e)}")

# 运行此示例：
# import asyncio
# asyncio.run(test_stream_crawl())
```

---

## 指标与监控

通过这些端点监控您的爬取器：

- `/health` - 快速健康检查
- `/metrics` - 详细的 Prometheus 指标
- `/schema` - 完整 API 模式

健康检查示例：
```bash
curl http://localhost:11235/health
```

---

*(部署场景和完整示例部分保持不变，可能更新链接如果示例移动)*

---

## 服务器配置

服务器的行为可以通过 `config.yml` 文件自定义。

### 理解 config.yml

配置文件从容器内的 `/app/config.yml` 加载。默认情况下，仓库中 `deploy/docker/config.yml` 的文件在构建期间被复制到那里。

以下是配置选项的详细分解（使用 `deploy/docker/config.yml` 中的默认值）：

```yaml
# 应用程序配置
app:
  title: "Crawl4AI API"
  version: "1.0.0" # 考虑设置为与库版本匹配，如 "0.5.1"
  host: "0.0.0.0"
  port: 8020 # 注意：此端口仅在直接运行 server.py 时使用。Gunicorn 覆盖此设置（见 supervisord.conf）。
  reload: False # 默认设置为 False - 适合生产
  timeout_keep_alive: 300

# 默认 LLM 配置
llm:
  provider: "openai/gpt-4o-mini"  # 可通过 LLM_PROVIDER 环境变量覆盖
  api_key_env: "OPENAI_API_KEY"
  # api_key: sk-...  # 如果直接传递 API 密钥，则忽略 api_key_env

# Redis 配置（由 supervisord 管理的内部 Redis 服务器使用）
redis:
  host: "localhost"
  port: 6379
  db: 0
  password: ""
  # ... 其他 redis 选项 ...

# 速率限制配置
rate_limiting:
  enabled: True
  default_limit: "1000/minute"
  trusted_proxies: []
  storage_uri: "memory://"  # 如果需要持久/共享限制，使用 "redis://localhost:6379"

# 安全配置
security:
  enabled: false # 安全功能的主开关
  jwt_enabled: false # 启用 JWT 认证（需要 security.enabled=true）
  https_redirect: false # 强制 HTTPS（需要 security.enabled=true）
  trusted_hosts: ["*"] # 允许的主机（生产中使用特定域名）
  headers: # 安全头（如果 security.enabled=true 则应用）
    x_content_type_options: "nosniff"
    x_frame_options: "DENY"
    content_security_policy: "default-src 'self'"
    strict_transport_security: "max-age=63072000; includeSubDomains"

# 爬取器配置
crawler:
  memory_threshold_percent: 95.0
  rate_limiter:
    base_delay: [1.0, 2.0] # 调度器请求间的最小/最大延迟（秒）
  timeouts:
    stream_init: 30.0  # 流初始化的超时
    batch_process: 300.0 # 非流式 /crawl 处理的超时

# 日志配置
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 可观察性配置
observability:
  prometheus:
    enabled: True
    endpoint: "/metrics"
  health_check:
    endpoint: "/health"
```

*(JWT 认证部分保持不变，只需注意请求的默认端口现在是 11235)*

*(配置技巧与最佳实践保持不变)*

### 自定义配置

您可以覆盖默认的 `config.yml`。

#### 方法1：构建前修改

1.  编辑本地仓库克隆中的 `deploy/docker/config.yml` 文件。
2.  使用 `docker buildx` 或 `docker compose --profile local-... up --build` 构建镜像。修改后的文件将被复制到镜像中。

#### 方法2：运行时挂载（推荐用于自定义部署）

1.  在本地创建自定义配置文件，如 `my-custom-config.yml`。确保包含所有必要部分。
2.  运行容器时挂载它：

    *   **使用 `docker run`：**
        ```bash
        # 假设 my-custom-config.yml 在当前目录
        docker run -d -p 11235:11235 \
          --name crawl4ai-custom-config \
          --env-file .llm.env \
          --shm-size=1g \
          -v $(pwd)/my-custom-config.yml:/app/config.yml \
          unclecode/crawl4ai:latest # 或您的特定标签
        ```

    *   **使用 `docker-compose.yml`：** 在服务定义中添加 `volumes` 部分：
        ```yaml
        services:
          crawl4ai-hub-amd64: # 或您选择的服务
            image: unclecode/crawl4ai:latest
            profiles: ["hub-amd64"]
            <<: *base-config
            volumes:
              # 将本地自定义配置挂载覆盖容器中的默认配置
              - ./my-custom-config.yml:/app/config.yml
              # 保留 base-config 中的共享内存卷
              - /dev/shm:/dev/shm
        ```
        *(注意：确保 `my-custom-config.yml` 与 `docker-compose.yml` 在同一目录)*

> 💡 挂载时，您的自定义文件*完全替换*默认文件。确保它是有效且完整的配置。

### 配置建议

1. **安全第一** 🔒
   - 生产环境始终启用安全
   - 使用特定的 trusted_hosts 而非通配符
   - 设置适当的速率限制以保护您的服务器
   - 在启用 HTTPS 重定向前考虑您的环境

2. **资源管理** 💻
   - 根据可用 RAM 调整 memory_threshold_percent
   - 根据内容大小和网络条件设置超时
   - 在多容器设置中使用 Redis 进行速率限制

3. **监控** 📊
   - 如果需要指标，启用 Prometheus
   - 开发环境设置 DEBUG 日志，生产环境设置 INFO
   - 定期健康检查监控至关重要

4. **性能调优** ⚡
   - 从保守的速率限制延迟开始
   - 增加 batch_process 超时以处理大内容
   - 根据初始响应时间调整 stream_init 超时

## 获取帮助

我们在这里帮助您成功使用 Crawl4AI！以下是获取支持的方式：

- 📖 查看我们的[完整文档](链接1)
- 🐛 发现错误？[提交问题](链接2)
- 💬 加入我们的[Discord 社区](https://discord.gg/crawl4ai)
- ⭐ 在 GitHub 上给我们加星以示支持！

## 总结

在本指南中，我们涵盖了开始使用 Crawl4AI 的 Docker 部署所需的一切：
- 构建和运行 Docker 容器
- 配置环境  
- 使用交互式 playground 进行测试
- 使用正确类型进行 API 请求
- 使用 Python SDK
- 利用专用端点进行截图、PDF 和 JavaScript 执行
- 通过模型上下文协议（MCP）连接
- 监控您的部署

新的 playground 界面 `http://localhost:11235/playground` 使测试配置和生成相应的 API 请求 JSON 更加容易。

对于 AI 应用程序开发者，MCP 集成允许像 Claude Code 这样的工具直接访问 Crawl4AI 的功能，无需复杂的 API 处理。

记住，`examples` 文件夹中的示例是您的好帮手 - 它们展示了您可以适应自己需求的真实使用模式。

继续探索，如果需要帮助，请随时联系我们！我们正在一起构建一些令人惊叹的东西。🚀

祝您爬取愉快！🕷️