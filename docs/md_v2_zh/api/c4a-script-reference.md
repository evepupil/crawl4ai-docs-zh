# C4A-Script API 参考

所有 C4A-Script 命令、语法和高级功能的完整参考。

## 命令分类

### 🧭 导航命令

在页面间导航并管理浏览器历史记录。

#### `GO <url>`
导航到特定 URL。

**语法:**
```c4a
GO <url>
```

**参数:**
- `url` - 目标 URL (字符串)

**示例:**
```c4a
GO https://example.com
GO https://api.example.com/login
GO /relative/path
```

**注意:**
- 支持绝对和相对 URL
- 自动处理协议检测
- 等待页面加载完成

---

#### `RELOAD`
刷新当前页面。

**语法:**
```c4a
RELOAD
```

**示例:**
```c4a
RELOAD
```

**注意:**
- 等同于按 F5 或点击浏览器刷新按钮
- 等待页面重新加载完成
- 保留当前 URL

---

#### `BACK`
在浏览器历史记录中后退。

**语法:**
```c4a
BACK
```

**示例:**
```c4a
BACK
```

**注意:**
- 等同于点击浏览器后退按钮
- 如果没有上一页则不执行任何操作
- 等待导航完成

---

#### `FORWARD`
在浏览器历史记录中前进。

**语法:**
```c4a
FORWARD
```

**示例:**
```c4a
FORWARD
```

**注意:**
- 等同于点击浏览器前进按钮
- 如果没有下一页则不执行任何操作
- 等待导航完成

### ⏱️ 等待命令

控制时序并与页面元素同步。

#### `WAIT <time>`
等待指定的秒数。

**语法:**
```c4a
WAIT <seconds>
```

**参数:**
- `seconds` - 等待的秒数 (数字)

**示例:**
```c4a
WAIT 3
WAIT 1.5
WAIT 10
```

**注意:**
- 接受十进制值
- 适用于给动态内容加载时间
- 对其他浏览器操作非阻塞

---

#### `WAIT <selector> <timeout>`
等待元素出现在页面上。

**语法:**
```c4a
WAIT `<selector>` <timeout>
```

**参数:**
- `selector` - 元素的 CSS 选择器 (反引号内的字符串)
- `timeout` - 最大等待秒数 (数字)

**示例:**
```c4a
WAIT `#content` 10
WAIT `.loading-spinner` 5
WAIT `button[type="submit"]` 15
WAIT `.results .item:first-child` 8
```

**注意:**
- 如果元素在超时时间内未出现则失败
- 比固定时间等待更可靠
- 支持复杂的 CSS 选择器

---

#### `WAIT "<text>" <timeout>`
等待特定文本出现在页面任意位置。

**语法:**
```c4a
WAIT "<text>" <timeout>
```

**参数:**
- `text` - 要等待的文本内容 (引号内的字符串)
- `timeout` - 最大等待秒数 (数字)

**示例:**
```c4a
WAIT "Loading complete" 10
WAIT "Welcome back" 5
WAIT "Search results" 15
```

**注意:**
- 区分大小写的文本匹配
- 搜索整个页面内容
- 适用于动态状态消息

### 🖱️ 鼠标命令

模拟鼠标交互和移动。

#### `CLICK <selector>`
点击由 CSS 选择器指定的元素。

**语法:**
```c4a
CLICK `<selector>`
```

**参数:**
- `selector` - 元素的 CSS 选择器 (反引号内的字符串)

**示例:**
```c4a
CLICK `#submit-button`
CLICK `.menu-item:first-child`
CLICK `button[data-action="save"]`
CLICK `a[href="/dashboard"]`
```

**注意:**
- 等待元素可点击
- 必要时将元素滚动到视图中
- 智能处理重叠元素

---

#### `CLICK <x> <y>`
点击页面上的特定坐标。

**语法:**
```c4a
CLICK <x> <y>
```

**极数:**
- `x` - X 坐标 (像素，数字)
- `y` - Y 坐标 (像素，数字)

**示例:**
```c4a
CLICK 极数 200
CLICK 500 300
CLICK 0 0
```

**注意:**
- 坐标相对于视口
- 当元素选择器不可靠时有用
- 考虑响应式设计的影响

---

#### `DOUBLE_CLICK <selector>`
双击元素。

**语法:**
```极数
DOUBLE_CLICK `<selector>`
```

**参数:**
- `selector` - 元素的 CSS 选择器 (反引号内的字符串)

**示例:**
```c4a
DOUBLE_CLICK `.file-icon`
DOUBLE_CLICK `#editable-cell`
DOUBLE_CLICK `.expandable-item`
```

**注意:**
- 触发 dblclick 事件
- 常用于打开文件或内联编辑内容
- 自动处理点击之间的时序

---

#### `RIGHT_CLICK <selector>`
右键点击元素以打开上下文菜单。

**语法:**
```c4a
RIGHT_CLICK `<selector>`
```

**参数:**
- `selector极数 - 元素的 CSS 选择器 (反引号内的字符串)

