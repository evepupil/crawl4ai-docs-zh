# GitBook文档翻译指南

## 文件翻译范围

GitBook是一个用于创建和发布文档的工具，主要翻译内容包括：

1. **Markdown文件**：
   - 所有`.md`文件，包括`README.md`（通常作为首页）
   - 文件内的所有文本内容，包括标题、段落、列表等

2. **目录结构文件**：
   - `SUMMARY.md`（定义GitBook的目录结构）
   - `GLOSSARY.md`（术语表，如果有）

3. **配置文件**：
   - `book.json`或`.gitbook.yaml`中的配置项（书名、描述等）
   - 插件配置中的文本内容

4. **自定义页面**：
   - 自定义模板中的文本（如果使用了模板）
   - 自定义CSS中的注释（如果有）

## 部署步骤

### 准备工作

1. 克隆原始文档仓库
```bash
git clone https://github.com/原始项目/文档仓库.git
cd 文档仓库
```

2. 安装GitBook CLI（如果使用GitBook传统版本）
```bash
npm install -g gitbook-cli
```

### 翻译流程

#### 方法一：创建独立翻译分支

1. 创建翻译分支
```bash
git checkout -b translation-zh
```

2. 翻译所有Markdown文件
3. 更新`SUMMARY.md`中的目录标题
4. 更新`book.json`或`.gitbook.yaml`中的配置

#### 方法二：使用GitBook多语言功能

1. 在`book.json`中配置多语言支持
```json
{
  "title": "文档标题",
  "languages": ["en", "zh"],
  "plugins": ["language-picker"]
}
```

2. 创建语言子目录
```bash
mkdir -p zh
cp -r *.md zh/
cp -r content zh/
```

3. 为每种语言创建独立的`SUMMARY.md`
4. 翻译`zh/`目录下的所有文件

### 构建与测试

#### 传统GitBook CLI（本地）

1. 安装依赖
```bash
gitbook install
```

2. 本地预览
```bash
gitbook serve
```

3. 构建静态站点
```bash
gitbook build
```

#### GitBook.com平台（在线）

1. 在GitBook.com创建新空间
2. 连接GitHub仓库
3. 配置构建设置
4. 发布站点

### 部署方法

1. **GitBook.com托管**：
   - 直接在GitBook.com平台上发布

2. **GitHub Pages部署**：
   - 将构建的`_book/`目录发布到gh-pages分支
```bash
gh-pages -d _book
```

3. **自定义服务器部署**：
   - 将生成的`_book/`目录上传到Web服务器

## 注意事项

1. **链接处理**：
   - 内部链接需要保持正确，确保翻译后的文件名与链接匹配
   - 如果使用多语言方法，链接路径可能需要调整

2. **图片处理**：
   - 如果图片包含文本，考虑创建本地化版本
   - 图片路径需要保持正确或相应调整

3. **插件兼容性**：
   - 确保使用的GitBook插件支持多语言
   - 某些插件可能需要额外配置才能正确显示翻译内容

4. **版本差异**：
   - GitBook有两个主要版本：传统CLI版本和新的GitBook.com平台
   - 确认项目使用的是哪个版本，因为它们的配置和工作流程有所不同

5. **多语言结构**：
   - 使用多语言功能时，确保每个语言版本的结构一致
   - 保持原始文档和翻译文档的同步更新

6. **术语一致性**：
   - 考虑使用`GLOSSARY.md`维护术语表，确保术语翻译一致

## 自动化工具建议

1. 使用脚本批量处理Markdown文件
2. 创建翻译记忆库，保持术语一致性
3. 使用GitBook插件如`gitbook-plugin-language-picker`支持语言切换
4. 设置CI/CD流程自动构建和部署翻译站点

## 维护更新

1. 定期与原始仓库同步，合并上游更改
2. 使用diff工具识别需要更新翻译的部分
3. 考虑使用Git钩子在提交前检查翻译文件的完整性
4. 建立自动化流程监测原始文档的变化 