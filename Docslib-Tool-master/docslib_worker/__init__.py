"""
docslib_worker - 文档翻译工作者模块

提供自动检测文档框架并进行翻译的功能
"""

__version__ = '0.1.0'

from docslib_worker.core.translation_manager import translate_project

__all__ = ['translate_project'] 