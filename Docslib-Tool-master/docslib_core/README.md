# DocsLib Core

DocsLib Core 是 DocsLib 项目的核心功能模块，提供配置管理、日志记录、进度跟踪等基础功能。

## 功能

- 配置管理：加载和管理项目配置
- 日志记录：提供统一的日志记录接口
- 进度跟踪：记录和管理翻译进度
- 工具函数：提供各种辅助功能

## 安装

```bash
pip install docslib-core
```

## 使用方法

```python
# 配置管理
from docslib_core.config import get_config_manager
config_manager = get_config_manager()
config = config_manager.get_config('default')

# 日志记录
from docslib_core.utils import get_logger
logger = get_logger('my_module')
logger.info('这是一条信息')

# 进度管理
from docslib_core.progress import get_progress_manager, FileStatus
progress_manager = get_progress_manager('my_project')
progress_manager.register_files(['file1.md', 'file2.md'])
progress_manager.update_file_status('file1.md', FileStatus.COMPLETED)
```

## 许可证

MIT 