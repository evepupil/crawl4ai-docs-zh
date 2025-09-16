# DocsLib Worker

DocsLib Worker 是一个用于将文档框架（如MkDocs、Docusaurus等）的文档翻译成其他语言的工具。

## 功能

- 支持多种文档框架的翻译，包括MkDocs、Docusaurus等
- 提供统一的翻译接口，可轻松扩展支持新的文档框架
- 支持翻译进度管理，可断点续传
- 支持配置化，可自定义翻译行为

## 安装

```bash
pip install docslib-worker
```

## 使用方法

```python
from docslib_worker.translators import get_translator_by_type

# 创建MkDocs翻译器
translator = get_translator_by_type(
    'mkdocs',
    source_path='path/to/source/docs',
    target_path='path/to/target/docs',
    config_path='path/to/config.yaml'
)

# 执行翻译
translator.translate()
```

## 命令行使用

通过 docslib_cli 提供的命令行接口使用：

```bash
python -m docslib_cli worker translate path/to/source/docs --target path/to/target/docs --framework mkdocs --target-lang zh-CN
```

## 许可证

MIT 