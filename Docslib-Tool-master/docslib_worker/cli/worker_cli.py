"""
命令行接口模块

提供从命令行调用翻译功能的接口
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any, Optional, List

# 确保包含项目根目录
project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入翻译管理器
from docslib_worker.core.translation_manager import translate_project

# 导入翻译器注册中心
from docslib_worker.core.translator_registry import list_supported_frameworks

# 导入核心模块的配置管理器和日志管理器
from docslib_core.config import get_config_manager
from docslib_core.utils import get_logger

def main():
    """主函数，解析命令行参数并执行相应操作"""
    parser = argparse.ArgumentParser(description='DocsLib Worker - 文档翻译工具')
    
    # 添加命令行参数
    parser.add_argument('source_path', help='源文档目录路径')
    parser.add_argument('-o', '--output', dest='target_path', help='目标翻译文档路径')
    parser.add_argument('-c', '--config', dest='config_path', help='配置文件路径')
    parser.add_argument('-l', '--log-level', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO', help='日志级别')
    parser.add_argument('-f', '--log-file', dest='log_file', help='日志文件路径')
    parser.add_argument('--framework', dest='framework', help='强制使用指定框架类型')
    parser.add_argument('--list-frameworks', action='store_true', help='列出支持的框架类型')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 获取配置管理器
    config_manager = get_config_manager(os.path.dirname(args.config_path) if args.config_path else None)
    
    # 加载配置
    config = config_manager.get_config('default')
    
    # 获取日志配置
    log_config = config.get('logging', {})
    if args.log_level:
        log_config['level'] = args.log_level
    if args.log_file:
        log_config['file'] = args.log_file
    
    # 设置日志记录器
    logger = get_logger('docslib_worker_cli', log_config)
    
    # 如果需要列出支持的框架类型
    if args.list_frameworks:
        frameworks = list_supported_frameworks()
        print("支持的文档框架类型:")
        for fw in frameworks:
            print(f"  - {fw}")
        return 0
    
    # 检查源路径是否存在
    if not os.path.exists(args.source_path):
        logger.error(f"源文档路径不存在: {args.source_path}")
        return 1
    
    # 执行翻译
    try:
        success = translate_project(
            source_path=args.source_path,
            target_path=args.target_path,
            config_path=args.config_path,
            log_level=args.log_level,
            log_file=args.log_file,
            force_framework=args.framework
        )
        
        if success:
            logger.info("翻译成功完成")
            return 0
        else:
            logger.error("翻译失败")
            return 1
            
    except Exception as e:
        logger.error(f"翻译过程中发生错误: {str(e)}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main()) 