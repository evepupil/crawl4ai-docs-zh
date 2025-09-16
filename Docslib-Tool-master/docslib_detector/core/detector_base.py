"""
检测器基础类，定义所有文档框架检测器的通用接口
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple

class DetectorBase(ABC):
    """
    文档框架检测器的基础抽象类
    
    所有具体的框架检测器都应该继承这个类并实现其方法
    """
    
    def __init__(self, repo_path: str, logger: Optional[logging.Logger] = None):
        """
        初始化检测器
        
        Args:
            repo_path: 文档仓库的本地路径
            logger: 可选的日志记录器，如果不提供则创建新的
        """
        self.repo_path = os.path.abspath(repo_path)
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # 检查路径是否存在
        if not os.path.exists(self.repo_path):
            raise ValueError(f"仓库路径不存在: {self.repo_path}")
        
        # 检测结果和置信度
        self._confidence = 0.0
        self._detection_results = {}
    
    @property
    def name(self) -> str:
        """返回检测器名称"""
        return self.__class__.__name__
    
    @property
    def framework_type(self) -> str:
        """返回文档框架类型"""
        return "unknown"
    
    @property
    def confidence(self) -> float:
        """返回检测置信度，范围0-1"""
        return self._confidence
    
    @property
    def detection_results(self) -> Dict[str, Any]:
        """返回检测的详细结果"""
        return self._detection_results
    
    @abstractmethod
    def detect(self) -> bool:
        """
        执行检测逻辑，判断是否为该类型的文档框架
        
        Returns:
            bool: 如果是该类型框架返回True，否则返回False
        """
        pass
    
    @abstractmethod
    def get_framework_info(self) -> Dict[str, Any]:
        """
        获取文档框架的详细信息
        
        Returns:
            Dict[str, Any]: 包含框架版本、配置等信息的字典
        """
        pass
    
    def file_exists(self, relative_path: str) -> bool:
        """
        检查仓库中是否存在指定文件
        
        Args:
            relative_path: 相对于仓库根目录的文件路径
            
        Returns:
            bool: 文件存在返回True，否则返回False
        """
        full_path = os.path.join(self.repo_path, relative_path)
        return os.path.isfile(full_path)
    
    def dir_exists(self, relative_path: str) -> bool:
        """
        检查仓库中是否存在指定目录
        
        Args:
            relative_path: 相对于仓库根目录的目录路径
            
        Returns:
            bool: 目录存在返回True，否则返回False
        """
        full_path = os.path.join(self.repo_path, relative_path)
        return os.path.isdir(full_path)
    
    def read_file(self, relative_path: str) -> Optional[str]:
        """
        读取仓库中指定文件的内容
        
        Args:
            relative_path: 相对于仓库根目录的文件路径
            
        Returns:
            Optional[str]: 文件内容，如果文件不存在则返回None
        """
        full_path = os.path.join(self.repo_path, relative_path)
        if not os.path.isfile(full_path):
            self.logger.warning(f"文件不存在: {relative_path}")
            return None
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"读取文件失败 {relative_path}: {str(e)}")
            return None
    
    def list_files(self, relative_dir: str = '', pattern: str = None) -> List[str]:
        """
        列出仓库中指定目录下的所有文件
        
        Args:
            relative_dir: 相对于仓库根目录的目录路径
            pattern: 可选的文件名匹配模式
            
        Returns:
            List[str]: 文件路径列表
        """
        import fnmatch
        
        full_dir = os.path.join(self.repo_path, relative_dir)
        if not os.path.isdir(full_dir):
            self.logger.warning(f"目录不存在: {relative_dir}")
            return []
        
        result = []
        for root, _, files in os.walk(full_dir):
            for file in files:
                if pattern and not fnmatch.fnmatch(file, pattern):
                    continue
                rel_path = os.path.relpath(os.path.join(root, file), self.repo_path)
                result.append(rel_path)
        
        return result
    
    def __str__(self) -> str:
        """返回检测器的字符串表示"""
        return f"{self.name} (confidence: {self.confidence:.2f})" 