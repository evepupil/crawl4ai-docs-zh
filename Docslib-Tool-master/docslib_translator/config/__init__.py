"""
配置模块

该模块包含翻译器的配置文件和提示词。
现在使用统一的配置管理器从项目根目录的config目录加载配置。
"""

import os
import yaml
from typing import Dict, Any

# 导入统一配置管理器
try:
    from docslib_core.config import get_config_manager
    
    def load_config(config_file: str = None) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_file: 配置文件路径，现在忽略此参数，统一使用配置管理器
            
        Returns:
            Dict[str, Any]: 配置信息字典
        """
        # 使用统一配置管理器加载翻译器配置
        config_manager = get_config_manager()
        return config_manager.get_config('translator')
    
    def load_prompts() -> Dict[str, Any]:
        """
        加载翻译提示词
        
        Returns:
            Dict[str, Any]: 不同文件类型的提示词字典
        """
        # 使用统一配置管理器加载提示词配置
        config_manager = get_config_manager()
        return config_manager.get_config('translator_prompts')

except ImportError:
    # 如果统一配置管理器不可用，则使用原始方法加载配置
    def load_config(config_file: str = None) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_file: 配置文件名或路径，默认为None
            
        Returns:
            Dict[str, Any]: 配置信息字典
        """
        # 如果未指定配置文件，则使用默认路径
        if config_file is None:
            # 尝试从项目根目录的config目录加载
            root_config = os.path.abspath(os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'config', 'translator.yaml'
            ))
            if os.path.exists(root_config):
                config_file = root_config
            else:
                # 回退到模块目录
                config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
        
        # 如果是相对路径，则相对于当前目录
        if not os.path.isabs(config_file):
            config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file)
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config

    def load_prompts() -> Dict[str, Any]:
        """
        加载翻译提示词
        
        Returns:
            Dict[str, Any]: 不同文件类型的提示词字典
        """
        # 尝试从项目根目录的config目录加载
        root_prompts = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'config', 'translator_prompts.yaml'
        ))
        
        if os.path.exists(root_prompts):
            prompts_path = root_prompts
        else:
            # 回退到模块目录
            prompts_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prompts.yaml')
        
        if not os.path.exists(prompts_path):
            raise FileNotFoundError(f"提示词配置文件不存在: {prompts_path}")
        
        with open(prompts_path, 'r', encoding='utf-8') as f:
            prompts = yaml.safe_load(f)
        
        return prompts 