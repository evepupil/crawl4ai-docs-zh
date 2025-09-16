"""
日志管理模块

该模块提供统一的日志管理功能，支持控制台和文件输出，并确保打印出日志的行数和所在模块。
"""

import os
import sys
import logging
import logging.handlers
from typing import Dict, Any, Optional, Union, Tuple
import traceback
from pathlib import Path
import codecs

# 日志级别映射
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# 日志格式映射
LOG_FORMATS = {
    'simple': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'detailed': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    'full': '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d:%(funcName)s - %(message)s'
}

# 默认配置
DEFAULT_CONFIG = {
    'level': 'INFO',
    'format': 'detailed',
    'console': True,
    'file': None,
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'propagate': False
}

# 缓存已创建的日志记录器
_loggers = {}

def get_logger(name: str, config: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        config: 配置字典，可包含以下键：
            - level: 日志级别，可以是'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
            - format: 日志格式，可以是'simple', 'detailed', 'full'或自定义格式字符串
            - console: 是否输出到控制台
            - file: 日志文件路径，如果为None则不输出到文件
            - max_size: 日志文件最大大小（字节）
            - backup_count: 保留的日志文件数量
            - propagate: 是否传播日志记录到父记录器
    
    Returns:
        logging.Logger: 日志记录器
    """
    # 如果已经创建过该记录器，直接返回
    if name in _loggers:
        return _loggers[name]
    
    return setup_logger(name, config)

def setup_logger(name: str, config: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        config: 配置字典，可包含以下键：
            - level: 日志级别，可以是'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
            - format: 日志格式，可以是'simple', 'detailed', 'full'或自定义格式字符串
            - console: 是否输出到控制台
            - file: 日志文件路径，如果为None则不输出到文件
            - max_size: 日志文件最大大小（字节）
            - backup_count: 保留的日志文件数量
            - propagate: 是否传播日志记录到父记录器
    
    Returns:
        logging.Logger: 日志记录器
    """
    # 合并配置
    cfg = DEFAULT_CONFIG.copy()
    if config:
        cfg.update(config)
    
    # 获取日志级别
    level = cfg['level']
    if isinstance(level, str):
        level = LOG_LEVELS.get(level.upper(), logging.INFO)
    
    # 获取日志格式
    log_format = cfg['format']
    if log_format in LOG_FORMATS:
        log_format = LOG_FORMATS[log_format]
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = cfg['propagate']
    
    # 清除已有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 创建格式化器
    formatter = logging.Formatter(log_format)
    
    # 添加控制台处理器
    if cfg['console']:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 添加文件处理器
    if cfg['file']:
        # 确保日志目录存在
        log_file = cfg['file']
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 自定义UTF-8文件处理器
        file_handler = UTF8RotatingFileHandler(
            log_file,
            maxBytes=cfg['max_size'],
            backupCount=cfg['backup_count'],
            encoding='utf-8-sig'  # 使用带BOM的UTF-8编码
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 缓存日志记录器
    _loggers[name] = logger
    
    return logger

# 自定义UTF-8文件处理器
class UTF8RotatingFileHandler(logging.handlers.RotatingFileHandler):
    """支持UTF-8编码的轮转文件处理器"""
    
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding='utf-8-sig', delay=False):
        """
        初始化处理器
        
        Args:
            filename: 日志文件名
            mode: 文件打开模式
            maxBytes: 文件最大大小
            backupCount: 备份文件数量
            encoding: 文件编码
            delay: 是否延迟打开文件
        """
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        
        # 如果文件不存在或为空，写入BOM标记
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            with codecs.open(filename, 'w', encoding='utf-8-sig') as f:
                pass

def configure_root_logger(config: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    配置根日志记录器
    
    Args:
        config: 配置字典
    
    Returns:
        logging.Logger: 根日志记录器
    """
    return setup_logger('root', config)

def get_calling_module_info() -> Dict[str, Any]:
    """
    获取调用模块的信息
    
    Returns:
        Dict[str, Any]: 调用模块信息
    """
    stack = traceback.extract_stack()
    # 跳过当前函数和日志函数
    frame = stack[-3]
    return {
        'filename': os.path.basename(frame.filename),
        'lineno': frame.lineno,
        'funcName': frame.name,
        'pathname': frame.filename
    }

class LoggerAdapter(logging.LoggerAdapter):
    """
    日志适配器，添加额外的上下文信息
    """
    
    def process(self, msg, kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        处理日志消息，添加额外的上下文信息
        
        Args:
            msg: 日志消息
            kwargs: 关键字参数
            
        Returns:
            Tuple[str, Dict[str, Any]]: 处理后的消息和关键字参数
        """
        # 如果没有提供extra，则创建一个空字典
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        # 添加我们自己的上下文信息
        # 注意：这里不再使用get_calling_module_info()，因为LogRecord已经包含了这些信息
        if not hasattr(self, 'extra'):
            self.extra = {}
        
        # 合并适配器的extra和kwargs的extra
        for key, value in self.extra.items():
            if key not in kwargs['extra']:
                kwargs['extra'][key] = value
                
        return msg, kwargs

def create_logger_with_context(name: str, config: Optional[Dict[str, Any]] = None) -> LoggerAdapter:
    """
    创建带有上下文信息的日志记录器
    
    Args:
        name: 日志记录器名称
        config: 配置字典
    
    Returns:
        LoggerAdapter: 带有上下文信息的日志适配器
    """
    logger = get_logger(name, config)
    return LoggerAdapter(logger, {})

# 设置默认的异常处理器，记录未捕获的异常
def setup_exception_logging():
    """设置未捕获异常的日志记录"""
    def log_uncaught_exception(exc_type, exc_value, exc_traceback):
        """记录未捕获的异常"""
        if issubclass(exc_type, KeyboardInterrupt):
            # 对于键盘中断，调用默认处理器
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger = get_logger('uncaught_exceptions')
        logger.critical(
            "未捕获的异常",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    # 设置异常处理器
    sys.excepthook = log_uncaught_exception 