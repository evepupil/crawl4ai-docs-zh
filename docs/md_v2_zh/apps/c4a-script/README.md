# C4A-Script 交互式教程

一个全面的基于网页的教程，用于学习和实验 C4A-Script - Crawl4AI 的可视化网页自动化语言。

## 🚀 快速开始

### 先决条件
- Python 3.7+
- 现代网页浏览器 (Chrome, Firefox, Safari, Edge)

### 运行教程

1. **克隆并导航**
   ```bash
   git clone https://github.com/unclecode/crawl4ai.git
   cd crawl4ai/docs/examples/c4a_script/tutorial/
   ```

2. **安装依赖**
   ```bash
   pip install flask
   ```

3. **启动服务器**
   ```bash
   python server.py
   ```

4. **在浏览器中打开**
   ```
   http://localhost:8080
   ```

**🌐 在线尝试**: [在线演示](https://docs.crawl4ai.com/c4a-script/demo)

### 2. 尝试你的第一个脚本

```c4a
# Basic interaction
GO playground/
WAIT `body` 2
IF (EXISTS `.cookie-banner`) THEN CLICK `.accept`
CLICK `#start-tutorial`
```

## 🎯 你将学到什么

### 核心功能
- **📝 文本编辑器**: 使用语法高亮编写 C4A-Script
- **🧩 可视化编辑器**: 使用拖放式 Blockly 界面构建脚本
- **🎬 录制模式**: 捕获浏览器操作并自动生成脚本
- **⚡ 实时执行**: 实时运行脚本并获得即时反馈
- **📊 时间线视图**: 可视化和编辑自动化步骤

## 📚 教程内容

### 基本命令
- **导航**: `GO url`
- **等待**: `WAIT selector timeout` 或 `WAIT seconds`
- **点击**: `CLICK selector`
- **输入**: `TYPE "text"`
- **滚动**: `SCROLL DOWN/UP amount`

### 控制流
- **条件语句**: `IF (condition) THEN action`
- **循环**: `REPEAT (action, condition)`
- **过程**: 定义可重用的命令序列

### 高级功能
- **JavaScript 求值**: `EVAL code`
- **变量**: `SET name = "value"`
- **复杂选择器**: 反引号中的 CSS 选择器

## 🎮 交互式演练场功能

教程包含一个完全交互式的网页应用，具有：

### 1. **认证系统**
- 带验证的登录表单
- 会话管理
- 受保护的内容

### 2. **动态内容**
- 无限滚动产品
- 分页控件
- 加载更多按钮

### 3. **复杂表单**
- 多步骤向导
- 动态字段可见性
- 表单验证

### 4. **交互式元素**
- 标签页和手风琴组件
- 模态框和弹出窗口
- 可展开内容

### 5. **数据表格**
- 可排序列
- 搜索功能
- 导出选项

## 🛠️ 教程功能

### 实时代码编辑器
- 语法高亮
- 实时编译
- 带建议的错误消息

### JavaScript 输出查看器
- 查看生成的 JavaScript 代码
- 直接编辑和测试 JS
- 理解编译过程

### 可视化执行
- 逐步进度
- 元素高亮显示
- 控制台输出

### 示例脚本
加载预编写的示例，演示：
- Cookie 横幅处理
- 登录工作流
- 无限滚动自动化
- 多步骤表单完成
- 复杂交互序列

## 📖 教程章节

### 1. 入门
学习基本命令和语法：
```c4a
GO https://example.com
WAIT `.content` 5
CLICK `.button`
```

### 2. 处理动态内容
掌握等待策略和条件语句：
```c4a
IF (EXISTS `.popup`) THEN CLICK `.close`
WAIT `.results` 10
```

### 3. 表单自动化
填写并提交表单：
```c4a
CLICK `#email`
TYPE "user@example.com"
CLICK `button[type="submit"]`
```

### 4. 高级工作流
构建复杂的自动化流程：
```c4a
PROC login
  CLICK `#username`
  TYPE $username
  CLICK `#password`
  TYPE $password
  CLICK `#login-btn`
ENDPROC

SET username = "demo"
SET password = "pass123"
login
```

## 🎯 实践挑战

### 挑战 1: Cookie 和弹出窗口
处理页面加载时出现的 Cookie 横幅和新闻通讯弹出窗口。

### 挑战 2: 完成登录
使用演示凭据成功登录应用程序。

### 挑战 3: 加载所有产品
使用无限滚动加载目录中的所有 100 个产品。

### 挑战 4: 多步骤调查
完成整个多步骤调查表单。

### 挑战 5: 完整工作流
创建一个脚本，实现登录、浏览产品和导出数据。

## 💡 提示与技巧

### 1. 使用特定选择器
```c4a
# 好 - 具体
CLICK `button.submit-order`

# 不好 - 太泛化
CLICK `button`
```

### 2. 始终处理弹出窗口
```c4a
# 检查常见弹出窗口
IF (EXISTS `.cookie-banner`) THEN CLICK `.accept`
IF (EXISTS `.newsletter-modal`) THEN CLICK `.close`
```

### 3. 添加适当的等待
```c4a
# 在交互前等待元素
WAIT `.form` 5
CLICK `#submit`
```

### 4. 使用过程提高可重用性
```c4a
PROC handle_popups
  IF (EXISTS `.popup`) THEN CLICK `.close`
  IF (EXISTS `.cookie-banner`) THEN CLICK `.accept`
ENDPROC

# 在任何地方使用
handle_popups
```

## 🔧 故障排除

### 常见问题

1. **“找不到元素”**
   - 在点击前添加 WAIT
   - 检查选择器特异性
   - 使用 IF 验证元素是否存在

2. **“等待选择器超时”**
   - 增加超时值
   - 检查元素是否动态加载
   - 验证选择器是否正确

3. **“缺少 THEN 关键字”**
   - 所有 IF 语句都需要 THEN
   - 格式: `IF (condition) THEN action`

## 🚀 与 Crawl4AI 一起使用

在教程中掌握 C4A-Script 后，将其与 Crawl4AI 一起使用：

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

config = CrawlerRunConfig(
    url="https://example.com",
    c4a_script="""
    WAIT `.content` 5
    IF (EXISTS `.load-more`) THEN CLICK `.load-more`
    WAIT `.new-content` 3
    """
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(config=config)
```

## 📝 示例脚本

查看 `scripts/` 文件夹获取完整示例：
- `01-basic-interaction.c4a` - 入门
- `02-login-flow.c4a` - 认证
- `03-infinite-scroll.c4a` - 动态内容
- `04-multi-step-form.c4a` - 复杂表单
- `05-complex-workflow.c4a` - 完整自动化

## 🏗️ 开发者指南

### 项目架构

```
tutorial/
├── server.py              # Flask 应用服务器
├── assets/               # 教程特定资源
│   ├── app.js            # 主要应用逻辑
│   ├── c4a-blocks.js     # 自定义 Blockly 块
│   ├── c4a-generator.js  # 代码生成
│   ├── blockly-manager.js # Blockly 集成
│   └── styles.css        # 主要样式
├── playground/           # 交互式演示环境
│   ├── index.html        # 演示网页应用
│   ├── app.js           # 演示应用逻辑
│   └── styles.css       # 演示样式
├── scripts/             # 示例 C4A 脚本
└── index.html           # 主要教程界面
```

### 关键组件

#### 1. TutorialApp (`assets/app.js`)
主要应用控制器，管理：
- 代码编辑器集成 (CodeMirror)
- 脚本执行和浏览器预览
- 教程导航和课程
- 状态管理和持久化

#### 2. BlocklyManager (`assets/blockly-manager.js`)
可视化编程界面：
- 自定义 C4A-Script 块定义
- 可视化块和文本之间的双向同步
- 实时代码生成
- 深色主题集成

#### 3. 录制系统
支持录制功能：
- 浏览器事件捕获
- 智能事件分组和过滤
- 自动 C4A-Script 生成
- 时间线可视化

### 自定义

#### 添加新命令
1. **定义块** (`assets/c4a-blocks.js`)
2. **添加生成器** (`assets/c4a-generator.js`)
3. **更新解析器** (`assets/blockly-manager.js`)

#### 主题和样式
- 主要样式: `assets/styles.css`
- 主题变量: CSS 自定义属性
- 深色模式: 根据系统偏好自动应用

### 配置
```python
# server.py 配置
PORT = 8080
DEBUG = True
THREADED = True
```

### API 端点
- `GET /` - 主要教程界面
- `GET /playground/` - 交互式演示环境
- `POST /execute` - 脚本执行端点
- `GET /examples/<script>` - 加载示例脚本

## 🔧 故障排除

### 常见问题

**端口已被占用**
```bash
# 终止现有进程
lsof -ti:8080 | xargs kill -9
# 或使用不同端口
python server.py --port 8081
```

**Blockly 未加载**
- 检查浏览器控制台是否有 JavaScript 错误
- 验证所有静态文件是否正确提供
- 确保正确的脚本加载顺序

**录制问题**
- 验证 iframe 权限
- 检查跨域通信
- 确保事件监听器已附加

### 调试模式
通过在 `assets/app.js` 中设置 `DEBUG = True` 来启用详细日志记录

## 📚 附加资源

- **[C4A-Script 文档](../../md_v2/core/c4a-script.md)** - 完整的语言指南
- **[API 参考](../../md_v2/api/c4a-script-reference.md)** - 详细的命令文档
- **[在线演示](https://docs.crawl4ai.com/c4a-script/demo)** - 无需安装即可尝试
- **[示例脚本](../)** - 更多自动化示例

## 🤝 贡献

### 错误报告
1. 检查 GitHub 上的现有问题
2. 提供最小复现步骤
3. 包括浏览器和系统信息
4. 添加相关控制台日志

### 功能请求
1. Fork 仓库
2. 创建功能分支: `git checkout -b feature/my-feature`
3. 使用不同浏览器彻底测试
4. 更新文档
5. 提交拉取请求

### 代码风格
- 使用一致的缩进 (JS 用 2 个空格，Python 用 4 个空格)
- 为复杂逻辑添加注释
- 遵循现有的命名约定
- 使用多个浏览器测试

---

**自动化愉快！** 🎉

需要帮助？查看我们的[文档](https://docs.crawl4ai.com)或在 [GitHub](https://github.com/unclecode/crawl4ai) 上提出问题。