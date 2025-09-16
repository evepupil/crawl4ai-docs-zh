"""
配置管理模块

该模块提供统一的配置管理功能，用于加载和访问DocsLib项目的各个组件的配置。
"""

from .config_manager import ConfigManager, get_config_manager

__all__ = ['ConfigManager', 'get_config_manager'] 