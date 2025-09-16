# `SSLCertificate` 参考文档

**`SSLCertificate`** 类封装了SSL证书数据，并允许以多种格式（PEM、DER、JSON或文本）导出。当你在**`CrawlerRunConfig`**中设置**`fetch_ssl_certificate=True`**时，**Crawl4AI**会使用它。

## 1. 概述

**位置**: `crawl4ai/ssl_certificate.py`

```python
class SSLCertificate:
    """
    表示SSL证书，并提供多种导出格式的方法。

    主要方法:
    - from_url(url, timeout=10)
    - from_file(file_path)
    - from_binary(binary_data)
    - to_json(filepath=None)
    - to_pem(filepath=None)
    - to_der(filepath=None)
    ...

    常用属性:
    - issuer
    - subject
    - valid_from
    - valid_until
    - fingerprint
    """
```

### 典型用例
1. 在爬取时**启用**证书获取：
   ```python
   CrawlerRunConfig(fetch_ssl_certificate=True, ...)
   ```
2. 执行`arun()`后，如果`result.ssl_certificate`存在，则它是**`SSLCertificate`**的实例。  
3. 你可以**读取**基本属性（颁发者、主体、有效期）或**导出**为多种格式。

---

## 2. 构造与获取

### 2.1 **`from_url(url, timeout=10)`**
从给定URL（端口443）手动加载SSL证书。通常内部使用，但也可以直接调用：

```python
cert = SSLCertificate.from_url("https://example.com")
if cert:
    print("指纹:", cert.fingerprint)
```

### 2.2 **`from_file(file_path)`**
从包含ASN.1或DER格式证书数据的文件加载。除非有本地证书文件，否则很少使用：

```python
cert = SSLCertificate.from_file("/path/to/cert.der")
```

### 2.3 **`from_binary(binary_data)`**
从原始二进制数据初始化。例如，如果从套接字或其他来源捕获：

```python
cert = SSLCertificate.from_binary(raw_bytes)
```

---

## 3. 常用属性

获取**`SSLCertificate`**实例（例如从爬取结果`result.ssl_certificate`）后，可以读取：

1. **`issuer`** *(dict)*  
   - 例如 `{"CN": "My Root CA", "O": "..."}`
2. **`subject`** *(dict)*  
   - 例如 `{"CN": "example.com", "O": "ExampleOrg"}`
3. **`valid_from`** *(str)*  
   - NotBefore日期/时间。通常为ASN.1/UTC格式。
4. **`valid_until`** *(str)*  
   - NotAfter日期/时间。
5. **`fingerprint`** *(str)*  
   - SHA-256摘要（小写十六进制）。  
   - 例如 `"d14d2e..."`

---

## 4. 导出方法

获取**`SSLCertificate`**对象后，可以**导出**或**检查**：

### 4.1 **`to_json(filepath=None)` → `Optional[str]`**
- 返回包含解析后证书字段的JSON字符串。  
- 如果提供`filepath`，则保存到磁盘并返回`None`。

**用法**:
```python
json_data = cert.to_json()  # 返回JSON字符串
cert.to_json("certificate.json")  # 写入文件，返回None
```

### 4.2 **`to_pem(filepath=None)` → `Optional[str]`**
- 返回PEM编码字符串（常用于Web服务器）。  
- 如果提供`filepath`，则保存到磁盘。

```python
pem_str = cert.to_pem()              # 内存中的PEM字符串
cert.to_pem("/path/to/cert.pem")     # 保存到文件
```

### 4.3 **`to_der(filepath=None)` → `Optional[bytes]`**
- 返回原始DER（二进制ASN.1）字节。  
- 如果指定`filepath`，则将字节写入该文件。

```python
der_bytes = cert.to_der()
cert.to_der("certificate.der")
```

### 4.4 (可选) **`export_as_text()`**
- 如果存在类似`export_as_text()`的方法，通常返回OpenSSL风格的文本表示。  
- 不常用，但可用于调试或手动检查。

---

## 5. 在Crawl4AI中的示例用法

以下是一个简单示例，展示爬虫如何从网站获取SSL证书并读取或导出。代码片段：

```python
import asyncio
import os
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

async def main():
    tmp_dir = "tmp"
    os.makedirs(tmp_dir, exist_ok=True)

    config = CrawlerRunConfig(
        fetch_ssl_certificate=True,
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com", config=config)
        if result.success and result.ssl_certificate:
            cert = result.ssl_certificate
            # 1. 基本信息
            print("颁发者CN:", cert.issuer.get("CN", ""))
            print("有效期至:", cert.valid_until)
            print("指纹:", cert.fingerprint)
            
            # 2. 导出
            cert.to_json(os.path.join(tmp_dir, "certificate.json"))
            cert.to_pem(os.path.join(tmp_dir, "certificate.pem"))
            cert.to_der(os.path.join(tmp_dir, "certificate.der"))
    
if __name__ == "__main__":
    asyncio.run(main())
```

---

## 6. 注意事项与最佳实践

1. **超时**: `SSLCertificate.from_url`内部默认使用**10秒**的套接字连接并封装SSL。  
2. **二进制形式**: 证书以ASN.1（DER）形式加载，然后由`OpenSSL.crypto`重新解析。  
3. **验证**: 此操作**不**验证证书链或信任存储。仅获取和解析。  
4. **集成**: 在Crawl4AI中，通常只需在`CrawlerRunConfig`中设置`fetch_ssl_certificate=True`；最终结果的`ssl_certificate`会自动构建。  
5. **导出**: 如果需要存储或分析证书，`to_json`和`to_pem`非常通用。

---

### 总结

- **`SSLCertificate`** 是一个便捷类，用于捕获和导出爬取站点的**TLS证书**。  
- 常见用法是通过设置`fetch_ssl_certificate=True`后访问**`CrawlResult.ssl_certificate`**字段。  
- 提供快速访问证书关键信息（`issuer`、`subject`、`fingerprint`）的功能，并易于导出（PEM、DER、JSON）以进行进一步分析或服务器使用。

当你需要**了解**站点的证书或需要进行加密或合规性检查时使用它。