"""
并行翻译器模块

该模块提供基于多线程的并行翻译功能，用于提高翻译效率。
"""

import os
import time
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Tuple, Callable, Union

# 导入翻译器模块
from .translator import Translator, TranslationError

class ParallelTranslator:
    """多线程并行翻译器类"""
    
    def __init__(self, 
                config_file: Optional[str] = None, 
                max_workers: int = 5,
                logger: Optional[logging.Logger] = None):
        """
        初始化多线程翻译器
        
        Args:
            config_file: 翻译器配置文件路径
            max_workers: 最大工作线程数
            logger: 日志记录器，如果为None则创建新的记录器
        """
        self.config_file = config_file
        self.max_workers = max_workers
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # 初始化翻译器
        try:
            self.translator = Translator(config_file=config_file)
            self.logger.info("翻译器初始化成功")
        except Exception as e:
            self.logger.error(f"翻译器初始化失败: {str(e)}", exc_info=True)
            raise
        
        # 线程锁，用于保护共享资源
        self.lock = threading.RLock()
        
        # 翻译任务统计
        self.stats = {
            'total_files': 0,
            'translated_files': 0,
            'failed_files': 0,
            'total_chars': 0,
            'total_tokens': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_time': 0,
            'start_time': None,
            'end_time': None
        }
    
    def translate_files(self, 
                       file_pairs: List[Tuple[str, str]], 
                       progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """
        并行翻译多个文件
        
        Args:
            file_pairs: 输入输出文件路径对列表 [(input_file, output_file), ...]
            progress_callback: 进度回调函数，接收一个字典参数，包含当前进度信息
            
        Returns:
            Dict[str, Any]: 翻译结果统计信息
        """
        self.logger.info(f"开始并行翻译文件，共 {len(file_pairs)} 个文件，最大线程数: {self.max_workers}")
        
        # 重置统计信息
        with self.lock:
            self.stats = {
                'total_files': len(file_pairs),
                'translated_files': 0,
                'failed_files': 0,
                'total_chars': 0,
                'total_tokens': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_time': 0,
                'start_time': time.time(),
                'end_time': None
            }
        
        # 结果列表
        results = []
        
        # 使用线程池并行翻译
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有翻译任务
            future_to_file = {
                executor.submit(self._translate_file_task, input_file, output_file): (input_file, output_file)
                for input_file, output_file in file_pairs
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_file):
                input_file, output_file = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # 更新统计信息
                    with self.lock:
                        if result['success']:
                            self.stats['translated_files'] += 1
                            self.stats['total_chars'] += result.get('char_count', 0)
                            self.stats['total_time'] += result.get('elapsed', 0)
                            self.stats['total_tokens'] += result.get('total_tokens', 0)
                            self.stats['total_input_tokens'] += result.get('input_tokens', 0)
                            self.stats['total_output_tokens'] += result.get('output_tokens', 0)
                        else:
                            self.stats['failed_files'] += 1
                    
                    # 调用进度回调
                    if progress_callback:
                        progress_info = self._get_progress_info()
                        progress_callback(progress_info)
                        
                except Exception as e:
                    self.logger.error(f"翻译文件失败: {input_file} -> {output_file}: {str(e)}", exc_info=True)
                    results.append({
                        'success': False,
                        'input_file': input_file,
                        'output_file': output_file,
                        'error': str(e)
                    })
                    
                    # 更新统计信息
                    with self.lock:
                        self.stats['failed_files'] += 1
                    
                    # 调用进度回调
                    if progress_callback:
                        progress_info = self._get_progress_info()
                        progress_callback(progress_info)
        
        # 更新结束时间
        with self.lock:
            self.stats['end_time'] = time.time()
        
        # 生成最终统计信息
        summary = self._get_summary()
        self.logger.info(
            f"并行翻译完成，成功: {summary['translated_files']}，失败: {summary['failed_files']}，"
            f"总耗时: {summary['elapsed_str']}，总字符: {summary['total_chars']}，"
            f"总tokens: {summary['total_tokens']}，"
            f"速度: {summary.get('chars_per_second', 0):.2f}字符/秒，"
            f"{summary.get('tokens_per_second', 0):.2f}tokens/秒"
        )
        
        return summary
    
    def translate_directory(self, 
                          source_dir: str, 
                          target_dir: str,
                          file_extensions: Optional[List[str]] = None,
                          exclude_patterns: Optional[List[str]] = None,
                          progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """
        并行翻译目录中的文件
        
        Args:
            source_dir: 源目录路径
            target_dir: 目标目录路径
            file_extensions: 要处理的文件扩展名列表，如 ['.md', '.txt']，如果为None则处理所有文件
            exclude_patterns: 要排除的文件/目录模式列表，如 ['node_modules', '.git']
            progress_callback: 进度回调函数
            
        Returns:
            Dict[str, Any]: 翻译结果统计信息
        """
        self.logger.info(f"开始并行翻译目录: {source_dir} -> {target_dir}")
        
        # 默认排除模式
        if exclude_patterns is None:
            exclude_patterns = ['.git', 'node_modules', '__pycache__', '.venv', '.env', '.idea', '.vscode']
        
        # 收集要翻译的文件对
        file_pairs = []
        for root, dirs, files in os.walk(source_dir):
            # 排除指定目录
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            # 处理文件
            for file in files:
                # 检查文件扩展名
                if file_extensions and not any(file.endswith(ext) for ext in file_extensions):
                    continue
                
                # 检查排除模式
                if any(pattern in file for pattern in exclude_patterns):
                    continue
                
                # 构建源文件和目标文件路径
                source_file = os.path.join(root, file)
                rel_path = os.path.relpath(source_file, source_dir)
                target_file = os.path.join(target_dir, rel_path)
                
                file_pairs.append((source_file, target_file))
        
        self.logger.info(f"找到 {len(file_pairs)} 个文件需要翻译")
        
        # 调用translate_files执行翻译
        return self.translate_files(file_pairs, progress_callback)
    
    def _translate_file_task(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        翻译单个文件的任务
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            
        Returns:
            Dict[str, Any]: 翻译结果信息
        """
        self.logger.info(f"开始翻译文件: {input_file} -> {output_file}")
        
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 记录开始时间
            start_time = time.time()
            
            # 使用翻译器翻译文件
            result = self.translator.translate_file(input_file, output_file)
            
            # 记录结束时间
            elapsed = time.time() - start_time
            
            self.logger.info(
                f"文件翻译完成: {input_file}，耗时: {elapsed:.2f}秒，"
                f"字符数: {result.get('char_count', 0)}，"
                f"tokens: {result.get('total_tokens', 0)}"
            )
            
            # 添加耗时信息
            result['elapsed'] = elapsed
            
            return result
            
        except Exception as e:
            self.logger.error(f"翻译文件失败: {input_file}: {str(e)}", exc_info=True)
            return {
                'success': False,
                'input_file': input_file,
                'output_file': output_file,
                'error': str(e)
            }
    
    def _get_progress_info(self) -> Dict[str, Any]:
        """
        获取当前翻译进度信息
        
        Returns:
            Dict[str, Any]: 进度信息
        """
        with self.lock:
            stats = dict(self.stats)
            
            # 计算完成百分比
            total = stats['total_files']
            completed = stats['translated_files'] + stats['failed_files']
            percent = (completed / total * 100) if total > 0 else 0
            
            # 计算已用时间
            elapsed = time.time() - stats['start_time'] if stats['start_time'] else 0
            
            # 估算剩余时间
            if completed > 0 and percent < 100:
                remaining = (elapsed / percent) * (100 - percent)
            else:
                remaining = 0
            
            # 计算速度
            chars_per_second = stats['total_chars'] / elapsed if elapsed > 0 and stats['total_chars'] > 0 else 0
            tokens_per_second = stats['total_tokens'] / elapsed if elapsed > 0 and stats['total_tokens'] > 0 else 0
            
            return {
                'total': total,
                'completed': completed,
                'percent': percent,
                'elapsed': elapsed,
                'remaining': remaining,
                'translated': stats['translated_files'],
                'failed': stats['failed_files'],
                'total_chars': stats['total_chars'],
                'total_tokens': stats['total_tokens'],
                'chars_per_second': chars_per_second,
                'tokens_per_second': tokens_per_second
            }
    
    def _get_summary(self) -> Dict[str, Any]:
        """
        获取翻译结果摘要
        
        Returns:
            Dict[str, Any]: 结果摘要
        """
        with self.lock:
            stats = dict(self.stats)
            
            # 计算总耗时
            elapsed = stats['end_time'] - stats['start_time'] if stats['end_time'] and stats['start_time'] else 0
            
            # 格式化耗时
            minutes, seconds = divmod(elapsed, 60)
            hours, minutes = divmod(minutes, 60)
            elapsed_str = f"{int(hours)}小时{int(minutes)}分{int(seconds)}秒" if hours > 0 else f"{int(minutes)}分{int(seconds)}秒"
            
            # 计算平均翻译速度
            chars_per_second = stats['total_chars'] / elapsed if elapsed > 0 and stats['total_chars'] > 0 else 0
            tokens_per_second = stats['total_tokens'] / elapsed if elapsed > 0 and stats['total_tokens'] > 0 else 0
            
            # 计算平均每个文件的token
            avg_tokens_per_file = stats['total_tokens'] / stats['translated_files'] if stats['translated_files'] > 0 else 0
            
            return {
                'success': stats['failed_files'] == 0,
                'total_files': stats['total_files'],
                'translated_files': stats['translated_files'],
                'failed_files': stats['failed_files'],
                'total_chars': stats['total_chars'],
                'total_tokens': stats['total_tokens'],
                'total_input_tokens': stats['total_input_tokens'],
                'total_output_tokens': stats['total_output_tokens'],
                'elapsed': elapsed,
                'elapsed_str': elapsed_str,
                'chars_per_second': chars_per_second,
                'tokens_per_second': tokens_per_second,
                'avg_tokens_per_file': avg_tokens_per_file,
                'completion_rate': (stats['translated_files'] / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
            }
    
    def get_translator(self) -> Translator:
        """
        获取内部使用的翻译器实例
        
        Returns:
            Translator: 翻译器实例
        """
        return self.translator 