"""
docslib_worker.translators - 文档框架翻译器模块
"""

# 导入所有翻译器实现
from docslib_worker.translators.base_translator import BaseTranslator
from docslib_worker.translators.mkdocs_translator import MkDocsTranslator
from docslib_worker.translators.docusaurus_translator import DocusaurusTranslator
from docslib_worker.translators.manual_translator import ManualTranslator

# 导入翻译器注册表函数
from docslib_worker.core.translator_registry import get_available_translators, get_translator_by_type

# 导出所有翻译器
__all__ = [
    'BaseTranslator', 
    'MkDocsTranslator',
    'DocusaurusTranslator',
    'ManualTranslator',
    'get_available_translators',
    'get_translator_by_type'
] 