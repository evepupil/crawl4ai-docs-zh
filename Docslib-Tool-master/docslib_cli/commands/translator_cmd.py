"""
翻译器命令模块

提供 docslib_translator 的命令行接口。
"""

import os
import sys
import argparse
import time
from typing import Dict, List, Any, Optional, Callable
import logging

# 确保可以导入其他模块
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from docslib_translator import Translator, ParallelTranslator
    from docslib_translator.config import get_translator_config
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

from ..utils.cli_utils import (
    print_success, print_error, print_warning, print_info, print_header,
    print_json, print_yaml, ProgressBar, confirm_action, select_option, get_input
)

def check_translator_available() -> bool:
    """
    检查翻译器模块是否可用
    
    Returns:
        bool: 翻译器模块是否可用
    """
    if not TRANSLATOR_AVAILABLE:
        print_error("无法导入 docslib_translator 模块，请确保已正确安装")
        print_info("可以使用以下命令安装：")
        print_info("pip install docslib-translator")
        return False
    return True

def translate_text_cmd(args: argparse.Namespace) -> int:
    """
    翻译文本命令
    
    Args:
        args: 命令行参数
        
    Returns:
        int: 退出码
    """
    if not check_translator_available():
        return 1
    
    # 获取参数
    text = args.text
    source_lang = args.source_lang
    target_lang = args.target_lang
    model = args.model
    
    # 如果文本为空，从标准输入读取
    if not text:
        print_info("从标准输入读取文本...")
        text = sys.stdin.read().strip()
        
    if not text:
        print_error("没有提供要翻译的文本")
        return 1
    
    print_header("文本翻译")
    print_info(f"源语言: {source_lang}")
    print_info(f"目标语言: {target_lang}")
    print_info(f"模型: {model}")
    print_info(f"文本长度: {len(text)} 字符")
    
    try:
        # 创建翻译器
        translator = Translator()
        
        # 开始计时
        start_time = time.time()
        
        # 翻译文本
        print_info("正在翻译...")
        translated_text = translator.translate_text(
            text, 
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        # 计算耗时
        elapsed = time.time() - start_time
        
        print_success(f"翻译完成，耗时: {elapsed:.2f}秒")
        print("\n--- 翻译结果 ---\n")
        print(translated_text)
        print("\n-----------------\n")
        
        return 0
    
    except Exception as e:
        print_error(f"翻译过程中发生错误: {str(e)}")
        return 1

def translate_file_cmd(args: argparse.Namespace) -> int:
    """
    翻译文件命令
    
    Args:
        args: 命令行参数
        
    Returns:
        int: 退出码
    """
    if not check_translator_available():
        return 1
    
    # 获取参数
    source_file = args.source
    target_file = args.target
    source_lang = args.source_lang
    target_lang = args.target_lang
    model = args.model
    
    # 检查源文件是否存在
    if not os.path.exists(source_file):
        print_error(f"源文件不存在: {source_file}")
        return 1
    
    # 如果目标文件未指定，则使用源文件名加上目标语言后缀
    if not target_file:
        file_name, file_ext = os.path.splitext(source_file)
        target_file = f"{file_name}.{target_lang}{file_ext}"
    
    # 确认是否覆盖目标文件
    if os.path.exists(target_file) and not args.force:
        if not confirm_action(f"目标文件 {target_file} 已存在，是否覆盖?"):
            print_info("操作已取消")
            return 0
    
    print_header("文件翻译")
    print_info(f"源文件: {source_file}")
    print_info(f"目标文件: {target_file}")
    print_info(f"源语言: {source_lang}")
    print_info(f"目标语言: {target_lang}")
    print_info(f"模型: {model}")
    
    try:
        # 读取源文件
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print_info(f"文件大小: {len(content)} 字符")
        
        # 创建翻译器
        translator = Translator()
        
        # 开始计时
        start_time = time.time()
        
        # 翻译文本
        print_info("正在翻译...")
        translated_content = translator.translate_text(
            content, 
            source_lang=source_lang,
            target_lang=target_lang,
            file_path=source_file
        )
        
        # 计算耗时
        elapsed = time.time() - start_time
        
        # 写入目标文件
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(translated_content)
        
        print_success(f"翻译完成，耗时: {elapsed:.2f}秒")
        print_success(f"已保存到: {target_file}")
        
        return 0
    
    except Exception as e:
        print_error(f"翻译过程中发生错误: {str(e)}")
        return 1

def translate_files_cmd(args: argparse.Namespace) -> int:
    """
    批量翻译文件命令
    
    Args:
        args: 命令行参数
        
    Returns:
        int: 退出码
    """
    if not check_translator_available():
        return 1
    
    # 获取参数
    source_dir = args.source_dir
    target_dir = args.target_dir
    file_pattern = args.pattern
    source_lang = args.source_lang
    target_lang = args.target_lang
    workers = args.workers
    
    # 检查源目录是否存在
    if not os.path.exists(source_dir):
        print_error(f"源目录不存在: {source_dir}")
        return 1
    
    # 如果目标目录未指定，则使用源目录名加上目标语言后缀
    if not target_dir:
        target_dir = f"{source_dir}_{target_lang}"
    
    # 确认是否覆盖目标目录
    if os.path.exists(target_dir) and not args.force:
        if not confirm_action(f"目标目录 {target_dir} 已存在，是否覆盖?"):
            print_info("操作已取消")
            return 0
    
    # 创建目标目录
    os.makedirs(target_dir, exist_ok=True)
    
    print_header("批量文件翻译")
    print_info(f"源目录: {source_dir}")
    print_info(f"目标目录: {target_dir}")
    print_info(f"文件模式: {file_pattern}")
    print_info(f"源语言: {source_lang}")
    print_info(f"目标语言: {target_lang}")
    print_info(f"并行工作线程: {workers}")
    
    try:
        # 查找匹配的文件
        import glob
        import os.path
        
        # 构建完整的文件模式
        full_pattern = os.path.join(source_dir, file_pattern)
        files = glob.glob(full_pattern, recursive=True)
        
        if not files:
            print_warning(f"没有找到匹配的文件: {full_pattern}")
            return 0
        
        print_info(f"找到 {len(files)} 个文件")
        
        # 准备翻译任务
        translation_tasks = []
        for source_file in files:
            # 计算目标文件路径
            rel_path = os.path.relpath(source_file, source_dir)
            target_file = os.path.join(target_dir, rel_path)
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            
            translation_tasks.append((source_file, target_file))
        
        # 创建并行翻译器
        parallel_translator = ParallelTranslator(max_workers=workers)
        
        # 开始计时
        start_time = time.time()
        
        # 翻译文件
        print_info("正在翻译文件...")
        result = parallel_translator.translate_files(translation_tasks)
        
        # 计算耗时
        elapsed = time.time() - start_time
        
        print_success(f"翻译完成，耗时: {elapsed:.2f}秒")
        print_success(f"成功: {result.get('successful', 0)} 个文件")
        print_warning(f"失败: {result.get('failed', 0)} 个文件")
        
        return 0
    
    except Exception as e:
        print_error(f"翻译过程中发生错误: {str(e)}")
        return 1

def show_config_cmd(args: argparse.Namespace) -> int:
    """
    显示配置命令
    
    Args:
        args: 命令行参数
        
    Returns:
        int: 退出码
    """
    if not check_translator_available():
        return 1
    
    print_header("翻译器配置")
    
    try:
        # 获取配置
        config = get_translator_config()
        
        # 显示配置
        if args.format == 'json':
            print_json(config)
        else:
            print_yaml(config)
        
        return 0
    
    except Exception as e:
        print_error(f"获取配置时发生错误: {str(e)}")
        return 1

def register_translator_commands(subparsers: argparse._SubParsersAction) -> None:
    """
    注册翻译器命令
    
    Args:
        subparsers: 子命令解析器
    """
    # 翻译器命令
    translator_parser = subparsers.add_parser(
        'translator', 
        help='翻译器工具'
    )
    translator_subparsers = translator_parser.add_subparsers(
        dest='translator_command',
        help='翻译器子命令'
    )
    
    # 文本翻译命令
    text_parser = translator_subparsers.add_parser(
        'text', 
        help='翻译文本'
    )
    text_parser.add_argument(
        'text', 
        nargs='?',
        help='要翻译的文本，如果为空则从标准输入读取'
    )
    text_parser.add_argument(
        '--source-lang', '-s',
        default='auto',
        help='源语言 (默认: auto)'
    )
    text_parser.add_argument(
        '--target-lang', '-t',
        default='zh',
        help='目标语言 (默认: zh)'
    )
    text_parser.add_argument(
        '--model', '-m',
        help='翻译模型'
    )
    text_parser.set_defaults(func=translate_text_cmd)
    
    # 文件翻译命令
    file_parser = translator_subparsers.add_parser(
        'file', 
        help='翻译文件'
    )
    file_parser.add_argument(
        'source',
        help='源文件路径'
    )
    file_parser.add_argument(
        'target',
        nargs='?',
        help='目标文件路径 (默认: 源文件名.目标语言后缀)'
    )
    file_parser.add_argument(
        '--source-lang', '-s',
        default='auto',
        help='源语言 (默认: auto)'
    )
    file_parser.add_argument(
        '--target-lang', '-t',
        default='zh',
        help='目标语言 (默认: zh)'
    )
    file_parser.add_argument(
        '--model', '-m',
        help='翻译模型'
    )
    file_parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='强制覆盖现有文件'
    )
    file_parser.set_defaults(func=translate_file_cmd)
    
    # 批量翻译文件命令
    files_parser = translator_subparsers.add_parser(
        'files', 
        help='批量翻译文件'
    )
    files_parser.add_argument(
        'source_dir',
        help='源目录路径'
    )
    files_parser.add_argument(
        'target_dir',
        nargs='?',
        help='目标目录路径 (默认: 源目录名_目标语言)'
    )
    files_parser.add_argument(
        '--pattern', '-p',
        default='**/*.md',
        help='文件匹配模式 (默认: **/*.md)'
    )
    files_parser.add_argument(
        '--source-lang', '-s',
        default='auto',
        help='源语言 (默认: auto)'
    )
    files_parser.add_argument(
        '--target-lang', '-t',
        default='zh',
        help='目标语言 (默认: zh)'
    )
    files_parser.add_argument(
        '--workers', '-w',
        type=int,
        default=5,
        help='并行工作线程数 (默认: 5)'
    )
    files_parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='强制覆盖现有文件'
    )
    files_parser.set_defaults(func=translate_files_cmd)
    
    # 显示配置命令
    config_parser = translator_subparsers.add_parser(
        'config', 
        help='显示翻译器配置'
    )
    config_parser.add_argument(
        '--format',
        choices=['json', 'yaml'],
        default='yaml',
        help='输出格式 (默认: yaml)'
    )
    config_parser.set_defaults(func=show_config_cmd) 