"""
翻译器基类模块

定义了所有翻译器的共同接口和基础功能实现
"""

import os
import re
import shutil
import fnmatch
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple

# 导入翻译器接口
from docslib_worker.core.translator import Translator

# 导入进度管理器
from docslib_core.progress import ProgressManager, get_progress_manager, FileStatus

# 导入工具
from docslib_core.utils import get_logger

class BaseTranslator(ABC):
    """翻译器基类，提供基础翻译功能实现"""
    
    def __init__(self, source_path: str, target_path: str, config_path: Optional[str] = None):
        """
        初始化翻译器
        
        Args:
            source_path: 源文档目录路径
            target_path: 目标翻译文档路径
            config_path: 配置文件路径
        """
        # 源目录和目标目录
        self.source_path = os.path.abspath(source_path)
        self.target_path = os.path.abspath(target_path)
        
        # 从路径中提取项目ID（使用源路径的目录名）
        project_id = os.path.basename(self.source_path)
        
        # 初始化进度管理器
        self.progress_manager = get_progress_manager(project_id)
        
        # 导入配置管理器和配置
        from docslib_core.config import get_config_manager
        self.config_manager = get_config_manager()
        
        # 加载默认配置
        if config_path:
            self.config = self.config_manager.load_config(config_path)
        else:
            self.config = self.config_manager.get_config('default')
        
        # 获取日志记录器
        self.logger = get_logger(f"docslib_worker.translators.{self.name.lower()}", 
                                self.config.get('logging', {}))
        
        # 翻译配置
        self.translator_config = self.config.get('translator', {})
        
        # 确保translatable_dirs存在，这些是需要添加语言后缀的目录
        if 'translatable_dirs' not in self.translator_config:
            self.translator_config['translatable_dirs'] = ['docs', 'blog']
            self.logger.info(f"使用默认的可翻译目录: {self.translator_config['translatable_dirs']}")
        
        # 排除列表
        self.exclude_patterns = self.translator_config.get('exclude_patterns', [])
        
        # 静态资源文件模式
        self.static_asset_patterns = self.translator_config.get('static_asset_patterns', [])
        
        # 特殊文件列表（需要特殊处理的文件）
        self.special_files = self.translator_config.get('special_files', [])
        
        # 翻译器实例
        self._translator = None
        
        self.logger.info(f"初始化翻译器: {self.name}")
        self.logger.info(f"源目录: {self.source_path}")
        self.logger.info(f"目标目录: {self.target_path}")
    
    @property
    def name(self) -> str:
        """返回翻译器名称"""
        return self.__class__.__name__
    
    @property
    def framework_type(self) -> str:
        """返回文档框架类型"""
        return "base"
    
    @property
    def translator(self) -> Translator:
        """获取翻译器实例"""
        if self._translator is None:
            # 动态导入翻译接口工厂
            from docslib_worker.core.translator_factory import create_translator
            
            # 创建翻译器实例
            translator_type = self.translator_config.get('type', 'offline')
            translator_options = self.translator_config.get('options', {})
            
            self.logger.info(f"创建翻译器: {translator_type}")
            self._translator = create_translator(translator_type, **translator_options)
            
            if self._translator is None:
                self.logger.error(f"无法创建翻译器: {translator_type}")
                raise ValueError(f"无法创建翻译器: {translator_type}")
                
        return self._translator
    
    def translate(self) -> bool:
        """
        执行翻译逻辑，将源文档翻译到目标语言
        
        Returns:
            bool: 翻译成功返回True，否则返回False
        """
        try:
            # 开始项目进度记录
            self.progress_manager.start_project()
            
            # 创建目标目录
            if not self.create_target_dir():
                self.logger.error(f"创建目标目录失败: {self.target_path}")
                self.progress_manager.fail_project("创建目标目录失败")
                return False
            
            # 获取需要翻译的文件列表
            files_to_translate = self.get_files_to_translate()
            self.logger.info(f"找到 {len(files_to_translate)} 个需要翻译的文件")
            
            # 显示初始翻译状态
            stats = self.progress_manager.get_stats()
            total_files = stats['total_files'] + stats['total_special_files']
            translated_files = stats['translated_files'] + stats['translated_special_files']
            remaining_files = total_files - translated_files
            percent_complete = (translated_files / total_files * 100) if total_files > 0 else 0
            
            self.logger.info(
                f"翻译开始 - 总文件数: {total_files} - 已翻译: {translated_files} "
                f"({percent_complete:.2f}%) - 剩余: {remaining_files} 个文件"
            )
            
            # 处理常规文件
            regular_files = [f for f in files_to_translate if os.path.basename(f) not in self.special_files]
            
            # 翻译普通文件
            if not self.translate_regular_files(regular_files):
                self.logger.error("翻译普通文件失败")
                self.progress_manager.fail_project("翻译普通文件失败")
                return False
            
            # 处理特殊文件
            special_files = [f for f in files_to_translate if os.path.basename(f) in self.special_files]
            if special_files:
                self.logger.info(f"处理 {len(special_files)} 个特殊文件")
                
                # 处理特殊文件
                if not self.process_special_files(special_files):
                    self.logger.error("处理特殊文件失败")
                    self.progress_manager.fail_project("处理特殊文件失败")
                    return False
            
            # 翻译后的额外处理
            self.post_translation()
            
            # 完成项目进度记录
            self.progress_manager.complete_project()
            
            # 显示最终翻译状态
            final_stats = self.progress_manager.get_stats()
            final_total = final_stats['total_files'] + final_stats['total_special_files']
            final_translated = final_stats['translated_files'] + final_stats['translated_special_files']
            final_percent = (final_translated / final_total * 100) if final_total > 0 else 0
            
            self.logger.info(
                f"翻译完成 - 总文件数: {final_total} - 已翻译: {final_translated} "
                f"({final_percent:.2f}%) - 成功率: {final_translated/final_total*100:.2f}%"
            )
            
            return True
        except Exception as e:
            self.logger.error(f"翻译过程中发生错误: {str(e)}", exc_info=True)
            self.progress_manager.fail_project(str(e))
            return False
    
    def translate_regular_files(self, files: List[str]) -> bool:
        """
        翻译普通文件
        
        Args:
            files: 文件相对路径列表
            
        Returns:
            bool: 翻译成功返回True，否则返回False
        """
        self.logger.info(f"开始翻译 {len(files)} 个常规文件")
        
        # 获取待翻译的文件（过滤已翻译的文件）
        files_to_translate = []
        for rel_path in files:
            file_status = self.progress_manager.get_file_status(rel_path, file_type='normal')
            
            # 如果文件状态不存在或者是未翻译，则加入待翻译列表
            if file_status is None or file_status['status'] == FileStatus.UNTRANSLATED:
                files_to_translate.append(rel_path)
            else:
                self.logger.debug(f"文件已翻译，跳过: {rel_path}")
        
        if not files_to_translate:
            self.logger.info("没有需要翻译的常规文件")
            return True
        
        self.logger.info(f"需要翻译的常规文件: {len(files_to_translate)} 个")
        
        # 准备文件对
        file_pairs = []
        for rel_path in files_to_translate:
            source_file = os.path.join(self.source_path, rel_path)
            target_file = self.get_target_path(rel_path)
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            
            file_pairs.append((source_file, target_file))
        
        # 批量翻译文件
        success = True
        if file_pairs:
            try:
                # 单独翻译每个文件，而不是使用批量翻译
                for i, (source_file, target_file) in enumerate(file_pairs):
                    rel_path = os.path.relpath(source_file, self.source_path)
                    
                    try:
                        # 翻译单个文件
                        self.logger.info(f"正在翻译文件 ({i+1}/{len(file_pairs)}): {rel_path}")
                        result = self.translator.translate_file(source_file, target_file)
                        
                        # 更新文件状态
                        if result['success'] and os.path.exists(target_file):
                            self.progress_manager.update_file_status(rel_path, FileStatus.TRANSLATED, file_type='normal')
                            
                            # 获取当前翻译进度
                            stats = self.progress_manager.get_stats()
                            translated = stats['translated_files']
                            total = stats['total_files']
                            remaining = total - translated
                            percent = (translated / total * 100) if total > 0 else 0
                            
                            # 打印翻译进度信息
                            self.logger.info(
                                f"文件翻译完成: {rel_path} - 进度: {translated}/{total} "
                                f"({percent:.2f}%) - 剩余: {remaining} 个文件"
                            )
                        else:
                            error_msg = f"翻译失败: {rel_path}"
                            self.logger.error(error_msg)
                            self.progress_manager.update_file_status(rel_path, FileStatus.UNTRANSLATED, error=error_msg, file_type='normal')
                            success = False
                    except Exception as e:
                        error_msg = f"翻译文件失败: {rel_path}: {str(e)}"
                        self.logger.error(error_msg, exc_info=True)
                        self.progress_manager.update_file_status(rel_path, FileStatus.UNTRANSLATED, error=error_msg, file_type='normal')
                        success = False
                
                # 翻译完成后打印最终统计信息
                stats = self.progress_manager.get_stats()
                self.logger.info(
                    f"翻译完成: {stats['translated_files']}/{stats['total_files']} 个文件 "
                    f"({stats['translated_files']/stats['total_files']*100:.2f}%)"
                )
                
            except Exception as e:
                error_msg = f"批量翻译文件失败: {str(e)}"
                self.logger.error(error_msg, exc_info=True)
                
                # 标记所有文件为失败
                for source_file, _ in file_pairs:
                    rel_path = os.path.relpath(source_file, self.source_path)
                    self.progress_manager.update_file_status(rel_path, FileStatus.UNTRANSLATED, error=error_msg, file_type='normal')
                
                success = False
        
        return success
    
    @abstractmethod
    def process_special_files(self, files: List[str]) -> bool:
        """
        处理需要特殊处理的文件，如配置文件等
        
        Args:
            files: 特殊文件相对路径列表
            
        Returns:
            bool: 处理成功返回True，否则返回False
        """
        pass
    
    def post_translation(self) -> None:
        """
        翻译后的额外处理，子类可覆盖此方法实现特定框架的处理逻辑
        """
        pass
    
    def create_target_dir(self) -> bool:
        """
        创建目标翻译目录
        
        Returns:
            bool: 创建成功返回True，否则返回False
        """
        try:
            os.makedirs(self.target_path, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"创建目标目录失败 {self.target_path}: {str(e)}")
            return False
    
    @abstractmethod
    def get_files_to_translate(self) -> List[str]:
        """
        获取需要翻译的文件列表
        
        每个具体的翻译器必须实现此方法，根据框架特定的规则选择需要翻译的文件
        
        Returns:
            List[str]: 需要翻译的文件相对路径列表
        """
        pass
    
    def get_target_path(self, source_rel_path: str) -> str:
        """
        获取目标文件路径
        对于需要翻译的子目录（如docs, blog等）添加语言后缀，
        而对其他路径保持原样
        
        Args:
            source_rel_path: 源文件相对路径
            
        Returns:
            str: 目标文件绝对路径
        """
        # 获取目标语言
        target_lang = self.config.get('global', {}).get('target_lang', 'zh')
        
        # 获取需要添加语言后缀的目录列表
        translatable_dirs = self.translator_config.get('translatable_dirs', ['docs', 'blog'])
        
        # 解析路径
        rel_dir_parts = os.path.normpath(source_rel_path).split(os.sep)
        
        # 检查路径是否在需要翻译的子目录中
        if rel_dir_parts and rel_dir_parts[0] in translatable_dirs:
            # 修改第一级目录，添加语言后缀
            rel_dir_parts[0] = f"{rel_dir_parts[0]}_{target_lang}"
            # 重建相对路径
            target_rel_path = os.path.join(*rel_dir_parts)
            return os.path.join(self.target_path, target_rel_path)
        
        # 如果不在特殊子目录中，则保持原路径不变
        return os.path.join(self.target_path, source_rel_path)
    
    @staticmethod
    def is_text_file(file_path: str) -> bool:
        """
        检查文件是否是文本文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 如果是文本文件返回True，否则返回False
        """
        # 文本文件的扩展名列表
        text_extensions = [
            '.md', '.txt', '.html', '.htm', '.xml', '.json', '.yaml', '.yml',
            '.js', '.css', '.scss', '.less', '.py', '.sh', '.bat', '.ps1',
            '.rst', '.adoc', '.tex', '.csv', '.tsv', '.ini', '.conf', '.cfg'
        ]
        
        # 根据扩展名判断
        ext = os.path.splitext(file_path)[1].lower()
        if ext in text_extensions:
            return True
        
        # 对于没有扩展名或扩展名不常见的文件，尝试检查文件内容
        try:
            with open(file_path, 'rb') as f:
                content = f.read(1024)  # 读取前1KB内容
                
                # 检查是否包含空字节（二进制文件通常包含空字节）
                if b'\x00' in content:
                    return False
                
                # 尝试解码为文本
                try:
                    content.decode('utf-8')
                    return True
                except UnicodeDecodeError:
                    try:
                        content.decode('gbk')
                        return True
                    except UnicodeDecodeError:
                        return False
        except:
            return False
    
    def copy_static_assets(self, asset_patterns: Optional[List[str]] = None) -> None:
        """
        复制静态资源文件
        
        Args:
            asset_patterns: 静态资源匹配模式列表，如果为None则使用默认配置
        """
        patterns = asset_patterns or self.static_asset_patterns
        if not patterns:
            self.logger.info("没有定义静态资源模式，跳过复制")
            return
        
        self.logger.info(f"复制静态资源文件")
        
        copied_count = 0
        skipped_count = 0
        error_count = 0
        
        for root, dirs, files in os.walk(self.source_path):
            # 过滤排除的目录
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in getattr(self, 'exclude_patterns', []))]
            
            # 计算相对路径
            rel_dir = os.path.relpath(root, self.source_path)
            
            # 确定目标目录，考虑可翻译目录
            if rel_dir != '.':
                # 将相对路径拆分为部分
                rel_dir_parts = rel_dir.split(os.sep)
                
                # 检查第一部分是否是可翻译目录
                translatable_dirs = self.translator_config.get('translatable_dirs', ['docs', 'blog'])
                target_lang = self.config.get('global', {}).get('target_lang', 'zh')
                
                if rel_dir_parts and rel_dir_parts[0] in translatable_dirs:
                    # 修改第一级目录，添加语言后缀
                    rel_dir_parts[0] = f"{rel_dir_parts[0]}_{target_lang}"
                    # 重建相对路径
                    target_rel_dir = os.path.join(*rel_dir_parts)
                else:
                    target_rel_dir = rel_dir
                
                target_dir = os.path.join(self.target_path, target_rel_dir)
            else:
                target_dir = self.target_path
            
            try:
                # 创建目标目录
                os.makedirs(target_dir, exist_ok=True)
                
                # 复制匹配的文件
                for filename in files:
                    rel_path = os.path.join(rel_dir, filename)
                    if rel_dir == '.':
                        rel_path = filename
                    
                    if any(fnmatch.fnmatch(rel_path, pattern) for pattern in patterns):
                        source_file = os.path.join(root, filename)
                        target_file = os.path.join(target_dir, filename)
                        
                        try:
                            # 确保目标目录存在
                            os.makedirs(os.path.dirname(target_file), exist_ok=True)
                            
                            try:
                                # 如果目标文件已经存在且无法访问，先尝试删除它
                                if os.path.exists(target_file):
                                    try:
                                        os.remove(target_file)
                                    except PermissionError:
                                        self.logger.warning(f"目标文件被占用，无法删除: {rel_path}")
                                        skipped_count += 1
                                        continue
                                    except Exception as e:
                                        self.logger.warning(f"删除目标文件失败: {rel_path}: {str(e)}")
                                
                                # 复制文件
                                shutil.copy2(source_file, target_file)
                                copied_count += 1
                                self.logger.debug(f"复制静态资源: {rel_path} -> {os.path.relpath(target_file, self.target_path)}")
                            except PermissionError as e:
                                self.logger.error(f"权限错误，文件可能被占用: {rel_path}: {str(e)}")
                                error_count += 1
                            except FileNotFoundError as e:
                                self.logger.error(f"文件不存在: {rel_path}: {str(e)}")
                                error_count += 1
                            except Exception as e:
                                self.logger.error(f"复制文件失败: {rel_path}: {str(e)}")
                                error_count += 1
                        except Exception as e:
                            self.logger.error(f"创建目标目录失败: {os.path.dirname(target_file)}: {str(e)}")
                            error_count += 1
                    else:
                        skipped_count += 1
            except Exception as e:
                self.logger.error(f"创建目标目录失败: {target_dir}: {str(e)}")
                error_count += 1
        
        self.logger.info(f"静态资源复制完成，共复制 {copied_count} 个文件，跳过 {skipped_count} 个文件，失败 {error_count} 个文件")
    
    def __str__(self) -> str:
        """返回翻译器的字符串表示"""
        return f"{self.name}(source={self.source_path}, target={self.target_path})" 