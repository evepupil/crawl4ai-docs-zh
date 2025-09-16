"""
命令行接口，处理命令行参数和用户交互
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, List, Optional

from docslib_detector.core.detector_manager import DetectorManager
from docslib_core.utils import get_logger

def parse_args():
    """
    解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(
        description='检测文档仓库使用的框架类型',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        'repo_path',
        help='文档仓库的本地路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出结果的文件路径，默认输出到控制台'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['json', 'text'],
        default='text',
        help='输出格式：json或text'
    )
    
    parser.add_argument(
        '-t', '--threshold',
        type=float,
        default=0.5,
        help='检测置信度阈值，范围0-1'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='输出详细日志'
    )
    
    parser.add_argument(
        '--no-log-file',
        action='store_true',
        help='不生成日志文件'
    )
    
    parser.add_argument(
        '--log-file',
        help='指定日志文件路径'
    )
    
    return parser.parse_args()

def format_output(detection_summary: Dict[str, Any], format_type: str) -> str:
    """
    格式化检测结果输出
    
    Args:
        detection_summary: 检测结果摘要
        format_type: 输出格式，'json'或'text'
        
    Returns:
        str: 格式化后的输出字符串
    """
    if format_type == 'json':
        return json.dumps(detection_summary, ensure_ascii=False, indent=2)
    
    # 文本格式输出
    lines = []
    lines.append("文档仓库框架检测结果")
    lines.append("=" * 30)
    lines.append(f"仓库路径: {detection_summary['repo_path']}")
    lines.append(f"检测器数量: {detection_summary['total_detectors']}")
    lines.append(f"匹配数量: {detection_summary['matched_detectors']}")
    lines.append("")
    
    if detection_summary['best_match']:
        best = detection_summary['best_match']
        lines.append("最佳匹配:")
        lines.append(f"  框架: {best['name']}")
        lines.append(f"  类型: {best['framework_type']}")
        lines.append(f"  置信度: {best['confidence']:.2f}")
        lines.append("")
        lines.append("详细信息:")
        
        for key, value in best['details'].items():
            lines.append(f"  {key}: {value}")
    else:
        lines.append("未检测到匹配的文档框架")
    
    if detection_summary['all_matches']:
        lines.append("")
        lines.append("所有匹配:")
        for match in detection_summary['all_matches']:
            lines.append(f"  {match['name']} ({match['framework_type']}): {match['confidence']:.2f}")
    
    return "\n".join(lines)

def main():
    """命令行入口函数"""
    args = parse_args()
    
    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_file = None if args.no_log_file else args.log_file
    logger = get_logger("docslib_detector", log_level, log_file)
    
    logger.info(f"开始检测仓库: {args.repo_path}")
    
    try:
        # 检测仓库
        detector_manager = DetectorManager(args.repo_path, logger)
        detector_manager.detect(args.threshold)
        
        # 获取检测结果
        detection_summary = detector_manager.get_detection_summary()
        
        # 格式化输出
        output = format_output(detection_summary, args.format)
        
        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            logger.info(f"检测结果已保存到: {args.output}")
        else:
            print(output)
        
        # 返回状态码
        if detection_summary['best_match']:
            return 0
        else:
            return 1
    
    except Exception as e:
        logger.error(f"检测过程中发生错误: {str(e)}", exc_info=args.verbose)
        return 2

if __name__ == "__main__":
    sys.exit(main()) 