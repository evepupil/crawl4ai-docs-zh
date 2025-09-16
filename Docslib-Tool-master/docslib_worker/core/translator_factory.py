"""
翻译器工厂模块

提供创建翻译器实例的工厂函数
"""

from typing import Optional, Dict, Any

# 导入翻译器接口
from docslib_worker.core.translator import Translator

def create_translator(translator_type: str, **options) -> Optional[Translator]:
    """
    创建翻译器实例
    
    Args:
        translator_type: 翻译器类型，如'offline'
        **options: 传递给翻译器构造函数的选项
        
    Returns:
        Optional[Translator]: 翻译器实例，如果创建失败则返回None
    """
    try:
        # 目前我们只支持一种翻译器类型，直接创建Translator实例
        # 未来可以根据translator_type创建不同类型的翻译器
        
        # 创建配置字典
        config = {
            'translation_service': {
                'provider': 'yuanbao',
                'base_url': options.get('base_url', 'http://localhost:8000/v1/'),
                'model': options.get('model', 'deepseek-v3'),
                'api_key': options.get('api_key', ''),
                'temperature': options.get('temperature', 0.1),
                'timeout': options.get('timeout', 30),
            },
            'translation_settings': {
                'source_lang': options.get('source_lang', 'en'),
                'target_lang': options.get('target_lang', 'zh'),
                'preserve_format': options.get('preserve_format', True),
                'max_retry': options.get('max_retry', 3),
                'concurrent_requests': options.get('concurrent_requests', 5)
            }
        }
        
        # 创建翻译器实例
        translator = Translator()
        
        return translator
        
    except Exception as e:
        import logging
        logging.error(f"创建翻译器失败: {str(e)}")
        return None 