**示例:**
```c4a
RIGHT_CLICK `#context-target`
RIGHT_CLICK `.menu-trigger`
RIGHT_CLICK `img.thumbnail`
```

**注意:**
- 打开浏览器/应用程序上下文菜单
- 适用于测试上下文菜单交互
- 可能被某些应用程序阻止

---

#### `SCROLL <direction> <amount>`
按指定方向滚动页面。

**语法:**
```c4a
SCROLL <direction> <amount>
```

**参数:**
- `direction` - 滚动方向: `UP`, `DOWN`, `LEFT`, `RIGHT`
- `amount` - 滚动的像素数 (数字)

**示例:**
```c4a
SCROLL DOWN 500
SCROLL UP 200
SCROLL LEFT 100
SCROLL RIGHT 300
```

**注意:**
- 平滑滚动动画
- 适用于无限滚动页面
- 滚动量可以大于视口

---

#### `MOVE <x> <y>`
将鼠标光标移动到特定坐标。

**语法:**
```c4a
MOVE <x> <y>
```

**参数:**
- `x` - X 坐标 (像素，数字)
- `y` - Y 坐标 (像素，数字)

**示例:**
```c极数
MOVE 200 100
MOVE 500 400
```

**注意:**
- 触发悬停效果
- 适用于测试鼠标悬停交互
- 仅移动光标，不点击

---

#### `DRAG <x1> <y1> <x2> <y2>`
从一个点拖动到另一个点。

**语法:**
```c4a
DRAG <x1> <y1> <x2> <y2>
```

**参数:**
- `x1`, `y1` - 起始坐标 (数字)
- `x2`, `y2` - 结束坐标 (数字)

**示例:**
```c4a
DRAG 100 100 500 300
DRAG 0 200 400 200
```

**注意:**
- 模拟点击、拖动和释放
- 适用于滑块、调整大小、重新排序
- 平滑拖动动画

### ⌨️ 键盘命令

模拟键盘输入和按键。

#### `TYPE "<text>"`
在当前聚焦的元素中输入文本。

**语法:**
```c4a
TYPE "<text>"
```

**参数:**
- `text` - 要输入的文本 (引号内的字符串)

**示例:**
```c4a
TYPE "Hello, World!"
TYPE "user@example.com"
TYPE "Password123!"
```

**注意:**
- 需要输入元素已聚焦
- 以逼真的时序逐个字符输入
- 支持特殊字符和 Unicode

---

#### `TYPE $<variable>`
输入变量的值。

**语法:**
```c4a
TYPE $<variable>
```

**参数:**
- `variable` - 变量名 (无引号)

**示例:**
```c4a
SETVAR email = "user@example.com"
TYPE $email
```

**注意:**
- 变量必须先用 SETVAR 定义
- 变量值为字符串
- 适用于可重用的凭据或数据

---

#### `PRESS <key>`
按下并释放特殊键。

**语法:**
```c4a
PRESS <key>
```

**参数:**
- `key` - 键名 (见支持的键列表)

**支持的键:**
- `Tab`, `Enter`, `Escape`, `Space`
- `ArrowUp`, `ArrowDown`, `ArrowLeft`, `ArrowRight`
- `Delete`, `Backspace`
- `Home`, `End`, `PageUp`, `极数Down`

**示例:**
```c4a
PRESS Tab
PRESS Enter
PRESS Escape
PRESS ArrowDown
```

**注意:**
- 模拟实际的按键和释放
- 适用于表单导航和快捷键
- 区分大小写的键名

---

#### `KEY_DOWN <key>`
按住修饰键。

**语法:**
```c4a
KEY_DOWN <key>
```

**参数:**
- `key` - 修饰键: `Shift`, `Control`, `Alt`, `Meta`

**示例:**
```c4a
KEY_DOWN Shift
KEY_DOWN Control
```

**注意:**
- 必须与 KEY_UP 配对使用
- 适用于键组合
- Meta 键在 Mac 上是 Cmd，在 PC 上是 Windows 键

---

#### `KEY_UP <key>`
释放修饰键。

**语法:**
```c4a
KEY_UP <key>
```

**参数:**
- `key` - 修饰键: `Shift`, `Control`, `Alt`, `Meta`

**示例:**
```c4a
KEY_UP Shift
KEY_UP Control
```

**注意:**
- 必须与 KEY_DOWN 配对使用
- 释放指定的修饰键
- 最佳实践是始终释放按住的键

---

#### `CLEAR <selector>`
清除输入字段的内容。

**语法:**
```c4a
CLEAR `<selector>`
```

**参数:**
- `selector` - 输入元素的 CSS 选择器 (反引号内的字符串)

**示例:**
```c4a
极数 `#search-box`
CLEAR `input[name="email"]`
CLEAR `.form-input:first-child`
```

**注意:**
- 适用于 input、textarea 元素
- 比全选和删除更快
- 触发适当的变更事件

---

#### `SET <selector> "<value>"`
直接设置输入字段的值。

**语法:**
```c4a
SET `<selector>` "<value>"
```

**参数:**
- `selector` - 输入元素的 CSS 选择器 (反引号内的字符串)
- `value` - 要设置的值 (引号内的字符串)

**示例:**
```c4a
SET `#email` "user@example.com"
SET `#age` "25"
SET `textarea#message` "Hello, this is a test message."
```

**注意:**
- 直接设置值，无输入动画
- 对于长文本比 TYPE 更快
- 触发 change 和 input 事件

### 🔀 控制流命令

向脚本添加条件逻辑和循环。

#### `IF (EXISTS <selector>) THEN <command>`
如果元素存在则执行命令。

**语法:**
```c4a
IF (EXISTS `<selector>`) THEN <command>
```

**参数:**
- `selector` - 要检查的 CSS 选择器 (反引号内的字符串)
- `command` - 如果条件为真则执行的命令

**示例:**
```c4a
IF (EXISTS `.cookie-banner`) THEN CLICK `.accept-cookies`
IF (EXISTS `#popup-modal`) THEN CLICK `.close-button`
IF (EXISTS `.error-message`) THEN RELOAD
```

**注意:**
- 在执行时检查元素是否存在
- 不等待元素出现
- 可以与 ELSE 结合使用

---

#### `IF (EXISTS <selector>) THEN <command> ELSE <command>`
根据元素存在性执行命令。

**语法:**
```c4a
IF (EXISTS `<selector>`) THEN <command> ELSE <command>
```

**参数:**
- `selector` - 要检查的 CSS 选择器 (反引号内的字符串)
- 第一个 `command` - 如果条件为真则执行
- 第二个 `command` - 如果条件为假则执行

**示例:**
```c4a
IF (EXISTS `.user-menu`) THEN CLICK `.logout` ELSE CLICK `.login`
IF (EXISTS `.loading`) THEN WAIT 5 ELSE CLICK `#continue`
```

**注意:**
- 只会执行一个命令
- 适用于处理不同的页面状态
- 命令必须在同一行

---

#### `极数 (NOT EXISTS <selector>) THEN <command>`
如果元素不存在则执行命令。

**语法:**
```c4a
IF (NOT EXISTS `<selector>`) THEN <极数>
```

**参数:**
- `selector` - 要检查的 CSS 选择器 (反引号内的字符串)
- `command` - 如果元素不存在则执行的命令

**示例:**
```c4a
IF (NOT EXISTS `.logged-in`) THEN GO /login
IF (NOT EXISTS `.results`) THEN CLICK `#search-button`
```

**注意:**
- EXISTS 条件的逆操作
- 适用于错误处理
- 可以检查缺失的必要元素

---

#### `IF (<javascript>) THEN <command>`
根据 JavaScript 条件执行命令。

**语法:**
```c4a
IF (`<javascript>`) THEN <command>
```

**参数:**
- `javascript` - 返回布尔值的 JavaScript 表达式 (反引号内的字符串)
- `command` - 如果条件为真则执行的命令

**示例:**
```c4a
IF (`window.innerWidth < 768`) THEN CLICK `.mobile-menu`
IF (`document.readyState === "complete"`) THEN CLICK `#start`
IF (`localStorage.getItem("user")`) THEN GO /dashboard
```

**注意:**
- JavaScript 在浏览器上下文中执行
- 必须返回布尔值
- 可以访问所有浏览器 API 和全局变量

---

#### `REPEAT (<command>, <count>)`
重复执行命令指定次数。

**语法:**
```c4a
REPEAT (<command>, <count>)
```

**参数:**
- `command` - 要重复的命令
- `count` - 重复次数 (数字)

**示例:**
```c4a
REPEAT (SCROLL DOWN 300, 5)
REPEAT (PRESS Tab, 3)
REPEAT (CLICK `.load-more`, 10)
```

**注意:**
- 精确执行 count 次命令
- 适用于分页、滚动、导航
- 重复之间无延迟 (如需延迟请添加 WAIT)

---

#### `REPEAT (<command>, <condition>)`
当条件为真时重复执行命令。

**语法:**
```c4a
REPEAT (<command>, `<condition>`)
```

**参数:**
- `command` - 要重复的命令
- `condition` - 要检查的 JavaScript 条件 (反引号内的字符串)

**示例:**
```c4a
REPEAT (SCROLL DOWN 500, `document.querySelector(".load-more")`)
REPEAT (PRESS ArrowDown, `window.scrollY < document.body.scrollHeight`)
```

**注意:**
- 每次迭代前检查条件
- JavaScript 条件必须返回布尔值
- 注意避免无限循环

### 💾 变量和数据

在脚本中存储和操作数据。

#### `SETVAR <name> = "<value>"`
创建或更新变量。

**语法:**
```c4a
SETVAR <name> = "<value>"
```

**参数:**
- `name` - 变量名 (字母数字，下划线)
- `value` - 变量值 (引号内的字符串)

**示例:**
```c4a
SETVAR username = "john@example.com"
SETVAR password = "secret123"
SETVAR base_url极数 "https://api.example.com"
SETVAR counter = "0"
```

**注意:**
- 变量在脚本作用域内是全局的
- 值始终为字符串
- 可以使用 $variable 语法与 TYPE 命令一起使用

---

#### `EVAL <javascript>`
执行任意 JavaScript 代码。

**语法:**
```c4a
EVAL `<javascript>`
```

**参数:**
- `javascript` - 要执行的 JavaScript 代码 (反引号内的字符串)

**示例:**
```c4a
EVAL `console.log("Script started")`
EVAL `window.scrollTo(0, 0)`
EVAL `localStorage.setItem("test", "value")`
EVAL `document.title = "Automated Test"`
```

**注意:**
- 完全访问浏览器 JavaScript API
- 适用于自定义逻辑和调试
- 不捕获返回值
- 注意安全影响

### 📝 注释和文档

#### `# <comment>`
向脚本添加注释以进行文档记录。

