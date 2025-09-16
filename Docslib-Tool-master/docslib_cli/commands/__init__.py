"""
DocsLib CLI 工具 - 命令模块

该模块包含 CLI 工具的各种命令实现。
"""

from .translator_cmd import register_translator_commands
from .worker_cmd import register_worker_commands

__all__ = ['register_translator_commands', 'register_worker_commands'] 