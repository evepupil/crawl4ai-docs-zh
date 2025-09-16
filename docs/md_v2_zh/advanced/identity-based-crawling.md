# 使用 Crawl4AI 保护您的数字身份

Crawl4AI 让您能够使用**真实的数字身份**浏览和与网络交互，确保您被识别为人类而非误认为机器人。本教程涵盖：

1. **托管浏览器** – 推荐用于持久化配置文件和基于身份爬取的方案。  
2. **魔法模式 (Magic Mode)** – 一种简化的备选方案，用于无需持久化身份的快速自动化。

---

## 1. 托管浏览器：您的数字身份解决方案

**托管浏览器 (Managed Browsers)** 让开发者能够创建和使用**持久化的浏览器配置文件**。这些配置文件存储了本地存储、Cookie 和其他会话数据，让您能以**真实的自己**进行浏览——包括登录状态、偏好设置和 Cookie。

### 主要优势

- **真实的浏览体验**：保留会话数据和浏览器指纹，就像普通用户一样。  
- **轻松配置**：一旦您在选定的数据目录中登录或解决了验证码 (CAPTCHA)，您就可以重新运行爬取任务而无需重复这些步骤。  
- **强大的数据访问能力**：如果您能在自己的浏览器中看到数据，您就可以使用真实身份自动化获取它。

---

以下是对您**托管浏览器**教程的**部分更新**，特别是关于使用 **Playwright 的 Chromium** 二进制文件（而非系统全局的 Chrome/Edge）来**创建用户数据目录**的部分。我们将展示如何**定位**该二进制文件并使用 `--user-data-dir` 参数启动它来设置您的配置文件。然后您可以将 `BrowserConfig.user_data_dir` 指向该文件夹以用于后续爬取。

---

### 创建用户数据目录（通过 Playwright 的命令行方式）

如果您安装了 Crawl4AI（它在底层安装了 Playwright），您的系统上已经有一个由 Playwright 管理的 Chromium。请按照以下步骤从命令行启动该 **Chromium**，并指定一个**自定义**数据目录：

1. **查找** Playwright Chromium 二进制文件：
   - 在大多数系统上，已安装的浏览器位于 `~/.cache/ms-playwright/` 文件夹或类似路径下。  
   - 要查看已安装浏览器的概览，请运行：
     ```bash
     python -m playwright install --dry-run
     ```
     或
     ```bash
     playwright install --dry-run
     ```
     （取决于您的环境）。这将显示 Playwright 存放 Chromium 的位置。

   - 例如，您可能会看到类似这样的路径：
     ```
     ~/.cache/ms-playwright/chromium-1234/chrome-linux/chrome
     ```
     在 Linux 上，或者在 macOS/Windows 上有对应的文件夹。

2. 使用**自定义**用户数据目录**启动** Playwright Chromium 二进制文件：
   ```bash
   # Linux 示例
   ~/.cache/ms-playwright/chromium-1234/chrome-linux/chrome \
       --user-data-dir=/home/<you>/my_chrome_profile
   ```
   ```bash
   # macOS 示例 (Playwright 的内部二进制文件)
   ~/Library/Caches/ms-playwright/chromium-1234/chrome-mac/Chromium.app/Contents/MacOS/Chromium \
       --user-data-dir=/Users/<you>/my_chrome_profile
   ```
   ```powershell
   # Windows 示例 (PowerShell/cmd)
   "C:\Users\<you>\AppData\Local\ms-playwright\chromium-1234\chrome-win\chrome.exe" ^
       --user-data-dir="C:\Users\<you>\my_chrome_profile"
   ```
   
   **请将**路径替换为您 `ms-playwright` 缓存结构中的实际子文件夹。  
   - 这将**打开**一个全新的 Chromium，并使用您新的或现有的数据文件夹。  
   - **登录**任何网站或按您想要的方式配置浏览器。  
   - 完成后**关闭**——您的配置文件数据已保存在该文件夹中。

3. 在 **`BrowserConfig.user_data_dir`** 中使用该文件夹：
   ```python
   from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

   browser_config = BrowserConfig(
       headless=True,
       use_managed_browser=True,
       user_data_dir="/home/<you>/my_chrome_profile",
       browser_type="chromium"
   )
   ```
   - 下次运行代码时，它会重用该文件夹——**保留**您的会话数据、Cookie、本地存储等。

---

## 3. 在 Crawl4AI 中使用托管浏览器

