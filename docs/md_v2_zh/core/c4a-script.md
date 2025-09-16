# C4A-Script：简化可视化网页自动化

## 什么是 C4A-Script？

C4A-Script 是一种功能强大、人类可读的领域特定语言（DSL），专为网页自动化和交互而设计。可以将其视为一种简化的编程语言，任何人都可以阅读和编写，非常适合自动化重复性网页任务、测试用户界面或创建交互式演示。

### 为什么选择 C4A-Script？

**语法简单，效果强大**
```c4a
# 使用通俗英语导航和交互
GO https://example.com
WAIT `#search-box` 5
TYPE "Hello World"
CLICK `button[type="submit"]`
```

**可视化编程支持**
C4A-Script 内置 Blockly 可视化编辑器，允许您通过拖放块来创建脚本 - 无需编码经验！

**完美适用于：**
- **UI 测试**：自动化用户交互流程
- **演示创建**：构建交互式产品演示
- **数据录入**：自动化表单填写和提交
- **测试工作流**：验证复杂的用户旅程
- **培训**：无需代码复杂性即可教授网页自动化

## 入门指南：您的第一个脚本

让我们创建一个在网站上搜索内容的简单脚本：

```c4a
# 我的第一个 C4A-Script
GO https://duckduckgo.com

# 等待搜索框出现
WAIT `input[name="q"]` 10

# 输入搜索查询
TYPE "Crawl4AI"

# 按 Enter 键搜索
PRESS Enter

# 等待结果
WAIT `.results` 5
```

就是这样！只需几行代码，您就自动化了一个完整的搜索工作流。

## 交互式教程和实时演示

想通过实践学习吗？我们为您准备好了：

**🚀 [实时演示](https://docs.crawl4ai.com/apps/c4a-script/)** - 立即在浏览器中尝试 C4A-Script！

**📁 [教程示例](https://github.com/unclecode/crawl4ai/blob/main/docs/examples/c4a_script/)** - 包含源代码的完整示例

### 本地运行教程

该教程包含一个基于 Flask 的 Web 界面，具有：
- **实时代码编辑器**，支持语法高亮
- **可视化 Blockly 编辑器**，用于拖放式编程
- **录制模式**，用于捕获您的操作并生成脚本
- **时间轴视图**，用于查看和编辑自动化步骤

```bash
# 克隆并导航到教程
cd docs/examples/c4a_script/tutorial/

# 安装依赖
pip install flask

# 启动教程服务器
python app.py

# 在浏览器中打开 http://localhost:5000
```

## 核心概念

### 命令和语法

C4A-Script 使用简单的、类似英语的命令。每个命令执行一个特定操作：

```c4a
# 注释以 # 开头
COMMAND parameter1 parameter2

# 大多数命令使用反引号中的 CSS 选择器
CLICK `#submit-button`

# 文本内容放在引号中
TYPE "Hello, World!"

# 数字直接使用
WAIT 3
```

### 选择器：查找元素

C4A-Script 使用 CSS 选择器来识别页面上的元素：

```c4a
# 按 ID
CLICK `#login-button`

# 按类
CLICK `.submit-btn`

# 按属性
CLICK `button[type="submit"]`

# 按文本内容
CLICK `button:contains("Sign In")`

# 复杂选择器
CLICK `.form-container input[name="email"]`
```

### 变量和动态内容

使用变量存储和重用值：

```c4a
# 设置变量
SETVAR username = "john@example.com"
SETVAR password = "secret123"

# 使用变量（前缀为 $）
TYPE $username
PRESS Tab
TYPE $password
```

## 命令类别

### 🧭 导航命令
像用户一样在网页上移动：

| 命令 | 用途 | 示例 |
|---------|---------|---------|
| `GO` | 导航到 URL | `GO https://example.com` |
| `RELOAD` | 刷新当前页面 | `RELOAD` |
| `BACK` | 后退历史记录 | `BACK` |
| `FORWARD` | 前进历史记录 | `FORWARD` |