**语法:**
```c4a
# <comment text>
```

**示例:**
```c4a
# This script logs into the application
# Step 1: Navigate to login page
GO /login

# Step 2: Fill credentials
TYPE "user@example.com"
```

**注意:**
- 注释在执行时被忽略
- 适用于文档记录和调试
- 可以出现在脚本中的任何位置
- 支持多行文档块

### 🔧 过程 (高级)

定义可重用的命令序列。

#### `PROC <name> ... ENDPROC`
定义一个可重用的过程。

**语法:**
```c4a
PROC <name>
  <commands>
ENDPROC
```

**参数:**
- `name` - 过程名 (字母数字，下划线)
- `commands` - 要包含在过程中的命令

**示例:**
```c4a
PROC login
  CLICK `#email`
  TYPE $email
  CLICK `#password`
  TYPE $password
  CLICK `#submit`
ENDPROC

PROC handle_popups
  IF (EXISTS `.cookie-banner`) THEN CLICK `.accept`
  IF (EXISTS `.newsletter-modal`) THEN CLICK `.close`
ENDPROC
```

**注意:**
- 过程必须在使用前定义
- 支持嵌套命令结构
- 变量与主脚本作用域共享

---

#### `<procedure_name>`
调用已定义的过程。

**语法:**
```c4a
<procedure_name>
```

**示例:**
```c4a
# Define procedure first
PROC setup
  GO /login
  WAIT `#form` 5
