# DocsLib CLI 工具使用说明

DocsLib CLI 是一个命令行工具，用于访问 DocsLib 工具集的各种功能，包括文本翻译、文件翻译和文档项目翻译等。

## 安装指南

### 依赖要求

- Python 3.8 或更高版本
- pip 包管理器
- docslib-core 
- docslib-translator
- docslib-worker
- docslib-detector

### 安装方法

#### 方法1: 使用安装脚本（推荐）

```bash
# 在项目根目录下运行安装脚本
python install.py
```

#### 方法2: 手动安装

```bash
# 安装所有依赖
pip install -e ../docslib_core
pip install -e ../docslib_translator
pip install -e ../docslib_detector
pip install -e ../docslib_worker
pip install -e .
```

## 功能概述

DocsLib CLI 工具提供以下主要功能：

1. **翻译器功能** (`translator`)：
   - 翻译单个文本
   - 翻译单个文件
   - 批量翻译文件
   - 查看翻译器配置

2. **文档工作器功能** (`worker`)：
   - 自动检测文档项目框架（如 MkDocs、Docusaurus 等）
   - 翻译整个文档项目
   - 支持自定义翻译配置

## 使用方法

### 基本命令

```bash
# 显示帮助信息
docslib --help

# 显示翻译器帮助信息
docslib translator --help

# 显示文档工作器帮助信息
docslib worker --help
```

### 翻译器命令

#### 翻译文本

```bash
# 翻译单个文本
docslib translator text "Hello, world!"

# 指定源语言和目标语言
docslib translator text "Hello, world!" --source-lang en --target-lang zh

# 从标准输入读取文本
cat file.txt | docslib translator text
```

#### 翻译文件

```bash
# 翻译单个文件
docslib translator file input.md output.md

# 指定源语言和目标语言
docslib translator file input.md output.md --source-lang en --target-lang zh

# 如果不指定输出文件，则使用源文件名加上目标语言后缀
docslib translator file input.md --target-lang zh
# 将生成 input.zh.md
```

#### 批量翻译文件

```bash
# 翻译目录中的所有 Markdown 文件
docslib translator files source_dir target_dir

# 指定文件匹配模式
docslib translator files source_dir target_dir --pattern "**/*.txt"

# 指定源语言和目标语言
docslib translator files source_dir target_dir --source-lang en --target-lang zh

# 指定并行工作线程数
docslib translator files source_dir target_dir --workers 10
```

#### 查看翻译器配置

```bash
# 以 YAML 格式显示配置
docslib translator config

# 以 JSON 格式显示配置
docslib translator config --format json
```

### 文档工作器命令

#### 检测文档项目框架

```bash
# 检测项目框架
docslib worker detect docs_dir

# 显示详细信息
docslib worker detect docs_dir --verbose
```

#### 翻译文档项目

```bash
# 翻译文档项目（自动检测框架类型）
docslib worker translate docs_dir output_dir

# 指定框架类型（如果自动检测不准确）
docslib worker translate docs_dir output_dir --framework mkdocs

# 指定配置文件
docslib worker translate docs_dir output_dir --config custom_config.yaml

# 指定目标语言
docslib worker translate docs_dir output_dir --target-lang zh

# 强制覆盖已存在的目标目录
docslib worker translate docs_dir output_dir --force
```

## 故障排除

### 常见问题

1. **导入错误**：
   
   如果出现 `无法导入 docslib_worker 模块` 或类似错误，您可以尝试以下几种解决方法：
   
   **方法1：使用导入修复工具**
   ```bash
   # 运行导入修复工具
   python fix_imports.py
   ```
   
   **方法2：使用备用启动脚本**
   ```bash
   # 使用备用启动脚本运行命令
   python run_docslib.py worker translate <源目录> <目标目录>
   ```
   
   **方法3：手动安装所有依赖**
   ```bash
   pip install -e ../docslib_core
   pip install -e ../docslib_translator
   pip install -e ../docslib_detector
   pip install -e ../docslib_worker
   pip install -e .
   ```
   
   **方法4：检查Python路径**
   ```bash
   # 查看当前Python路径
   python -c "import sys; print('\n'.join(sys.path))"
   
   # 检查模块是否已安装
   python -c "import importlib.util; print('docslib_worker 已安装' if importlib.util.find_spec('docslib_worker') else 'docslib_worker 未安装')"
   ```

2. **权限问题**：
   
   确保有读写目标目录的权限。在Windows上，可能需要以管理员权限运行命令提示符或PowerShell。

3. **内存不足**：
   
   处理大型文档项目时，可以减少并行工作线程数：
   ```bash
   docslib worker translate docs_dir output_dir --workers 3
   ```

4. **翻译质量问题**：
   
   可以通过配置文件调整翻译参数，提高翻译质量

### 日志文件

默认情况下，日志文件保存在以下位置：

- Linux/macOS: `~/.docslib/logs/`
- Windows: `%USERPROFILE%\.docslib\logs\`

## 高级用法

### 自定义配置文件

您可以创建自定义配置文件来控制翻译行为：

```yaml
# 翻译设置
translation:
  source_lang: en
  target_lang: zh
  preserve_format: true
  max_retry: 3
  concurrent_requests: 5

# 文件处理设置
file_processing:
  translate_extensions:
    - .md
    - .txt
    - .html
  special_files:
    - mkdocs.yml
    - README.md
    - index.md
  exclude:
    - .git
    - node_modules
    - site

# SEO 设置
seo:
  title_suffix: " | 中文文档"
  default_keywords:
    - 文档
    - 技术文档
    - 中文文档
  description_template: "{title} - 详细的中文技术文档，提供完整的{keywords}指南。"
```

### 环境变量

DocsLib CLI 支持以下环境变量：

- `DOCSLIB_CONFIG_PATH`: 指定配置文件路径
- `DOCSLIB_LOG_LEVEL`: 设置日志级别 (DEBUG, INFO, WARNING, ERROR)
- `PYTHONPATH`: 如果遇到导入错误，可以设置此变量包含所有模块路径

## 开发指南

如果您想为 DocsLib CLI 工具贡献代码，请按照以下步骤操作：

1. 创建您的特性分支
2. 实现您的功能或修复
3. 添加测试用例
4. 确保所有测试通过
5. 提交拉取请求

## 联系方式

如有问题或建议，请联系：

- 项目主页：https://github.com/docslib/docslib-tool
- 电子邮件：info@docslib.example.com 