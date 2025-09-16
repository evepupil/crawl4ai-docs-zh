# Crawl4AI Chrome 扩展

Crawl4AI 的可视化提取工具 - 点击即可从任何网页提取数据和内容！

## 🚀 功能特性

- **Click2Crawl**: 点击元素即时构建数据提取方案
- **Markdown 提取**: 选择元素并导出为简洁的 markdown 格式
- **脚本构建器 (Alpha)**: 录制浏览器操作以创建自动化脚本
- **智能元素选择**: 提供视觉反馈的容器和字段选择功能
- **代码生成**: 生成完整的 Crawl4AI Python 代码
- **精美深色 UI**: 与 Crawl4AI 设计语言保持一致

## 📦 安装指南

### 方法一：加载解压的扩展（推荐用于开发）

1. 打开 Chrome 并访问 `chrome://extensions/`
2. 在右上角启用"开发者模式"
3. 点击"加载已解压的扩展程序"
4. 选择 `crawl4ai-assistant` 文件夹
5. 扩展图标（🚀🤖）将出现在工具栏中

### 方法二：首先生成图标

如需正常显示图标：

1. 在浏览器中打开 `icons/generate_icons.html`
2. 右键单击每个画布并另存为：
   - `icon-16.png`
   - `icon-48.png`
   - `icon-128.png`
3. 然后按照上述方法一操作

## 🎯 使用指南

### 使用 Click2Crawl

1. **访问您想要提取数据的任何网站**
2. **点击工具栏中的 Crawl4AI 扩展图标**
3. **点击"Click2Crawl"** 开始捕获模式
4. **选择容器元素**：
   - 悬停在元素上（它们会以蓝色高亮显示）
   - 点击重复的容器（例如产品卡片、文章块）
5. **在容器内选择字段**：
   - 元素现在会以绿色高亮显示
   - 点击您想要提取的每个数据片段
   - 为每个字段命名（例如"title"、"price"、"description"）
6. **测试和导出**：
   - 点击"测试方案"立即查看提取的数据
   - 导出为 Python 代码、JSON 方案或 markdown 格式

### 运行生成的代码

下载的 Python 文件包含：

```python
# 1. The HTML snippet of your selected container
HTML_SNIPPET = """..."""

# 2. The extraction query based on your selections
EXTRACTION_QUERY = """..."""

# 3. Functions to generate and test the schema
async def generate_schema():
    # Generates the extraction schema using LLM
    
async def test_extraction():
    # Tests the schema on the actual website
```

使用方法：

1. 安装 Crawl4AI：`pip install crawl4ai`
2. 运行脚本：`python crawl4ai_schema_*.py`
3. 脚本将生成 `generated_schema.json` 文件
4. 在您的 Crawl4AI 项目中使用此方案！

## 🎨 视觉反馈

- **蓝色虚线轮廓**: 容器选择模式
- **绿色虚线轮廓**: 字段选择模式
- **蓝色实线轮廓**: 已选容器
- **绿色实线轮廓**: 已选字段
- **浮动工具栏**: 显示当前模式和选择状态

## ⌨️ 键盘快捷键

- **ESC**: 取消当前捕获会话

## 🔧 技术细节

- 使用 Manifest V3 构建，确保安全性和性能
- 纯客户端操作 - 不向外部服务器发送数据
- 生成的代码使用 Crawl4AI 的 LLM 集成功能
- 智能选择器生成优先考虑稳定属性

## 🐛 故障排除

### 扩展无法加载
- 确保处于开发者模式
- 检查控制台是否有任何错误
- 确保所有文件都在正确的目录中

### 无法选择元素
- 某些网站可能会阻止扩展
- 尝试刷新页面
- 确保您已先点击"Schema Builder"

### 生成的代码无法工作
- 确保已安装 Crawl4AI
- 检查是否配置了 LLM API 密钥
- 确认网站结构未发生变化

## 🤝 贡献指南

此扩展是 Crawl4AI 项目的一部分。欢迎贡献！

- 报告问题：[GitHub Issues](https://github.com/unclecode/crawl4ai/issues)
- 加入讨论：[Discord](https://discord.gg/crawl4ai)

## 📄 许可证

与 Crawl4AI 相同 - 详见主项目。