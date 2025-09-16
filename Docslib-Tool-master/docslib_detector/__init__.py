"""
docslib_detector - 文档仓库部署类型检测工具
"""

__version__ = '0.1.0'

from docslib_detector.core.detector_manager import detect_framework, detect_files

__all__ = ['detect_framework', 'detect_files'] 