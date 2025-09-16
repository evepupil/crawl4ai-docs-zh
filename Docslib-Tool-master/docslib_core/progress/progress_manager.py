"""
翻译进度管理器模块

负责管理和存储项目翻译进度，包括文件翻译和特殊文件翻译的进度
"""

import os
import json
import time
import logging
import threading
import datetime
from enum import Enum
from typing import Dict, List, Set, Any, Optional, Tuple, Union

# 导入配置管理器
from docslib_core.config import get_config_manager
from docslib_core.utils import get_logger

# 定义文件状态枚举
class FileStatus(str, Enum):
    """文件翻译状态枚举（简化版）"""
    UNTRANSLATED = "untranslated"  # 未翻译
    TRANSLATED = "translated"      # 已翻译

# 全局进度管理器实例
_progress_manager_instance = None
_progress_manager_lock = threading.RLock()

def get_progress_manager(project_id: str = None) -> 'ProgressManager':
    """
    获取进度管理器实例
    
    Args:
        project_id: 项目ID，如果为None则使用默认ID
        
    Returns:
        ProgressManager: 进度管理器实例
    """
    global _progress_manager_instance
    
    if _progress_manager_instance is None:
        with _progress_manager_lock:
            if _progress_manager_instance is None:
                _progress_manager_instance = ProgressManager(project_id)
    
    return _progress_manager_instance

