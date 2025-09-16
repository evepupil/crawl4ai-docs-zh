"""
配置管理器

该模块提供统一的配置管理功能，用于加载和访问DocsLib项目的各个组件的配置。
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List, Union
from functools import lru_cache

# 配置管理器单例
_config_manager_instance = None

def get_config_manager(config_dir: Optional[str] = None) -> 'ConfigManager':
    """
    获取配置管理器单例实例
    
    Args:
        config_dir: 配置文件目录，如果为None则使用默认目录
        
    Returns:
        ConfigManager: 配置管理器实例
    """
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager(config_dir)
    return _config_manager_instance

class ConfigManager:
    """统一配置管理器"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录，如果为None则使用默认目录
        """
        # 设置日志记录器
        self.logger = logging.getLogger('docslib.config')
        
        # 默认配置目录
        if config_dir is None:
            # 使用项目根目录下的config目录
            self.config_dir = os.path.abspath(os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'config'
            ))
        else:
            self.config_dir = os.path.abspath(config_dir)
        
        self.logger.debug(f"配置目录: {self.config_dir}")
        
        # 配置缓存
        self._config_cache: Dict[str, Dict[str, Any]] = {}
        
        # 加载默认配置
        self._default_config = self._load_yaml_file('default.yaml') or {}
        
    def get_config(self, name: str) -> Dict[str, Any]:
        """
        获取指定名称的配置
        
        Args:
            name: 配置名称（不含扩展名）
            
        Returns:
            Dict[str, Any]: 配置字典
        """
        # 检查缓存
        if name in self._config_cache:
            return self._config_cache[name]
        
        # 加载配置
        config_file = f"{name}.yaml"
        config = self._load_yaml_file(config_file) or {}
        
        # 合并默认配置
        if name in self._default_config:
            config = self._merge_config(self._default_config.get(name, {}), config)
        
        # 缓存配置
        self._config_cache[name] = config
        
        return config
    
    def get_value(self, name: str, key_path: str, default: Any = None) -> Any:
        """
        获取配置中的特定值
        
        Args:
            name: 配置名称（不含扩展名）
            key_path: 键路径，使用点号分隔（如'logging.level'）
            default: 默认值，如果键不存在则返回该值
            
        Returns:
            Any: 配置值
        """
        config = self.get_config(name)
        keys = key_path.split('.')
        
        # 遍历键路径
        current = config
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        
        return current
    
    def reload(self, name: Optional[str] = None) -> None:
        """
        重新加载配置
        
        Args:
            name: 配置名称（不含扩展名），如果为None则重新加载所有配置
        """
        if name is None:
            # 重新加载所有配置
            self._config_cache.clear()
            self._default_config = self._load_yaml_file('default.yaml') or {}
            self.logger.info("已重新加载所有配置")
        elif name in self._config_cache:
            # 重新加载指定配置
            del self._config_cache[name]
            self.logger.info(f"已重新加载配置: {name}")
    
    def _load_yaml_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        加载YAML配置文件
        
        Args:
            filename: 文件名
            
        Returns:
            Optional[Dict[str, Any]]: 配置字典，如果文件不存在则返回None
        """
        file_path = os.path.join(self.config_dir, filename)
        
        if not os.path.exists(file_path):
            self.logger.warning(f"配置文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            self.logger.debug(f"已加载配置文件: {file_path}")
            return config
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {file_path}: {str(e)}")
            return None
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并配置
        
        Args:
            base: 基础配置
            override: 覆盖配置
            
        Returns:
            Dict[str, Any]: 合并后的配置
        """
        result = base.copy()
        
        for key, value in override.items():
            # 如果两者都是字典，则递归合并
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                # 否则直接覆盖
                result[key] = value
        
        return result
    
    def get_all_config_files(self) -> List[str]:
        """
        获取所有配置文件名
        
        Returns:
            List[str]: 配置文件名列表（不含扩展名）
        """
        files = []
        if os.path.exists(self.config_dir):
            for file in os.listdir(self.config_dir):
                if file.endswith('.yaml'):
                    files.append(file[:-5])  # 去掉.yaml后缀
        return files
    
    def __str__(self) -> str:
        return f"ConfigManager(config_dir='{self.config_dir}')"
    
    def __repr__(self) -> str:
        return self.__str__() 