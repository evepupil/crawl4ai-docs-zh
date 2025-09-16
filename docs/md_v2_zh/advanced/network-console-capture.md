# 网络请求与控制台消息捕获

Crawl4AI 可以在爬取过程中捕获所有网络请求和浏览器控制台消息，这对于调试、安全分析或理解页面行为非常宝贵。

## 配置

要启用网络和控制台捕获功能，请使用以下配置选项：

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

# 启用网络请求捕获和控制台消息捕获
config = CrawlerRunConfig(
    capture_network_requests=True,  # 捕获所有网络请求和响应
    capture_console_messages=True   # 捕获所有浏览器控制台输出
)
```

## 使用示例

```python
import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def main():
    # 启用网络请求捕获和控制台消息捕获
    config = CrawlerRunConfig(
        capture_network_requests=True,
        capture_console_messages=True
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://example.com",
            config=config
        )
        
        if result.success:
            # 分析网络请求
            if result.network_requests:
                print(f"Captured {len(result.network_requests)} network events")
                
                # 统计请求类型
                request_count = len([r for r in result.network_requests if r.get("event_type") == "request"])
                response_count = len([r for r in result.network_requests if r.get("event_type") == "response"])
                failed_count = len([r for r in result.network_requests if r.get("event_type") == "request_failed"])
                
                print(f"Requests: {request_count}, Responses: {response_count}, Failed: {failed_count}")
                
                # 查找API调用
                api_calls = [r for r in result.network_requests 
                            if r.get("event_type") == "request" and "api" in r.get("url", "")]
                if api_calls:
                    print(f"Detected {len(api_calls)} API calls:")
                    for call in api_calls[:3]:  # 显示前3个
                        print(f"  - {call.get('method')} {call.get('url')}")
            
            # 分析控制台消息
            if result.console_messages:
                print(f"Captured {len(result.console_messages)} console messages")
                
                # 按类型分组
                message_types = {}
                for msg in result.console_messages:
                    msg_type = msg.get("type", "unknown")
                    message_types[msg_type] = message_types.get(msg_type, 0) + 1
                
                print("Message types:", message_types)
                
                # 显示错误（通常最重要）
                errors = [msg for msg in result.console_messages if msg.get("type") == "error"]
                if errors:
                    print(f"Found {len(errors)} console errors:")
                    for err in errors[:2]:  # 显示前2个
                        print(f"  - {err.get('text', '')[:100]}")
            
            # 将所有捕获的数据导出到文件进行详细分析
            with open("network_capture.json", "w") as f:
                json.dump({
                    "url": result.url,
                    "network_requests": result.network_requests or [],
                    "console_messages": result.console_messages or []
                }, f, indent=2)
            
            print("Exported detailed capture data to network_capture.json")

if __name__ == "__main__":
    asyncio.run(main())
```

## 捕获的数据结构

### 网络请求

`result.network_requests` 包含一个字典列表，每个字典代表一个网络事件，包含以下常见字段：

| 字段 | 描述 |
|-------|-------------|
| `event_type` | 事件类型：`"request"`、`"response"` 或 `"request_failed"` |
| `url` | 请求的URL |
| `timestamp` | 事件捕获时的Unix时间戳 |

#### 请求事件字段

```json
{
  "event_type": "request",
  "url": "https://example.com/api/data.json",
  "method": "GET",
  "headers": {"User-Agent": "...", "Accept": "..."},
  "post_data": "key=value&otherkey=value",
  "resource_type": "fetch",
  "is_navigation_request": false,
  "timestamp": 1633456789.123
}
```

#### 响应事件字段

```json
{
  "event_type": "response",
  "url": "https://example.com/api/data.json",
  "status": 200,
  "status_text": "OK",
  "headers": {"Content-Type": "application/json", "Cache-Control": "..."},
  "from_service_worker": false,
  "request_timing": {"requestTime": 极客时间, "receiveHeadersEnd": 1234.78},
  "timestamp": 1633456789.456
}
```

#### 失败请求事件字段

```json
{
  "极客时间": "request_failed",
  "url": "https://example.com/missing.png",
  "method": "GET",
  "resource_type": "image",
  "failure_text": "net::ERR_ABORTED 404",
  "timestamp": 1633456789.789
}
```

### 控制台消息

`result.console_messages` 包含一个字典列表，每个字典代表一个控制台消息，包含以下常见字段：

| 字段 | 描述 |
|-------|-------------|
| `type` | 消息类型：`"log"`、`"error"`、`"warning"`、`"info"` 等 |
| `text` | 消息文本 |
| `timestamp` | 消息捕获时的Unix时间戳 |

#### 控制台消息示例

```json
{
  "type": "error",
  "text": "Uncaught TypeError: Cannot read property 'length' of undefined",
  "location": "https://example.com/script.js:123:45",
  "timestamp": 1633456790.123
}
```

## 主要优势

- **完整的请求可见性**：捕获所有网络活动，包括：
  - 请求（URL、方法、头部、提交数据）
  - 响应（状态码、头部、时间信息）
  - 失败的请求（含错误消息）
  
- **控制台消息访问**：查看所有JavaScript控制台输出：
  - 日志消息
  - 警告
  - 带堆栈跟踪的错误
  - 开发者调试信息

- **强大的调试能力**：识别问题，如：
  - 失败的API调用或资源加载
  - 影响页面功能的JavaScript错误
  - CORS或其他安全问题
  - 隐藏的API端点和数据流

- **安全分析**：检测：
  - 意外的第三方请求
  - 请求负载中的数据泄漏
  - 可疑的脚本行为

- **性能洞察**：分析：
  - 请求时间数据
  - 资源加载模式
  - 潜在瓶颈

## 使用场景

1. **API发现**：识别单页应用中的隐藏端点和数据流
2. **调试**：追踪影响页面功能的JavaScript错误
3. **安全审计**：检测不需要的第三方请求或数据泄漏
4. **性能分析**：识别加载缓慢的资源
5. **广告/追踪器分析**：检测和分类广告或追踪调用

此功能对于复杂的JavaScript密集型网站、单页应用程序，或者当您需要了解浏览器与服务器之间的确切通信时特别有价值。