"""
DocsLib翻译器模块

该模块提供基于AI的文档翻译功能，支持多种文件格式。
现在使用统一的配置管理系统。
"""

import os
import sys

# 添加当前目录到Python搜索路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from .translator import Translator, TranslationError
from .parallel import ParallelTranslator

# 导入配置管理器和日志管理器
from docslib_core.config import ConfigManager
from docslib_core.utils import setup_logger, get_logger

# 全局配置管理器
_config_manager = None

def get_config_manager():
    """获取配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_translator_config():
    """获取翻译器配置"""
    return get_config_manager().get_config('translator')

def get_translator_prompts():
    """获取翻译器提示词配置"""
    return get_config_manager().get_config('translator_prompts')

def setup_logging(config=None):
    """设置日志记录"""
    if config is None:
        config = get_translator_config().get('logging', {})
    
    # 使用核心模块的日志管理器
    return setup_logger('docslib_translator', config)

__version__ = '0.1.0'
__all__ = [
    'Translator', 
    'TranslationError', 
    'ParallelTranslator',
    'get_logger',
    'setup_logger',
    'get_translator_config',
    'get_translator_prompts',
    'setup_logging'
] 

# 设置默认日志记录器
setup_logging() 