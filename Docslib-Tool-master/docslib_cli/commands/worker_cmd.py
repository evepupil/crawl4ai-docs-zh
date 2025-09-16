"""
文档工作器命令模块

提供 docslib_worker 的命令行接口，用于调用文档翻译功能。
"""

import os
import sys
import argparse
import time
from typing import Dict, List, Any, Optional, Callable

# 确保可以导入其他模块
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from docslib_worker.translators import get_translator_by_type, get_available_translators
    from docslib_core.config import get_config_manager
    from docslib_detector import detect_framework
    from docslib_translator import ParallelTranslator
    WORKER_AVAILABLE = True
except ImportError:
    WORKER_AVAILABLE = False

from ..utils.cli_utils import (
    print_success, print_error, print_warning, print_info, print_header,
    print_json, print_yaml, ProgressBar, confirm_action, select_option, get_input
)

def check_worker_available() -> bool:
    """
    检查文档工作器模块是否可用
    
    Returns:
        bool: 文档工作器模块是否可用
    """
    if not WORKER_AVAILABLE:
        print_error("无法导入 docslib_worker 模块，请确保已正确安装")
        print_info("可以使用以下命令安装：")
        print_info("pip install docslib-worker")
        return False
    return True

def translate_docs_cmd(args: argparse.Namespace) -> int:
    """
    翻译文档命令
    
    Args:
        args: 命令行参数
        
    Returns:
        int: 退出码
    """
    if not check_worker_available():
        return 1
    
    # 获取参数
    source_path = os.path.abspath(args.source)
    target_path = os.path.abspath(args.target) if args.target else None
    config_path = os.path.abspath(args.config) if args.config else None
    framework_type = args.framework
    target_lang = args.target_lang
    workers = args.workers
    
    # 检查源路径是否存在
    if not os.path.exists(source_path):
        print_error(f"源文档路径不存在: {source_path}")
        return 1
    
    # 获取配置以确定目标语言
    config_manager = get_config_manager()
    config = config_manager.get_config('default')
    
    # 如果指定了目标语言，则更新配置
    if target_lang:
        config['global']['target_lang'] = target_lang
    
    # 获取目标语言（从命令行参数或配置中）
    target_lang = config['global']['target_lang']
    
    # 如果未指定目标路径，则使用与源路径相同的目录名
    # 子目录的语言后缀将由翻译器处理
    if not target_path:
        # 判断源路径是文件还是目录
        if os.path.isdir(source_path):
            # 源路径是目录，使用相同的目录名
            source_dir = os.path.dirname(source_path)
            source_name = os.path.basename(source_path)
            target_path = os.path.join(source_dir, source_name)
        else:
            # 源路径是文件，使用相同的文件名
            target_path = source_path
    
    # 确认是否覆盖目标路径
    if os.path.exists(target_path) and not args.force:
        if not confirm_action(f"目标路径 {target_path} 已存在，内容可能会被覆盖，是否继续?"):
            print_info("操作已取消")
            return 0
    
    # 获取可用的翻译器类型
    available_translators = get_available_translators()
    
    # 调试信息：打印可用的翻译器
    print_info("可用的翻译器:")
    for t, info in available_translators.items():
        print_info(f"  - {t}: {info['description']}")
        if info.get('is_default'):
            print_info("    (默认翻译器)")
    
    # 如果未指定框架类型，则使用检测器检测
    if not framework_type:
        print_info(f"检测文档框架类型: {source_path}")
        try:
            # 使用外部检测器检测框架类型
            framework_info = detect_framework(source_path)
            detected_type = framework_info.get("framework")
            
            # 调试信息：打印检测到的框架类型
            print_info(f"检测器返回的框架类型: {detected_type}")
            print_info(f"检测器返回的完整信息: {framework_info}")
            
            # 将检测到的框架类型转换为小写，以匹配翻译器注册时使用的名称
            if detected_type:
                detected_type = detected_type.lower()
                print_info(f"转换为小写后的框架类型: {detected_type}")

            if detected_type and detected_type != "unknown" and detected_type in available_translators:
                framework_type = detected_type
                print_info(f"检测到框架类型: {framework_type}")
            else:
                # 调试信息：打印为什么不使用检测到的框架类型
                if not detected_type:
                    print_warning("检测器返回的框架类型为空")
                elif detected_type == "unknown":
                    print_warning("检测器返回的框架类型为 unknown")
                elif detected_type not in available_translators:
                    print_warning(f"检测到的框架类型 {detected_type} 不在可用翻译器列表中")
                
                # 如果检测失败，使用默认翻译器
                default_type = next((t for t, info in available_translators.items()
                                   if info.get('is_default')), None)
                if default_type:
                    framework_type = default_type
                    print_warning(f"未检测到已知的文档框架类型，将使用默认翻译器: {framework_type}")        
                else:
                    print_error("未检测到已知的文档框架类型，且未配置默认翻译器")
                    return 1
        except Exception as e:
            print_error(f"检测框架类型时发生错误: {str(e)}")
            return 1
    
    # 检查指定的框架类型是否可用
    if framework_type not in available_translators:
        print_error(f"不支持的文档框架类型: {framework_type}")
        print_info("可用的框架类型:")
        for t, info in available_translators.items():
            print_info(f"  - {t}: {info['description']}")
        return 1
    
    print_header("文档翻译")
    print_info(f"源路径: {source_path}")
    print_info(f"目标路径: {target_path}")
    print_info(f"文档框架: {framework_type}")
    print_info(f"目标语言: {target_lang}")
    
    if workers > 0:
        print_info(f"并发翻译: 启用 (工作线程数: {workers})")
    else:
        print_info("并发翻译: 禁用")
    
    try:
        # 获取翻译器实例
        translator = get_translator_by_type(
            framework_type,
            source_path=source_path,
            target_path=target_path,
            config_path=config_path
        )
        
        # 开始计时
        start_time = time.time()
        
        # 显示翻译进度
        print_info("正在翻译文档...")
        
        # 根据是否启用并发模式选择不同的翻译方法
        if workers > 0:
            # 创建进度条
            progress_bar = ProgressBar(total=100, prefix="翻译进度", suffix="完成", length=50)
            
            # 定义进度回调函数
            def progress_callback(progress_info):
                percent = progress_info.get('percent', 0)
                progress_bar.update(percent)
            
            # 获取需要翻译的文件列表
            files_to_translate = translator.get_files_to_translate()
            
            # 准备文件对
            file_pairs = []
            for rel_path in files_to_translate:
                source_file = os.path.join(source_path, rel_path)
                target_file = translator.get_target_path(rel_path)
                file_pairs.append((source_file, target_file))
            
            # 创建并行翻译器
            parallel_translator = ParallelTranslator(max_workers=workers)
            
            # 执行并行翻译
            result = parallel_translator.translate_files(file_pairs, progress_callback)
            
            # 翻译后的额外处理
            translator.post_translation()
            
            success = True
        else:
            # 使用普通翻译方法
            success = translator.translate()
        
        # 计算耗时
        elapsed = time.time() - start_time
        
        if success:
            print_success(f"翻译完成，耗时: {elapsed:.2f}秒")
            print_success(f"翻译结果已保存到: {target_path}")
            return 0
        else:
            print_error("翻译过程中发生错误，请查看日志获取详细信息")
            return 1
    
    except Exception as e:
        print_error(f"翻译过程中发生错误: {str(e)}")
        return 1

