#!/usr/bin/env python
"""
DocsLib CLI 工具主入口

该模块提供命令行界面的主入口点。
"""

import os
import sys
import argparse
from typing import List, Optional

# 确保可以导入其他模块
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from docslib_cli.commands import register_translator_commands, register_worker_commands
from docslib_cli.utils.cli_utils import print_header, print_error, print_info

def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器
    
    Returns:
        argparse.ArgumentParser: 参数解析器
    """
    parser = argparse.ArgumentParser(
        description='DocsLib 命令行工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 添加版本信息
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    # 创建子命令解析器
    subparsers = parser.add_subparsers(
        dest='command',
        help='可用命令'
    )
    
    # 注册翻译器命令
    register_translator_commands(subparsers)
    
    # 注册文档工作器命令
    register_worker_commands(subparsers)
    
    return parser

def main(args: Optional[List[str]] = None) -> int:
    """
    主函数
    
    Args:
        args: 命令行参数列表，如果为 None 则使用 sys.argv
        
    Returns:
        int: 退出码
    """
    parser = create_parser()
    args = parser.parse_args(args)
    
    # 如果没有提供命令，显示帮助信息
    if not args.command:
        print_header("DocsLib 命令行工具")
        print_info("使用 -h 或 --help 查看帮助信息")
        parser.print_help()
        return 0
    
    # 执行对应的命令
    if hasattr(args, 'func'):
        return args.func(args)
    else:
        print_error(f"未知命令: {args.command}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 