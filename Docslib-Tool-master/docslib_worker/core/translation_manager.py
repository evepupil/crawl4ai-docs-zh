"""
翻译管理器模块

提供检测框架类型并调用相应翻译器的功能
"""

import os
import time
from typing import Dict, Any, Optional, List, Tuple

# 导入核心模块的配置管理器和日志管理器
from docslib_core.config import get_config_manager
from docslib_core.utils import get_logger

# 导入检测器
from docslib_detector import detect_framework

# 导入翻译器注册表
from docslib_worker.core.translator_registry import (
    get_translator_by_type,
    get_available_translators
)

def translate_project(
    source_path: str, 
    target_path: Optional[str] = None,
    config_path: Optional[str] = None,
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    force_framework: Optional[str] = None
) -> bool:
    """
    翻译文档项目
    
    Args:
        source_path: 源文档目录路径
        target_path: 目标翻译文档路径，如果为None则使用源路径加目标语言后缀
        config_path: 配置文件路径
        log_level: 日志级别
        log_file: 日志文件路径
        force_framework: 强制使用指定框架类型，跳过检测
        
    Returns:
        bool: 翻译成功返回True，否则返回False
    """
    start_time = time.time()
    
    # 获取配置管理器
    config_manager = get_config_manager(os.path.dirname(config_path) if config_path else None)
    
    # 加载配置
    config = config_manager.get_config('default')
    
    # 获取日志配置
    log_config = config.get('logging', {})
    if log_level:
        log_config['level'] = log_level
    if log_file:
        log_config['file'] = log_file
    
    # 设置日志记录器
    logger = get_logger('docslib_worker', log_config)
    
    # 获取目标语言
    target_lang = config.get('global', {}).get('target_lang', 'zh')
    
    # 如果未指定目标路径，使用源路径加目标语言后缀
    if not target_path:
        source_dir = os.path.abspath(source_path)
        parent_dir = os.path.dirname(source_dir)
        dir_name = os.path.basename(source_dir)
        target_path = os.path.join(parent_dir, f"{dir_name}_{target_lang}")
    
    logger.info(f"翻译项目: {source_path} -> {target_path}")
    logger.info(f"目标语言: {target_lang}")
    
    # 如果强制指定了框架类型，直接使用
    if force_framework:
        framework_type = force_framework
        framework_info = {"framework": framework_type}
        logger.info(f"强制使用框架类型: {framework_type}")
    else:
        # 否则，检测框架类型
        logger.info(f"检测文档框架类型: {source_path}")
        framework_info = detect_framework(source_path, logger)
        framework_type = framework_info.get("framework", "unknown")
        
        if framework_type == "unknown":
            logger.warning("未检测到已知的文档框架类型，将使用默认翻译器")
    
    # 获取支持的框架列表
    available_translators = get_available_translators()
    supported_frameworks = list(available_translators.keys())
    logger.info(f"支持的框架类型: {supported_frameworks}")
    
    try:
        # 获取翻译器实例
        translator = get_translator_by_type(
            framework_type,
            source_path=source_path,
            target_path=target_path,
            config_path=config_path
        )
        
        # 执行翻译
        logger.info("开始翻译文档...")
        success = translator.translate()
        
        elapsed = time.time() - start_time
        
        if success:
            logger.info(f"文档翻译完成: {target_path}，耗时: {elapsed:.2f}秒")
        else:
            logger.error("文档翻译失败")
        
        return success
    
    except ValueError as e:
        logger.error(f"创建翻译器失败: {str(e)}")
        return False
    
    except Exception as e:
        logger.error(f"翻译过程中发生错误: {str(e)}")
        return False 