### ⏱️ 等待命令
确保元素在交互前准备就绪：

| 命令 | 用途 | 示例 |
|---------|---------|---------|
| `WAIT` | 等待时间/元素/文本 | `WAIT 3` 或 `WAIT \`#element\` 10` |

### 🖱️ 鼠标命令
像人类一样点击、拖拽和移动：

| 命令 | 用途 | 示例 |
|---------|---------|---------|
| `CLICK` | 点击元素或坐标 | `CLICK \`button\`` 或 `CLICK 100 200` |
| `DOUBLE_CLICK` | 双击元素 | `DOUBLE_CLICK \`.item\`` |
| `RIGHT_CLICK` | 右键点击元素 | `RIGHT_CLICK \`#menu\`` |
| `SCROLL` | 按方向滚动 | `SCROLL DOWN 500` |
| `DRAG` | 从一点拖拽到另一点 | `DRAG 100 100 500 300` |

### ⌨️ 键盘命令
自然地输入文本和按键：

| 命令 | 用途 | 示例 |
|---------|---------|---------|
| `TYPE` | 输入文本或变量 | `TYPE "Hello"` 或 `TYPE $username` |
| `PRESS` | 按下特殊键 | `PRESS Tab` 或 `PRESS Enter` |
| `CLEAR` | 清除输入字段 | `CLEAR \`#search\`` |
| `SET` | 直接设置输入值 | `SET \`#email\` "user@example.com"` |

### 🔀 控制流
为脚本添加逻辑和重复：

| 命令 | 用途 | 示例 |
|---------|---------|---------|
| `IF` | 条件执行 | `IF (EXISTS \`#popup\`) THEN CLICK \`#close\`` |
| `REPEAT` | 循环命令 | `REPEAT (SCROLL DOWN 300, 5)` |

### 💾 变量和高级功能
存储数据并执行自定义代码：

| 命令 | 用途 | 示例 |
|---------|---------|---------|
| `SETVAR` | 创建变量 | `SETVAR email = "test@example.com"` |
| `EVAL` | 执行 JavaScript | `EVAL \`console.log('Hello')\`` |

## 实际示例

### 示例 1：登录流程
```c4a
# 完整的登录自动化
GO https://myapp.com/login

# 等待页面加载
WAIT `#login-form` 5

# 填写凭据
CLICK `#email`
TYPE "user@example.com"
PRESS Tab
TYPE "mypassword"

# 提交表单
CLICK `button[type="submit"]`

# 等待仪表板
WAIT `.dashboard` 10
```

### 示例 2：电子商务购物
```c4a
# 使用变量的购物自动化
SETVAR product = "laptop"
SETVAR budget = "1000"

GO https://shop.example.com
WAIT `#search-box` 3

# 搜索产品
TYPE $product
PRESS Enter
WAIT `.product-list` 5

# 按价格筛选
CLICK `.price-filter`
SET `#max-price` $budget
CLICK `.apply-filters`

# 选择第一个结果
WAIT `.product-item` 3
CLICK `.product-item:first-child`
```

### 示例 3：带条件的表单自动化
```c4a
# 具有错误处理的智能表单填写
GO https://forms.example.com

# 检查用户是否已登录
IF (EXISTS `.user-menu`) THEN GO https://forms.example.com/new
IF (NOT EXISTS `.user-menu`) THEN CLICK `#login-link`

# 填写表单
WAIT `#contact-form` 5
SET `#name` "John Doe"
SET `#email` "john@example.com"
SET `#message` "Hello from C4A-Script!"

# 如果出现弹出窗口则处理
IF (EXISTS `.cookie-banner`) THEN CLICK `.accept-cookies`