ENDPROC

# Call procedure
setup
login
```

**注意:**
- 过程必须在调用前定义
- 可以多次调用
- 不支持参数 (改用变量)

## 错误处理最佳实践

### 1. 始终使用等待
```c4a
# Bad - element might not be ready
CLICK `#button`

# Good - wait for element first
WAIT `#button` 5
CLICK `极数`
```

### 2. 处理可选元素
```c4a
# Check before interacting
IF (EXISTS `.popup`) THEN CLICK `.close`
IF (EXISTS `.cookie-banner`) THEN CLICK `.accept`

# Then proceed with main flow
CLICK `#main-action`
```

### 3. 使用描述性变量
```c4a
# Set up reusable data
SETVAR admin_email = "admin@company.com"
SETVAR test_password = "TestPass123!"
SETVAR staging_url = "https://staging.example.com"

# Use throughout script
GO $staging_url
TYPE $admin_email
```

### 4. 添加调试信息
```c4a
# Log progress
EVAL `console.log("Starting login process")`
GO /login

# Verify page state
IF (`document.title.includes("Login")`) THEN EVAL `console.log("On login page")`

# Continue with login
TYPE $username
```

## 常见模式

### 登录流程
```c4a
# Complete login automation
SETVAR email = "user@example.com"
SETVAR password = "mypassword"