class ProgressManager:
    """翻译进度管理器，用于记录和管理项目翻译进度"""
    
    def __init__(self, project_id: Optional[str] = None):
        """
        初始化进度管理器
        
        Args:
            project_id: 项目ID，如果为None则使用默认ID
        """
        # 获取配置管理器
        self.config_manager = get_config_manager()
        
        # 获取配置
        self.config = self.config_manager.get_config('default')
        
        # 获取日志记录器
        self.logger = get_logger('docslib_core.progress', self.config.get('logging', {}))
        
        # 项目ID
        self.project_id = project_id or "default"
        
        # 数据目录
        self.data_dir = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            'data'
        ))
        
        # 进度数据目录
        self.progress_dir = os.path.join(self.data_dir, 'progress')
        
        # 确保目录存在
        os.makedirs(self.progress_dir, exist_ok=True)
        
        # 进度文件路径
        self.progress_file = os.path.join(self.progress_dir, f"{self.project_id}.json")
        
        # 进度数据
        self.progress_data = {
            'project_id': self.project_id,
            'start_time': self._format_time(datetime.datetime.now()),
            'last_update_time': self._format_time(datetime.datetime.now()),
            'status': 'not_started',  # not_started, in_progress, completed, failed
            'files': {},              # 文件进度
            'special_files': {},      # 特殊文件进度
            'stats': {
                'total_files': 0,
                'translated_files': 0,
                'total_special_files': 0,
                'translated_special_files': 0
            }
        }
        
        # 加载已有的进度数据
        self._load_progress()
        
        # 线程锁，用于保护并发访问
        self.lock = threading.RLock()
        
        self.logger.info(f"初始化进度管理器，项目ID: {self.project_id}")
    
    def _format_time(self, dt: datetime.datetime) -> str:
        """
        格式化时间为易读格式
        
        Args:
            dt: 时间对象
            
        Returns:
            str: 格式化的时间字符串，例如：'2023-06-01 14:30:25'
        """
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    
    def _load_progress(self) -> None:
        """加载进度数据"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 更新进度数据
                    if data and isinstance(data, dict):
                        self.progress_data.update(data)
                        
                        # 确保统计数据一致
                        self._update_stats()
                        
                        self.logger.info(f"加载进度数据: {self.progress_file}")
                    else:
                        self.logger.warning(f"进度文件格式不正确: {self.progress_file}")
                
            except Exception as e:
                self.logger.error(f"加载进度数据失败: {str(e)}")
        else:
            self.logger.info(f"未找到进度文件，将创建新的进度数据: {self.progress_file}")
    
    def _save_progress(self) -> None:
        """保存进度数据"""
        try:
            # 更新最后更新时间
            self.progress_data['last_update_time'] = self._format_time(datetime.datetime.now())
            
            # 确保目录存在
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
            
            # 保存数据
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, ensure_ascii=False, indent=2)
                
            self.logger.debug(f"保存进度数据: {self.progress_file}")
            
        except Exception as e:
            self.logger.error(f"保存进度数据失败: {str(e)}")
    
    def _update_stats(self) -> None:
        """更新统计数据"""
        files = self.progress_data['files']
        special_files = self.progress_data['special_files']
        
        stats = {
            'total_files': len(files),
            'translated_files': sum(1 for _, status in files.items() if status['status'] == FileStatus.TRANSLATED),
            'total_special_files': len(special_files),
            'translated_special_files': sum(1 for _, status in special_files.items() if status['status'] == FileStatus.TRANSLATED)
        }
        
        self.progress_data['stats'] = stats
    
    def start_project(self) -> None:
        """开始项目翻译"""
        with self.lock:
            # 如果已经开始，则不再重复操作
            if self.progress_data['status'] in ['in_progress', 'completed']:
                return
            
            self.progress_data['start_time'] = self._format_time(datetime.datetime.now())
            self.progress_data['status'] = 'in_progress'
            self._save_progress()
            
            self.logger.info(f"开始项目翻译: {self.project_id}")
    
    def complete_project(self) -> None:
        """完成项目翻译"""
        with self.lock:
            self.progress_data['status'] = 'completed'
            self._update_stats()
            self._save_progress()
            
            self.logger.info(f"完成项目翻译: {self.project_id}")
    
    def fail_project(self, reason: str = None) -> None:
        """标记项目翻译失败"""
        with self.lock:
            self.progress_data['status'] = 'failed'
            if reason:
                self.progress_data['failure_reason'] = reason
            self._update_stats()
            self._save_progress()
            
            self.logger.info(f"项目翻译失败: {self.project_id}, 原因: {reason}")
    
    def save(self) -> None:
        """手动保存进度数据"""
        with self.lock:
            self._update_stats()
            self._save_progress()
    
    def register_files(self, files: List[str], file_type: str = 'normal') -> None:
        """
        注册需要翻译的文件
        
        Args:
            files: 文件相对路径列表
            file_type: 文件类型，normal或special
        """
        with self.lock:
            container = self.progress_data['files'] if file_type == 'normal' else self.progress_data['special_files']
            
            # 添加新文件
            current_time = self._format_time(datetime.datetime.now())
            for file_path in files:
                # 如果文件已存在，则不覆盖
                if file_path not in container:
                    container[file_path] = {
                        'status': FileStatus.UNTRANSLATED,
                        'register_time': current_time,
                        'complete_time': None,
                        'error': None
                    }
            
            self._update_stats()
            self._save_progress()
            
            type_name = "普通文件" if file_type == 'normal' else "特殊文件"
            self.logger.info(f"注册{type_name}: {len(files)}个")
    
    def update_file_status(self, file_path: str, status: FileStatus, 
                          error: str = None, file_type: str = 'normal') -> None:
        """
        更新文件翻译状态
        
        Args:
            file_path: 文件相对路径
            status: 文件状态（已翻译或未翻译）
            error: 错误信息，如果有的话
            file_type: 文件类型，normal或special
        """
        with self.lock:
            container = self.progress_data['files'] if file_type == 'normal' else self.progress_data['special_files']
            
            if file_path not in container:
                # 如果文件不存在，则添加它
                container[file_path] = {
                    'status': status,
                    'register_time': self._format_time(datetime.datetime.now()),
                    'complete_time': self._format_time(datetime.datetime.now()) if status == FileStatus.TRANSLATED else None,
                    'error': error
                }
            else:
                # 更新状态
                file_info = container[file_path]
                old_status = file_info['status']
                
                # 如果从未翻译变为已翻译，记录完成时间
                if status == FileStatus.TRANSLATED and old_status != FileStatus.TRANSLATED:
                    file_info['complete_time'] = self._format_time(datetime.datetime.now())
                
                # 如果有错误，更新错误信息
                if error:
                    file_info['error'] = error
                
                file_info['status'] = status
            
            self._update_stats()
            # 每次更新文件状态后实时保存进度
            self._save_progress()
            
            type_name = "文件" if file_type == 'normal' else "特殊文件"
            self.logger.debug(f"更新{type_name}状态: {file_path} -> {status}")
    
    def get_file_status(self, file_path: str, file_type: str = 'normal') -> Optional[Dict[str, Any]]:
        """
        获取文件翻译状态
        
        Args:
            file_path: 文件相对路径
            file_type: 文件类型，normal或special
            
        Returns:
            Optional[Dict[str, Any]]: 文件状态信息，如果文件不存在则返回None
        """
        with self.lock:
            container = self.progress_data['files'] if file_type == 'normal' else self.progress_data['special_files']
            return container.get(file_path)
    
    def get_files_by_status(self, status: Union[FileStatus, List[FileStatus]], 
                           file_type: str = 'normal') -> List[str]:
        """
        获取指定状态的文件列表
        
        Args:
            status: 文件状态或状态列表
            file_type: 文件类型，normal或special
            
        Returns:
            List[str]: 符合条件的文件路径列表
        """
        with self.lock:
            container = self.progress_data['files'] if file_type == 'normal' else self.progress_data['special_files']
            
            if isinstance(status, list):
                return [path for path, info in container.items() if info['status'] in status]
            else:
                return [path for path, info in container.items() if info['status'] == status]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取进度统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        with self.lock:
            self._update_stats()
            return self.progress_data['stats'].copy()
    
    def get_progress_percentage(self) -> float:
        """
        获取总体进度百分比
        
        Returns:
            float: 进度百分比，0-100
        """
        with self.lock:
            self._update_stats()
            stats = self.progress_data['stats']
            
            total = stats['total_files'] + stats['total_special_files']
            if total == 0:
                return 0.0
            
            translated = stats['translated_files'] + stats['translated_special_files']
            return (translated / total) * 100.0
    
    def reset(self) -> None:
        """重置进度数据"""
        with self.lock:
            # 重置数据
            self.progress_data = {
                'project_id': self.project_id,
                'start_time': self._format_time(datetime.datetime.now()),
                'last_update_time': self._format_time(datetime.datetime.now()),
                'status': 'not_started',
                'files': {},
                'special_files': {},
                'stats': {
                    'total_files': 0,
                    'translated_files': 0,
                    'total_special_files': 0,
                    'translated_special_files': 0
                }
            }
            
            # 保存重置后的数据
            self._save_progress()
            
            self.logger.info(f"重置项目进度: {self.project_id}")
    
    def get_failed_files(self, file_type: str = 'normal') -> List[Tuple[str, str]]:
        """
        获取翻译失败的文件列表及错误信息
        
        Args:
            file_type: 文件类型，normal或special
            
        Returns:
            List[Tuple[str, str]]: 文件路径和错误信息的元组列表
        """
        with self.lock:
            container = self.progress_data['files'] if file_type == 'normal' else self.progress_data['special_files']
            return [(path, info['error']) for path, info in container.items() 
                   if info['status'] == FileStatus.UNTRANSLATED and info['error']]
    
    def __enter__(self):
        """支持上下文管理器"""
        self.start_project()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        if exc_type is not None:
            self.fail_project(str(exc_val))
        else:
            self.complete_project()
        
        # 保存进度
        self.save() 