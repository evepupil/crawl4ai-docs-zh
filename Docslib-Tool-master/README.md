# DocsLib 文档翻译工具集

DocsLib 是一个强大的文档翻译工具集，专注于技术文档的翻译，支持多种文档框架，如 MkDocs、Docusaurus 等。

## 功能特点

- **自动框架检测**：自动识别文档项目的框架类型
- **批量文档翻译**：一键翻译整个文档项目
- **进度跟踪**：实时监控翻译进度
- **保留格式**：保持原文档的结构和格式
- **多语言支持**：支持多种语言之间的翻译
- **可扩展性**：易于扩展支持新的文档框架

## 安装指南

### 依赖要求

- Python 3.8 或更高版本
- pip 包管理器

### 快速安装

使用提供的安装脚本可以一键安装所有组件：

```bash
# 克隆仓库
git clone https://github.com/docslib/docslib-tool.git
cd docslib-tool

# 运行安装脚本
python install.py
```

### 手动安装

如果您希望手动安装，请按照以下顺序安装各个组件：

```bash
# 安装核心组件
pip install -e docslib_core

# 安装翻译器
pip install -e docslib_translator

# 安装文档框架检测器
pip install -e docslib_detector

# 安装文档工作器
pip install -e docslib_worker

# 安装命令行工具
pip install -e docslib_cli

# 安装主包
pip install -e .
```

### 解决导入问题

如果您遇到类似 `无法导入 docslib_worker 模块` 的错误，可以使用我们提供的修复工具：

```bash
# 运行导入修复工具
python fix_imports.py
```

或者使用备用的启动脚本运行 DocsLib CLI：

```bash
# 使用备用启动脚本
python run_docslib.py worker translate <源目录> <目标目录>
```

这些工具会尝试通过多种方法修复导入问题，包括：
- 使用 pip 重新安装模块
- 创建 .pth 文件添加模块到 Python 路径
- 生成自定义启动脚本

## 使用方法

安装完成后，您可以使用 `docslib` 命令来使用各种功能。

### 命令行帮助

```bash
# 显示主命令帮助
docslib --help

# 显示翻译器命令帮助
docslib translator --help

# 显示文档工作器命令帮助
docslib worker --help
```

### 翻译文本

```bash
# 翻译单个文本
docslib translator text "Hello, world!"

# 指定源语言和目标语言
docslib translator text "Hello, world!" --source-lang en --target-lang zh
```

### 翻译文件

```bash
# 翻译单个文件
docslib translator file input.md output.md

# 批量翻译文件
docslib translator files source_dir target_dir --pattern "**/*.md"
```

### 翻译文档项目

```bash
# 翻译文档项目（自动检测框架类型）
docslib worker translate docs_dir output_dir

# 指定框架类型
docslib worker translate docs_dir output_dir --framework mkdocs

# 指定配置文件
docslib worker translate docs_dir output_dir --config custom_config.yaml
```

## 项目结构

DocsLib 工具集由以下几个主要组件组成：

- **docslib_core**：核心功能模块，提供配置管理、日志记录和进度跟踪
- **docslib_translator**：翻译引擎，负责文本和文件的翻译
- **docslib_detector**：框架检测器，用于识别文档项目的框架类型
- **docslib_worker**：文档工作器，处理特定框架的文档翻译
- **docslib_cli**：命令行界面，提供用户友好的命令行工具

## 故障排除

### 常见问题

1. **导入错误**：
   如果遇到 `无法导入 docslib_worker 模块` 等错误，请尝试以下解决方案：
   ```bash
   # 方法1：使用修复工具
   python fix_imports.py
   
   # 方法2：使用备用启动脚本
   python run_docslib.py --help
   
   # 方法3：手动安装所有模块
   pip install -e docslib_core
   pip install -e docslib_translator
   pip install -e docslib_detector
   pip install -e docslib_worker
   pip install -e docslib_cli
   ```

2. **权限问题**：
   如果安装过程中遇到权限错误，请尝试使用管理员权限运行命令：
   - Windows: 以管理员身份运行命令提示符或PowerShell
   - Linux/macOS: 使用 `sudo` 命令

3. **内存不足**：
   处理大型文档项目时，可以通过减少并行工作线程来降低内存使用：
   ```bash
   docslib worker translate docs_dir --workers 2
   ```

4. **Python路径问题**：
   如果您使用的是虚拟环境或自定义Python安装，请确保正确激活环境：
   ```bash
   # 激活虚拟环境 (Windows)
   .\venv\Scripts\activate
   
   # 激活虚拟环境 (Linux/macOS)
   source venv/bin/activate
   ```

### 日志文件

默认情况下，日志文件保存在以下位置：

- Linux/macOS: `~/.docslib/logs/`
- Windows: `%USERPROFILE%\.docslib\logs\`

## 贡献指南

我们欢迎并感谢任何形式的贡献！如果您想要贡献代码、报告问题或提出建议，请：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件

## 联系我们

如有任何问题或建议，欢迎联系我们：

- 项目主页：[https://github.com/docslib/docslib-tool](https://github.com/docslib/docslib-tool)
- 电子邮件：info@docslib.example.com 