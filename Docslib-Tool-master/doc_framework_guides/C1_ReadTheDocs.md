# ReadTheDocs文档翻译指南

## 文件翻译范围

ReadTheDocs是一个动态渲染的文档托管平台，主要翻译内容包括：

1. **文档源文件**：
   - `docs/`目录下的所有`.rst`（reStructuredText）或`.md`（Markdown）文件
   - 文件内的所有文本内容，包括标题、段落、列表、表格等
   - 代码块内的注释（可选）

2. **配置文件**：
   - `conf.py`中的项目名称、版本、语言等配置
   - `mkdocs.yml`（如果使用MkDocs作为生成器）
   - `.readthedocs.yaml`中的构建配置

3. **索引文件**：
   - `index.rst`或`index.md`（主索引文件）
   - 各章节的索引文件

4. **主题自定义内容**：
   - 自定义主题中的HTML模板
   - 自定义CSS中的文本和注释

## 部署步骤

### 准备工作

1. 克隆原始文档仓库
```bash
git clone https://github.com/原始项目/文档仓库.git
cd 文档仓库
```

2. 安装依赖
```bash
pip install -r requirements.txt
# 或者
pip install sphinx sphinx-rtd-theme
```

### 翻译流程

#### 方法一：使用Sphinx国际化功能

1. 提取待翻译文本
```bash
sphinx-build -b gettext docs/ docs/_build/gettext
```

2. 初始化中文翻译文件
```bash
sphinx-intl update -p docs/_build/gettext -l zh_CN
```

3. 翻译`docs/locale/zh_CN/LC_MESSAGES/`目录下的`.po`文件

4. 更新`conf.py`配置多语言支持
```python
language = 'zh_CN'  # 默认语言
locale_dirs = ['locale/']  # 翻译文件目录
gettext_compact = False  # 不合并翻译文件
```

#### 方法二：创建独立翻译分支

1. 创建翻译分支
```bash
git checkout -b translation-zh
```

2. 直接翻译`docs/`目录下的所有文档文件
3. 更新`conf.py`中的配置，将语言设置为`'zh_CN'`

### 构建与测试

1. 本地构建文档
```bash
# 使用Sphinx
sphinx-build -b html docs/ docs/_build/html

# 使用MkDocs（如果项目使用MkDocs）
mkdocs build
```

2. 本地预览
```bash
# Sphinx
python -m http.server -d docs/_build/html

# MkDocs
mkdocs serve
```

### 部署方法

1. **ReadTheDocs平台部署**：
   - 在ReadTheDocs创建项目，连接到GitHub仓库
   - 在项目管理页面添加新语言版本
   - 配置构建设置

2. **手动部署**：
   - 构建HTML文档
   - 将生成的HTML文件上传到Web服务器

## 注意事项

1. **reStructuredText语法**：
   - RST比Markdown更严格，注意保持格式一致
   - 特别注意标题下划线长度、缩进级别等

2. **Sphinx指令处理**：
   - 保留Sphinx特有的指令（如`.. note::`、`.. warning::`等）
   - 确保翻译不破坏指令格式

3. **交叉引用**：
   - 保持原始文档中的引用标签（如`:ref:`、`:doc:`等）
   - 如果翻译了引用标签，确保更新所有引用它的地方

4. **图片和媒体**：
   - 如果图片包含文本，考虑创建本地化版本
   - 保持图片路径正确

5. **多语言配置**：
   - 确保`.readthedocs.yaml`中正确配置了多语言支持
   - 设置语言切换菜单

6. **版本控制**：
   - ReadTheDocs支持多版本文档，确保翻译覆盖所有活跃版本
   - 考虑使用版本别名管理翻译版本

## 自动化工具建议

1. 使用`sphinx-intl`管理翻译流程
2. 使用翻译记忆工具保持术语一致性
3. 设置CI/CD流程自动构建翻译文档
4. 使用`polib`等Python库处理`.po`文件的批量操作

## 维护更新

1. 定期与原始仓库同步，更新翻译
2. 使用`sphinx-intl update`更新翻译文件
3. 监控ReadTheDocs构建日志，及时修复错误
4. 建立自动化流程检测原始文档的变化并更新翻译 