一旦您拥有了包含会话数据的数据目录，将其传递给 **`BrowserConfig`**：

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    # 1) 引用您的持久化数据目录
    browser_config = BrowserConfig(
        headless=True,             # 自动化运行时设为 'True'
        verbose=True,
        use_managed_browser=True,  # 启用持久化浏览器策略
        browser_type="chromium",
        user_data_dir="/path/to/my-chrome-profile"
    )

    # 2) 标准爬取配置
    crawl_config = CrawlerRunConfig(
        wait_for="css:.logged-in-content"
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url="https://example.com/private", config=crawl_config)
        if result.success:
            print("Successfully accessed private data with your identity!")
        else:
            print("Error:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
```

### 工作流程

1. **外部登录**（通过 CLI 或您正常的 Chrome 并使用 `--user-data-dir=...`）。  
2. **关闭**该浏览器。  
3. 在 Crawl4AI 的 `user_data_dir=` 中使用相同的文件夹。  
4. **爬取** – 网站会将您的身份视为刚刚登录的同一用户。

---

## 4. 魔法模式：简化自动化

如果您**不需要**持久化配置文件或基于身份的方法，**魔法模式 (Magic Mode)** 提供了一种快速模拟类人浏览的方式，而无需存储长期数据。

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
        url="https://example.com",
        config=CrawlerRunConfig(
            magic=True,  # 简化大量交互
            remove_overlay_elements=True,
            page_timeout=60000
        )
    )
```

**魔法模式**：

- 模拟类似用户的体验  
- 随机化用户代理和导航器信息
- 随机化交互和时间  
- 掩盖自动化信号  
- 尝试处理弹出窗口  

**但**如果您想要一个完全合法的基于身份的解决方案，它不能替代**真正的**基于用户的会话。

---

## 5. 托管浏览器 vs. 魔法模式 对比

| 特性                     | **托管浏览器**                                           | **魔法模式**                                     |
|--------------------------|--------------------------------------------------------|--------------------------------------------------|
| **会话持久性**           | 在 user_data_dir 中保留完整的 localStorage/cookie      | 无持久化数据（每次运行都是新的）                 |
| **真实身份**             | 具有完整权限和偏好的真实用户配置文件                   | 模拟类用户模式，但没有实际身份                   |
| **复杂网站**             | 最适合需要登录的网站或重度配置                         | 适用于简单任务，几乎不需要登录或配置             |
| **设置**                 | 外部创建 user_data_dir，然后在 Crawl4AI 中使用          | 单行方法 (`magic=True`)                          |
| **可靠性**               | 极其一致（多次运行数据相同）                           | 适用于较小任务，稳定性可能稍差                   |

---

## 6. 使用 BrowserProfiler 类

Crawl4AI 提供了一个专用的 `BrowserProfiler` 类来管理浏览器配置文件，使得为基于身份的浏览创建、列出和删除配置文件变得容易。

### 使用 BrowserProfiler 创建和管理配置文件

`BrowserProfiler` 类提供了一个全面的 API 用于浏览器配置文件管理：

```python
import asyncio
from crawl4ai import BrowserProfiler

async def manage_profiles():
    # 创建一个分析器实例
    profiler = BrowserProfiler()
    
    # 交互式创建配置文件 - 打开一个浏览器窗口
    profile_path = await profiler.create_profile(
        profile_name="my-login-profile"  # 可选：为您的配置文件命名
    )
    
    print(f"Profile saved at: {profile_path}")
    
    # 列出所有可用配置文件
    profiles = profiler.list_profiles()
    
    for profile in profiles:
        print(f"Profile: {profile['name']}")
        print(f"  Path: {profile['path']}")
        print(f"  Created: {profile['created']}")
        print(f"  Browser type: {profile['type']}")
    
    # 按名称获取特定配置文件的路径
    specific_profile = profiler.get_profile_path("my-login-profile")
    
    # 不再需要时删除配置文件
    success = profiler.delete_profile("old-profile-name")
    
asyncio.run(manage_profiles())
```

**配置文件创建的工作原理：**
1.  打开一个浏览器窗口供您交互
2.  您登录网站、设置偏好等
3.  完成后，在终端按 'q' 关闭浏览器
4.  配置文件保存在 Crawl4AI 配置文件目录中
5.  您可以将返回的路径与 `BrowserConfig.user_data_dir` 一起使用

### 交互式配置文件管理

`BrowserProfiler` 还提供了一个交互式管理控制台，指导您完成配置文件的创建、列出和删除：

```python
import asyncio
from crawl4ai import BrowserProfiler, AsyncWebCrawler, BrowserConfig

# 定义一个使用配置文件进行爬取的函数
async def crawl_with_profile(profile_path, url):
    browser_config = BrowserConfig(
        headless=True,
        use_managed_browser=True,
        user_data_dir=profile_path
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url)
        return result

async def main():
    # 创建一个分析器实例
    profiler = BrowserProfiler()
    
    # 启动交互式配置文件管理器
    # 将爬取函数作为回调传递会添加一个“使用配置文件爬取”的选项
    await profiler.interactive_manager(crawl_callback=crawl_with_profile)
    
asyncio.run(main())
```

### 传统方法

为了向后兼容，`ManagedBrowser` 上的旧方法仍然可用，但它们委托给新的 `BrowserProfiler` 类：

```python
from crawl4ai.browser_manager import ManagedBrowser

# 这些方法仍然有效，但在内部使用 BrowserProfiler
profiles = ManagedBrowser.list_profiles()
```

### 完整示例

请参阅 `docs/examples/identity_based_browsing.py` 中的完整示例，以全面演示如何使用新的 `BrowserProfiler` 类创建和使用配置文件进行身份验证浏览。

---

## 7. 区域设置、时区和地理位置控制

除了使用持久化配置文件，Crawl4AI 还支持自定义浏览器的区域设置、时区和地理位置设置。这些功能通过允许您控制网站如何感知您的位置和区域设置，来增强您的基于身份的浏览体验。

### 设置区域设置和时区

您可以通过 `CrawlerRunConfig` 设置浏览器的区域设置和时区：

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
        url="https://example.com",
        config=CrawlerRunConfig(
            # 设置浏览器区域设置（语言和区域格式）
            locale="fr-FR",  # 法语 (法国)
            
            # 设置浏览器时区
            timezone_id="Europe/Paris",
            
            # 其他常规选项...
            magic=True,
            page_timeout=60000
        )
    )