def manual_translate_cmd(args: argparse.Namespace) -> int:
    """
    手动翻译命令
    
    Args:
        args: 命令行参数
        
    Returns:
        int: 退出码
    """
    if not check_worker_available():
        return 1
    
    # 获取参数
    source_path = os.path.abspath(args.source)
    target_path = os.path.abspath(args.target) if args.target else None
    config_path = os.path.abspath(args.config) if args.config else None
    target_lang = args.target_lang
    workers = args.workers
    
    # 检查源路径是否存在
    if not os.path.exists(source_path):
        print_error(f"源文档路径不存在: {source_path}")
        return 1
    
    # 获取配置以确定目标语言
    config_manager = get_config_manager()
    config = config_manager.get_config('default')
    
    # 如果指定了配置文件，加载它
    if config_path and os.path.exists(config_path):
        try:
            manual_config = config_manager.load_config(config_path)
            # 合并配置
            config = config_manager.merge_configs(config, manual_config)
        except Exception as e:
            print_error(f"加载配置文件失败: {str(e)}")
            return 1
    
    # 尝试加载手动翻译器的配置
    try:
        manual_config = config_manager.get_config('manual_translator')
        # 合并配置
        config = config_manager.merge_configs(config, manual_config)
    except Exception as e:
        print_warning(f"加载手动翻译器配置失败: {str(e)}")
    
    # 如果指定了目标语言，则更新配置
    if target_lang:
        config['global']['target_lang'] = target_lang
    
    # 获取目标语言（从命令行参数或配置中）
    target_lang = config['global']['target_lang']
    
    # 如果未指定目标路径，则使用源路径-目标语言的形式
    if not target_path:
        source_dir = os.path.dirname(source_path)
        source_name = os.path.basename(source_path)
        target_path = os.path.join(source_dir, f"{source_name}-{target_lang}")
    
    # 确认是否覆盖目标路径
    if os.path.exists(target_path) and not args.force:
        if not confirm_action(f"目标路径 {target_path} 已存在，内容可能会被覆盖，是否继续?"):
            print_info("操作已取消")
            return 0
    
    # 处理文件类型参数
    if args.file_types:
        file_types = [f.strip() for f in args.file_types.split(',')]
        if 'manual_translator' not in config:
            config['manual_translator'] = {}
        config['manual_translator']['file_types'] = file_types
        print_info(f"将翻译以下文件类型: {file_types}")
    
    # 处理排除模式参数
    if args.exclude:
        exclude_patterns = [p.strip() for p in args.exclude.split(',')]
        if 'manual_translator' not in config:
            config['manual_translator'] = {}
        config['manual_translator']['exclude_patterns'] = exclude_patterns
        print_info(f"将排除以下模式: {exclude_patterns}")
    
    # 处理复制静态资源参数
    if args.copy_static:
        if 'manual_translator' not in config:
            config['manual_translator'] = {}
        config['manual_translator']['copy_static_assets'] = True
        print_info("将复制静态资源")
    
    # 处理工作线程数参数
    if 'manual_translator' not in config:
        config['manual_translator'] = {}
    config['manual_translator']['max_workers'] = workers
    
    print_header("手动文档翻译")
    print_info(f"源路径: {source_path}")
    print_info(f"目标路径: {target_path}")
    print_info(f"目标语言: {target_lang}")
    
    if workers > 0:
        print_info(f"并发翻译: 启用 (工作线程数: {workers})")
    else:
        print_info("并发翻译: 禁用")
    
    try:
        # 获取翻译器实例
        translator = get_translator_by_type(
            'manual',
            source_path=source_path,
            target_path=target_path,
            config_path=config_path
        )
        
        # 开始计时
        start_time = time.time()
        
        # 显示翻译进度
        print_info("正在翻译文档...")
        
        # 执行翻译
        success = translator.translate()
        
        # 计算耗时
        elapsed = time.time() - start_time
        
        if success:
            print_success(f"翻译完成，耗时: {elapsed:.2f}秒")
            print_success(f"翻译结果已保存到: {target_path}")
            return 0
        else:
            print_error("翻译过程中发生错误，请查看日志获取详细信息")
            return 1
    
    except Exception as e:
        print_error(f"翻译过程中发生错误: {str(e)}")
        return 1

