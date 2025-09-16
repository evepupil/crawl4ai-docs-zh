# Crawl4AI 中文文档

这个目录包含了 Crawl4AI 文档的中文翻译版本。

## 目录结构

- `docs/md_v2_zh/` - 中文文档源文件
- `mkdocs_zh.yml` - 中文文档构建配置文件
- `site/` - 构建后的网站文件

## 构建中文文档

要构建中文文档网站，请运行以下命令：

```bash
mkdocs build -f mkdocs_zh.yml
```

## 本地预览中文文档

要本地预览中文文档，请运行以下命令：

```bash
mkdocs serve -f mkdocs_zh.yml
```

然后在浏览器中打开 `http://localhost:8000` 查看文档。

## 部署

要部署中文文档网站，您可以使用任何静态网站托管服务，如 GitHub Pages、Netlify 或 Vercel。

只需将 `site/` 目录中的内容部署到您的托管服务即可。

## 翻译信息

- 翻译工具: DocsLib AI Translator
- 翻译日期: 2025-09-16
- 翻译完成时间: 约18分钟
- 翻译文件数: 102个文件

## 注意事项

1. 代码块内容保持原文不翻译
2. 链接地址保持原文不翻译
3. 技术术语已尽量保持一致性
4. 翻译后已测试构建，确保网站可以正常访问

## 贡献

如果您发现翻译中的任何问题或有改进建议，请提交 Issue 或 Pull Request。