# 提交
CLICK `#submit-button`
WAIT `.success-message` 10
```

## 使用 Blockly 进行可视化编程

C4A-Script 包含一个基于 Google Blockly 的强大可视化编程界面。完美适用于：

- **非程序员**想要创建自动化
- **快速原型设计**自动化工作流
- **教育环境**教授自动化概念
- **协作开发**，其中可视化表示有助于沟通

### 特性：
- **拖放界面**：通过连接块构建脚本
- **实时同步**：可视化模式中的更改立即更新文本脚本
- **智能块类型**：块按功能分类（导航、操作等）
- **错误预防**：可视化连接防止语法错误
- **注释支持**：添加可视化注释块以进行文档记录

在我们的[实时演示](https://docs.crawl4ai.com/c4a-script/demo)或[本地教程](/examples/c4a_script/tutorial/)中尝试可视化编辑器。

## 高级功能

### 录制模式
教程界面包含录制功能，可监视您的浏览器交互并自动生成 C4A-Script 命令：

1. 在教程界面中点击“录制”
2. 在浏览器预览中执行操作
3. 实时观察 C4A-Script 命令的生成
4. 编辑和优化生成的脚本

### 错误处理和调试
C4A-Script 提供清晰的错误消息和调试信息：

```c4a
# 使用注释进行调试
# 这将等待元素最多 10 秒
WAIT `#slow-loading-element` 10

# 点击前检查元素是否存在
IF (EXISTS `#optional-button`) THEN CLICK `#optional-button`

# 使用 EVAL 进行自定义调试
EVAL `console.log("Current page title:", document.title)`
```

### 与 Crawl4AI 集成
C4A-Script 与 Crawl4AI 的网页爬取能力无缝集成：

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

# 在爬取前使用 C4A-Script 进行交互
script = """
GO https://example.com
CLICK `#load-more-content`
WAIT `.dynamic-content` 5
"""

config = CrawlerRunConfig(
    js_code=script,
    wait_for=".dynamic-content"
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun("https://example.com", config=config)
    print(result.markdown)
```

## 最佳实践

### 1. 始终等待元素
```c4a
# 不好：立即点击
CLICK `#button`

# 好：等待元素出现
WAIT `#button` 5
CLICK `#button`
```

### 2. 使用描述性注释
```c4a
# 登录用户账户
GO https://myapp.com/login
WAIT `#login-form` 5

# 输入凭据
TYPE "user@example.com"
PRESS Tab
TYPE "password123"

# 提交并等待重定向
CLICK `#submit-button`
WAIT `.dashboard` 10
```

### 3. 处理变量条件
```c4a
# 处理不同的页面状态
IF (EXISTS `.cookie-banner`) THEN CLICK `.accept-cookies`
IF (EXISTS `.popup-modal`) THEN CLICK `.close-modal`

# 继续主工作流
CLICK `#main-action`
```

### 4. 使用变量提高可重用性
```c4a
# 定义一次，随处使用
SETVAR base_url = "https://myapp.com"
SETVAR test_email = "test@example.com"

GO $base_url/login
SET `#email` $test_email
```

## 获取帮助

- **📖 [完整示例](/examples/c4a_script/)** - 真实世界的自动化脚本
- **🎮 [交互式教程](/examples/c4a_script/tutorial/)** - 动手学习环境
- **📋 [API 参考](/api/c4a-script-reference/)** - 详细的命令文档
- **🌐 [实时演示](https://docs.crawl4ai.com/c4a-script/demo)** - 在浏览器中尝试

## 下一步是什么？

准备好深入探索了吗？请查看：

1. **[API 参考](/api/c4a-script-reference/)** - 完整的命令文档
2. **[教程示例](/examples/c4a_script/)** - 可复制粘贴的现成脚本
3. **[本地教程设置](/examples/c4a_script/tutorial/)** - 运行完整的开发环境

C4A-Script 使网页自动化对每个人都可访问。无论您是自动化测试的开发人员、创建交互式演示的设计师，还是简化重复性任务的业务用户，C4A-Script 都拥有您所需的工具。

*立即开始自动化 - 未来的您会感谢自己！* 🚀