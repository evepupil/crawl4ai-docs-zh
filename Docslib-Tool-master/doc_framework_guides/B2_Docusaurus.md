# Docusaurus文档翻译指南

## 文件翻译范围

Docusaurus是由Facebook开发的静态网站生成器，主要翻译内容包括：

1. **Markdown文档**：
   - `docs/`目录下的所有`.md`或`.mdx`文件
   - `blog/`目录下的博客文章（如果有）
   - 文件内的所有文本内容，包括标题、段落、列表等

2. **React组件**：
   - `src/pages/`目录下的页面组件中的文本
   - `src/components/`目录下自定义组件中的文本

3. **配置与国际化文件**：
   - `docusaurus.config.js`中的配置项（网站标题、导航栏等）
   - `i18n/`目录下的翻译文件（如果已有国际化设置）
   - `sidebar.js`中的侧边栏配置

4. **静态内容**：
   - `static/`目录下的静态HTML、图片中的文本等

## 部署步骤

### 准备工作

1. 克隆原始文档仓库
```bash
git clone https://github.com/原始项目/文档仓库.git
cd 文档仓库
```

2. 安装依赖
```bash
npm install
# 或
yarn install
```

### 翻译流程

#### 方法一：使用Docusaurus内置的国际化功能

1. 初始化新语言
```bash
npm run write-translations -- --locale zh-CN
```

2. 配置`docusaurus.config.js`添加中文支持
```js
module.exports = {
  // ... 其他配置
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'zh-CN'],
    localeConfigs: {
      en: {
        label: 'English',
      },
      'zh-CN': {
        label: '简体中文',
      },
    },
  },
};
```

3. 创建翻译版本的文档
```bash
mkdir -p i18n/zh-CN/docusaurus-plugin-content-docs/current
cp -r docs/** i18n/zh-CN/docusaurus-plugin-content-docs/current
```

4. 翻译`i18n/zh-CN/`目录下的文件

#### 方法二：创建独立的翻译分支

1. 创建翻译分支
```bash
git checkout -b translation-zh
```

2. 直接翻译`docs/`和其他目录下的内容
3. 更新配置文件中的文本

### 构建与测试

1. 本地预览翻译效果
```bash
npm run start -- --locale zh-CN  # 使用国际化方法时
# 或
npm run start  # 使用独立分支方法时
```

2. 构建静态站点
```bash
npm run build
```

### 部署方法

1. **GitHub Pages部署**
```bash
GIT_USER=<用户名> npm run deploy
```

2. **Netlify/Vercel部署**
   - 连接GitHub仓库到Netlify/Vercel
   - 设置构建命令为`npm run build`
   - 设置输出目录为`build/`

3. **自定义服务器部署**
   - 将生成的`build/`目录上传到Web服务器

## 注意事项

1. **MDX文件处理**：Docusaurus支持MDX（Markdown + JSX），翻译时需注意保留React组件及其属性
2. **React组件中的文本**：
   - 组件中的硬编码文本需要翻译
   - 考虑使用i18n系统管理组件内的文本
3. **代码示例**：通常不翻译代码块中的代码，但可以翻译注释
4. **版本控制**：
   - Docusaurus支持文档版本控制，确保翻译覆盖所有活跃版本
   - 使用`npm run docusaurus docs:version 1.0.0`创建新版本
5. **搜索功能**：
   - 如使用Algolia搜索，需配置多语言搜索索引
   - 本地搜索插件可能需要额外配置
6. **插件兼容性**：确保使用的插件支持国际化

## 自动化工具建议

1. 使用Crowdin等平台管理翻译流程
2. 配置Docusaurus的`docusaurus-plugin-content-docs`插件支持i18n
3. 利用脚本批量处理Markdown文件中的特定模式

## 维护更新

1. 定期与原始仓库同步
2. 使用`docusaurus-update-i18n`工具帮助更新翻译
3. 建立CI/CD流程自动构建和部署翻译站点 