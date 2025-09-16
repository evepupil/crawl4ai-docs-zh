"""
检测器管理器模块

提供文档框架检测的主要接口
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple

# 导入检测器
from docslib_detector.detectors.mkdocs import MkDocsDetector
from docslib_detector.detectors.docusaurus import DocusaurusDetector
from docslib_detector.detectors.readthedocs import ReadTheDocsDetector
from docslib_detector.detectors.gitbook import GitBookDetector

# 导入核心日志模块
from docslib_core.utils import get_logger

def detect_framework(repo_path: str, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    检测文档项目的框架类型
    
    Args:
        repo_path: 文档项目的路径
        logger: 可选的日志记录器
        
    Returns:
        Dict[str, Any]: 包含检测结果的字典，包括框架类型、版本等信息
    """
    # 创建日志记录器
    if logger is None:
        logger = get_logger("DocsLibDetector")
    
    logger.info(f"开始检测文档项目框架: {repo_path}")
    
    # 检查路径是否存在
    if not os.path.exists(repo_path):
        logger.error(f"项目路径不存在: {repo_path}")
        return {"framework": "unknown", "error": "项目路径不存在"}
    
    # 创建所有检测器
    detectors = [
        MkDocsDetector(repo_path, logger),
        DocusaurusDetector(repo_path, logger),
        ReadTheDocsDetector(repo_path, logger),
        GitBookDetector(repo_path, logger)
    ]
    
    # 运行所有检测器
    results = []
    for detector in detectors:
        logger.info(f"运行检测器: {detector.name}")
        try:
            is_match = detector.detect()
            if is_match:
                results.append((detector.framework_type, detector.confidence, detector))
        except Exception as e:
            logger.error(f"检测器 {detector.name} 运行出错: {str(e)}")
    
    # 如果没有检测到任何框架
    if not results:
        logger.warning("未检测到任何已知的文档框架")
        return {"framework": "unknown", "confidence": 0.0}
    
    # 按置信度排序
    results.sort(key=lambda x: x[1], reverse=True)
    
    # 获取最高置信度的检测结果
    framework_type, confidence, detector = results[0]
    
    # 获取框架详细信息
    framework_info = detector.get_framework_info()
    framework_info["confidence"] = confidence
    
    logger.info(f"检测完成，框架类型: {framework_type}，置信度: {confidence:.2f}")
    
    return framework_info

def detect_files(source_dir: str, extensions: List[str], exclude_patterns: List[str], 
                logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    检测项目中的文件
    
    Args:
        source_dir: 源目录
        extensions: 文件扩展名列表
        exclude_patterns: 排除模式列表
        logger: 可选的日志记录器
        
    Returns:
        Dict[str, Any]: 包含检测到的文件信息
    """
    # 创建日志记录器
    if logger is None:
        logger = get_logger("DocsLibDetector")
    
    logger.info(f"开始检测文件: {source_dir}")
    logger.info(f"文件扩展名: {extensions}")
    logger.info(f"排除模式: {exclude_patterns}")
    
    files = []
    
    # 遍历目录查找文件
    for root, dirs, filenames in os.walk(source_dir):
        # 排除目录
        dirs[:] = [d for d in dirs if not any(pattern in os.path.join(root, d) for pattern in exclude_patterns)]
        
        # 处理文件
        for filename in filenames:
            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, source_dir)
            
            # 检查是否应该排除
            if any(pattern in rel_path for pattern in exclude_patterns):
                continue
            
            # 检查扩展名
            _, ext = os.path.splitext(filename)
            if ext in extensions:
                files.append({
                    'path': file_path,
                    'relative_path': rel_path,
                    'extension': ext,
                    'size': os.path.getsize(file_path)
                })
    
    logger.info(f"检测到 {len(files)} 个文件")
    
    return {'files': files} 