GO /login
WA极数 `#login-form` 5

# Handle optional cookie banner
IF (EXISTS `.cookie-banner`) THEN CLICK `.accept-cookies`

# Fill and submit form
CLICK `#email`
TYPE $email
PRESS Tab
TYPE $password
CLICK `button[type="submit"]`

# Wait for redirect
WAIT `.dashboard` 10
```

### 无限滚动
```c4a
# Load all content with infinite scroll
GO /products

# Scroll and load more content
REPEAT (SCROLL DOWN 500, `document.querySelector(".load-more")`)

# Alternative: Fixed number of scroll极数
REPEAT (SCROLL DOWN 800, 10)
WAIT 2
```

### 表单验证
```c4a
# Handle form with validation
SET `#email` "invalid-email"
CLICK `#submit`

# Check for validation error
IF (EXISTS `.error-email`) THEN SET `#email` "valid@example.com"

# Retry submission
CLICK `#submit`
WAIT `.success-message` 5
```

### 多步骤流程
```c4a
# Complex multi-step workflow
PROC navigate_to_step
  CLICK `.next-button`
  WAIT `.step-content` 5
ENDPROC

# Step 1
WAIT `.step-1极数 5
SET `#name` "John Doe"
navigate_to_step

# Step 2
极数 `#email` "john@example.com"
navigate_to_step

# Step 3
CLICK `#submit-final`
WAIT `.confirmation` 10
```

## 与 Crawl4AI 集成

将 C4A-Script 与 Crawl4AI 结合使用以实现动态内容交互:

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

# Define interaction script
script = """
# Handle dynamic content loading
WAIT `.content` 5
IF (EXISTS `.load-more-button`) THEN CLICK `.load-more-button`
WAIT `.additional-content` 5

# Accept cookies if needed
IF (EXISTS `.cookie-banner`) THEN CLICK `.accept-all`
"""

config = CrawlerRunConfig(
    c4a_script=script,
    wait_for=".content",
    screenshot=True
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun("https://example.com", config=config)
    print(result.markdown)
```

此参考涵盖了所有可用的 C4A-Script 命令和模式。要进行交互式学习，请尝试[教程](../examples/c4a_script/tutorial/)或[实时演示](https://docs.crawl4ai.com/c4a-script/demo)。