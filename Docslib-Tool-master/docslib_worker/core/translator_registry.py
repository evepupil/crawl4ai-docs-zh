"""
翻译器注册表模块

管理和提供对可用文档框架翻译器的访问
"""

import os
import importlib
from typing import Dict, Any, Type, Optional

# 存储已注册的翻译器
_TRANSLATORS = {}
_DEFAULT_TRANSLATOR = None

def register_translator(framework_type: str, is_default: bool = False):
    """
    翻译器类装饰器，用于注册翻译器
    
    Args:
        framework_type: 框架类型标识符
        is_default: 是否为默认翻译器
    """
    def decorator(cls):
        global _DEFAULT_TRANSLATOR
        _TRANSLATORS[framework_type] = {
            'class': cls,
            'description': cls.__doc__ or f"{framework_type} 翻译器",
            'is_default': is_default
        }
        
        if is_default and _DEFAULT_TRANSLATOR is None:
            _DEFAULT_TRANSLATOR = framework_type
            
        return cls
    
    return decorator

def get_available_translators() -> Dict[str, Dict[str, Any]]:
    """
    获取所有可用的翻译器
    
    Returns:
        Dict[str, Dict[str, Any]]: 框架类型到翻译器信息的映射
    """
    return _TRANSLATORS

def get_translator_by_type(framework_type: str, **kwargs) -> Any:
    """
    获取指定类型的翻译器实例
    
    Args:
        framework_type: 框架类型标识符
        **kwargs: 传递给翻译器构造函数的参数
    
    Returns:
        Any: 翻译器实例
    
    Raises:
        ValueError: 如果指定的框架类型不存在
    """
    if framework_type not in _TRANSLATORS:
        if _DEFAULT_TRANSLATOR:
            framework_type = _DEFAULT_TRANSLATOR
        else:
            raise ValueError(f"未找到框架类型: {framework_type}")
    
    translator_class = _TRANSLATORS[framework_type]['class']
    return translator_class(**kwargs) 