```

**工作原理：**
- `locale` 影响语言偏好、日期格式、数字格式等。
- `timezone_id` 影响 JavaScript 的 Date 对象和与时间相关的功能
- 这些设置会在创建浏览器上下文时应用，并在整个会话期间保持

### 配置地理位置

控制浏览器地理位置 API 报告的 GPS 坐标：

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, GeolocationConfig

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
        url="https://maps.google.com",  # 或任何具有位置感知的网站
        config=CrawlerRunConfig(
            # 配置精确的 GPS 坐标
            geolocation=GeolocationConfig(
                latitude=48.8566,   # 巴黎坐标
                longitude=2.3522,
                accuracy=100        # 精度（米）（可选）
            ),
            
            # 该网站会将您视为在巴黎
            page_timeout=60000
        )
    )
```

**重要说明：**
- 当指定 `geolocation` 时，浏览器会自动被授予访问位置的权限
- 使用 Geolocation API 的网站将收到您指定的确切坐标
- 这会影响地图服务、商店定位器、送货服务等
- 结合适当的 `locale` 和 `timezone_id`，您可以创建一个完全一致的位置配置文件

### 与托管浏览器结合使用

这些设置与托管浏览器完美配合，提供完整的身份解决方案：

```python
from crawl4ai import (
    AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, 
    GeolocationConfig
)

browser_config = BrowserConfig(
    use_managed_browser=True,
    user_data_dir="/path/to/my-profile",
    browser_type="chromium"
)

crawl_config = CrawlerRunConfig(
    # 位置设置
    locale="es-MX",                  # 西班牙语 (墨西哥)
    timezone_id="America/Mexico_City",
    geolocation=GeolocationConfig(
        latitude=19.4326,            # 墨西哥城
        longitude=-99.1332
    )
)

async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(url="https://example.com", config=crawl_config)
```

将持久化配置文件与精确的地理位置和区域设置相结合，让您可以完全控制您的数字身份。

## 8. 总结

- **创建**您的用户数据目录，可以通过：
  - 外部使用 `--user-data-dir=/some/path` 启动 Chrome/Chromium
  - 或使用内置的 `BrowserProfiler.create_profile()` 方法
  - 或通过 `profiler.interactive_manager()` 的交互式界面
- **登录**或根据需要配置网站，然后关闭浏览器
- 在 `BrowserConfig(user_data_dir="...")` + `use_managed_browser=True` 中**引用**该文件夹
- 使用 `locale`、`timezone_id` 和 `geolocation` **自定义**身份各方面
- 使用 `BrowserProfiler.list_profiles()` **列出和重用**配置文件
- 使用专用的 `BrowserProfiler` 类**管理**您的配置文件
- 享受反映您真实身份的**持久化**会话
- 如果只需要快速的、临时性的自动化，**魔法模式**可能就足够了

**推荐**：对于稳健的、基于身份的爬取以及与复杂网站的简化交互，应始终优先选择**托管浏览器**。对于不需要持久化数据的快速任务或原型，使用**魔法模式**。

通过这些方法，您可以保留**真实的**浏览环境，确保网站将您完全视为普通用户——无需重复登录或浪费时间。