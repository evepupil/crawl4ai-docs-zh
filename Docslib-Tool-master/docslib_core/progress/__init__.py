"""
docslib_core.progress - 翻译进度管理模块

提供项目翻译进度的记录和管理功能
"""

from docslib_core.progress.progress_manager import (
    ProgressManager, 
    get_progress_manager, 
    FileStatus
)

__all__ = ['ProgressManager', 'get_progress_manager', 'FileStatus'] 