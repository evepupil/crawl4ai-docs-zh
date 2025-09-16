"""
翻译器接口桥接模块

将docslib_translator中的Translator类导入到docslib_worker.core命名空间
"""

# 直接从docslib_translator导入Translator类
from docslib_translator import Translator, TranslationError

# 导出这些类
__all__ = ['Translator', 'TranslationError'] 