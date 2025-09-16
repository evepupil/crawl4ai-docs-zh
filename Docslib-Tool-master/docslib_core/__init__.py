"""
DocsLib核心功能模块

该模块提供DocsLib项目的核心功能，包括配置管理、日志记录、进度跟踪等。
"""

__version__ = '0.1.0'

# 导出配置管理器
from docslib_core.config import get_config_manager, ConfigManager

# 导出日志工具
from docslib_core.utils import get_logger, setup_logger

# 导出进度管理器
from docslib_core.progress import ProgressManager, get_progress_manager, FileStatus

__all__ = [
    'get_config_manager', 
    'ConfigManager', 
    'get_logger', 
    'setup_logger',
    'ProgressManager',
    'get_progress_manager',
    'FileStatus'
] 