def list_frameworks_cmd(args: argparse.Namespace) -> int:
    """
    列出支持的文档框架命令
    
    Args:
        args: 命令行参数
        
    Returns:
        int: 退出码
    """
    if not check_worker_available():
        return 1
    
    # 获取可用的翻译器类型
    available_translators = get_available_translators()
    
    print_header("支持的文档框架")
    
    if not available_translators:
        print_warning("没有可用的文档框架翻译器")
        return 0
    
    print_info(f"共找到 {len(available_translators)} 个框架翻译器:")
    
    for framework_type, info in available_translators.items():
        translator_class = info['class']
        print_info(f"- {framework_type}: {info['description']}")
        if info.get('is_default'):
            print_info("  (默认翻译器)")
    
    return 0

def register_worker_commands(subparsers: argparse._SubParsersAction) -> None:
    """
    注册文档工作器命令
    
    Args:
        subparsers: 子命令解析器
    """
    # 创建工作器命令解析器
    worker_parser = subparsers.add_parser(
        'worker',
        help='文档工作器命令'
    )
    
    worker_subparsers = worker_parser.add_subparsers(
        dest='worker_command',
        help='工作器子命令'
    )
    
    # 翻译文档命令
    translate_parser = worker_subparsers.add_parser(
        'translate',
        help='翻译文档'
    )
    
    translate_parser.add_argument(
        'source',
        help='源文档目录路径'
    )
    
    translate_parser.add_argument(
        '--target', '-t',
        help='目标翻译文档路径'
    )
    
    translate_parser.add_argument(
        '--config', '-c',
        help='配置文件路径'
    )
    
    translate_parser.add_argument(
        '--framework', '-f',
        help='文档框架类型，如 mkdocs, docusaurus 等'
    )
    
    translate_parser.add_argument(
        '--target-lang', '-l',
        help='目标语言，默认使用配置中的设置'
    )
    
    translate_parser.add_argument(
        '--force',
        action='store_true',
        help='强制覆盖已存在的目标目录'
    )
    
    # 添加并发翻译相关参数
    translate_parser.add_argument(
        '--workers', '-w',
        type=int,
        default=5,
        help='并发翻译的工作线程数，默认为5，设为0则禁用并发翻译'
    )
    
    translate_parser.set_defaults(func=translate_docs_cmd)
    
    # 列出支持的框架命令
    list_parser = worker_subparsers.add_parser(
        'list-frameworks',
        help='列出支持的文档框架'
    )
    
    list_parser.set_defaults(func=list_frameworks_cmd)
    
    # 手动翻译命令
    manual_parser = worker_subparsers.add_parser(
        'manual-translate',
        help='手动翻译指定目录下的文件'
    )
    
    manual_parser.add_argument(
        'source',
        help='源文档目录路径'
    )
    
    manual_parser.add_argument(
        '--target', '-t',
        help='目标翻译文档路径，默认为源目录名-目标语言'
    )
    
    manual_parser.add_argument(
        '--config', '-c',
        help='配置文件路径'
    )
    
    manual_parser.add_argument(
        '--target-lang', '-l',
        help='目标语言，默认使用配置中的设置'
    )
    
    manual_parser.add_argument(
        '--file-types',
        help='要翻译的文件类型，逗号分隔，例如：.md,.txt'
    )
    
    manual_parser.add_argument(
        '--exclude',
        help='要排除的文件或目录模式，逗号分隔'
    )
    
    manual_parser.add_argument(
        '--copy-static',
        action='store_true',
        help='是否复制静态资源'
    )
    
    manual_parser.add_argument(
        '--force',
        action='store_true',
        help='强制覆盖已存在的目标目录'
    )
    
    # 添加并发翻译相关参数
    manual_parser.add_argument(
        '--workers', '-w',
        type=int,
        default=5,
        help='并发翻译的工作线程数，默认为5，设为0则禁用并发翻译'
    )
    
    manual_parser.set_defaults(func=manual_translate_cmd)
    
    # 如果没有提供子命令，则显示帮助信息
    worker_parser.set_defaults(func=lambda args: worker_parser.print_help()) 