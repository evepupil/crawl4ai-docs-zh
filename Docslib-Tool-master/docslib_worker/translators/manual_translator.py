"""
手动翻译器

用于处理特定目录下的特定类型文件的翻译，主要用于解决其他翻译器无法处理的文件
"""

import os
import time
from typing import Dict, List, Any, Optional, Set, Tuple
import shutil
import json
import re

# 导入基础翻译器
from docslib_worker.translators.base_translator import BaseTranslator
from docslib_worker.core.translator_registry import register_translator

# 导入进度管理相关内容
from docslib_core.progress import FileStatus

# 导入并行翻译器
from docslib_translator import ParallelTranslator

@register_translator(framework_type='manual')
class ManualTranslator(BaseTranslator):
    """手动翻译器，用于处理特定目录下的特定类型文件的翻译"""
    
    def __init__(self, source_path: str, target_path: str, config_path: Optional[str] = None):
        """
        初始化手动翻译器
        
        Args:
            source_path: 源文档目录路径
            target_path: 目标翻译文档路径
            config_path: 配置文件路径
        """
        super().__init__(source_path, target_path, config_path)
        
        # 从配置中获取文件类型设置，如果没有则使用默认值
        file_types = self.config.get('manual_translator', {}).get('file_types', ['.md', '.mdx', '.txt'])
        self.translate_extensions = file_types if isinstance(file_types, list) else [file_types]
        
        # 从配置中获取排除模式，如果没有则使用默认值
        exclude_patterns = self.config.get('manual_translator', {}).get('exclude_patterns', [
            '__pycache__', '.git', '.github', 'node_modules', 'venv', '.venv', '.env'
        ])
        self.exclude_patterns = exclude_patterns if isinstance(exclude_patterns, list) else [exclude_patterns]
        
        # 不需要特殊文件处理
        self.special_files = []
        
        self.logger.info(f"初始化手动翻译器，源路径: {source_path}, 目标路径: {target_path}")
        self.logger.info(f"翻译文件类型: {self.translate_extensions}")
        self.logger.info(f"排除模式: {self.exclude_patterns}")
    
    @property
    def framework_type(self) -> str:
        """返回文档框架类型"""
        return "manual"
    
    def get_files_to_translate(self) -> List[str]:
        """
        获取需要翻译的文件列表
        
        Returns:
            List[str]: 需要翻译的文件相对路径列表
        """
        self.logger.info(f"扫描目录: {self.source_path}")
        
        # 获取所有文件
        all_files = []
        
        # 调试计数器
        total_files_count = 0
        excluded_by_pattern_count = 0
        not_translatable_ext_count = 0
        
        for root, dirs, files in os.walk(self.source_path):
            # 过滤排除的目录
            original_dirs_count = len(dirs)
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in self.exclude_patterns)]
            if original_dirs_count > len(dirs):
                self.logger.debug(f"排除了 {original_dirs_count - len(dirs)} 个目录，在 {root}")
            
            # 处理文件
            for file in files:
                total_files_count += 1
                
                # 获取相对路径
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.source_path)
                
                # 检查是否应该排除
                if any(pattern in rel_path for pattern in self.exclude_patterns):
                    excluded_by_pattern_count += 1
                    self.logger.debug(f"排除文件 (模式匹配): {rel_path}")
                    continue
                
                # 检查是否是需要翻译的文件类型
                _, ext = os.path.splitext(file)
                if ext.lower() in self.translate_extensions:
                    all_files.append(rel_path)
                    self.logger.debug(f"添加文件到翻译列表: {rel_path}")
                else:
                    not_translatable_ext_count += 1
                    self.logger.debug(f"排除文件 (不可翻译的扩展名): {rel_path}, 扩展名: {ext.lower()}")
        
        # 更新进度管理器中的文件列表
        self.progress_manager.register_files(all_files, file_type='normal')
        
        # 打印详细的扫描统计信息
        self.logger.info(f"扫描统计: 总文件数: {total_files_count}")
        self.logger.info(f"- 排除的文件 (模式匹配): {excluded_by_pattern_count}")
        self.logger.info(f"- 不可翻译扩展名: {not_translatable_ext_count}")
        self.logger.info(f"- 添加到翻译列表: {len(all_files)}")
        self.logger.info(f"找到 {len(all_files)} 个需要翻译的文件")
        
        return all_files
    
    def get_target_path(self, rel_path: str) -> str:
        """
        获取目标文件路径
        
        Args:
            rel_path: 文件相对路径
            
        Returns:
            str: 目标文件路径
        """
        # 如果未指定目标路径，则使用源路径-目标语言的形式
        if not self.target_path or self.target_path == self.source_path:
            target_lang = self.config.get('global', {}).get('target_lang', 'zh')
            source_dir = os.path.dirname(self.source_path)
            source_name = os.path.basename(self.source_path)
            self.target_path = os.path.join(source_dir, f"{source_name}-{target_lang}")
            self.logger.info(f"未指定目标路径，使用默认目标路径: {self.target_path}")
        
        # 构建目标文件路径，保持与源目录相同的结构
        return os.path.join(self.target_path, rel_path)
    
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
            
            if not files_to_translate:
                self.logger.warning("没有找到需要翻译的文件")
                self.progress_manager.complete_project()
                return True
            
            # 显示初始翻译状态
            stats = self.progress_manager.get_stats()
            total_files = stats['total_files']
            translated_files = stats['translated_files']
            remaining_files = total_files - translated_files
            percent_complete = (translated_files / total_files * 100) if total_files > 0 else 0
            
            self.logger.info(
                f"翻译开始 - 总文件数: {total_files} - 已翻译: {translated_files} "
                f"({percent_complete:.2f}%) - 剩余: {remaining_files} 个文件"
            )
            
            # 使用并行翻译
            max_workers = self.config.get('manual_translator', {}).get('max_workers', 5)
            if max_workers > 0:
                self.logger.info(f"使用并行翻译，最大线程数: {max_workers}")
                
                # 准备文件对
                file_pairs = []
                for rel_path in files_to_translate:
                    source_file = os.path.join(self.source_path, rel_path)
                    target_file = self.get_target_path(rel_path)
                    
                    # 确保目标目录存在
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    
                    file_pairs.append((source_file, target_file))
                
                # 创建并行翻译器
                parallel_translator = ParallelTranslator(max_workers=max_workers)
                
                # 定义进度回调函数
                def progress_callback(progress_info):
                    percent = progress_info.get('percent', 0)
                    completed = progress_info.get('completed', 0)
                    total = progress_info.get('total', 0)
                    
                    # 更新文件状态
                    for i in range(completed):
                        if i < len(files_to_translate):
                            self.progress_manager.update_file_status(
                                files_to_translate[i], 
                                FileStatus.TRANSLATED, 
                                file_type='normal'
                            )
                
                # 执行并行翻译
                result = parallel_translator.translate_files(file_pairs, progress_callback)
                
                # 检查翻译结果
                if result.get('failed', 0) > 0:
                    self.logger.warning(f"有 {result.get('failed', 0)} 个文件翻译失败")
                
                self.logger.info(
                    f"翻译完成 - 成功: {result.get('translated_files', 0)} 个文件, "
                    f"失败: {result.get('failed_files', 0)} 个文件"
                )
            else:
                # 使用单线程翻译
                self.logger.info("使用单线程翻译")
                
                # 翻译每个文件
                success_count = 0
                fail_count = 0
                
                for i, rel_path in enumerate(files_to_translate):
                    source_file = os.path.join(self.source_path, rel_path)
                    target_file = self.get_target_path(rel_path)
                    
                    # 确保目标目录存在
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    
                    self.logger.info(f"正在翻译文件 ({i+1}/{len(files_to_translate)}): {rel_path}")
                    
                    try:
                        # 检查是否是JSON文件
                        _, ext = os.path.splitext(source_file)
                        if ext.lower() == '.json':
                            # 使用专门的JSON翻译方法
                            result = self._translate_json_file(source_file, target_file)
                        else:
                            # 使用普通翻译方法
                            result = self.translator.translate_file(source_file, target_file)
                        
                        # 更新文件状态
                        if result['success'] and os.path.exists(target_file):
                            self.progress_manager.update_file_status(rel_path, FileStatus.TRANSLATED, file_type='normal')
                            success_count += 1
                            
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
                            fail_count += 1
                    except Exception as e:
                        error_msg = f"翻译文件异常: {rel_path}: {str(e)}"
                        self.logger.error(error_msg, exc_info=True)
                        self.progress_manager.update_file_status(rel_path, FileStatus.UNTRANSLATED, error=error_msg, file_type='normal')
                        fail_count += 1
                
                self.logger.info(f"翻译完成 - 成功: {success_count} 个文件, 失败: {fail_count} 个文件")
            
            # 完成项目
            self.progress_manager.complete_project()
            return True
            
        except Exception as e:
            self.logger.error(f"翻译过程中发生错误: {str(e)}", exc_info=True)
            self.progress_manager.fail_project(f"翻译过程中发生错误: {str(e)}")
            return False
            
    def _translate_json_file(self, source_file: str, target_file: str) -> Dict[str, Any]:
        """
        翻译JSON文件，只翻译其中的label字段
        
        Args:
            source_file: 源文件路径
            target_file: 目标文件路径
            
        Returns:
            Dict[str, Any]: 翻译结果信息
        """
        self.logger.info(f"翻译JSON文件: {source_file}")
        
        try:
            # 读取JSON文件
            with open(source_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # 递归翻译JSON中的label字段
            self._translate_json_labels(json_data)
            
            # 写入翻译后的JSON
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'char_count': len(str(json_data)),
                'elapsed': 0
            }
        except Exception as e:
            self.logger.error(f"翻译JSON文件失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _translate_json_labels(self, data: Any) -> None:
        """
        递归翻译JSON中的label字段
        
        Args:
            data: JSON数据
        """
        if isinstance(data, dict):
            # 如果是字典，检查是否有label字段
            for key, value in data.items():
                if key == 'label' and isinstance(value, str):
                    # 翻译label字段
                    data[key] = self.translator.translate_text(value)
                    self.logger.debug(f"翻译label: {value} -> {data[key]}")
                elif isinstance(value, (dict, list)):
                    # 递归处理嵌套的字典或列表
                    self._translate_json_labels(value)
        elif isinstance(data, list):
            # 如果是列表，递归处理每个元素
            for item in data:
                self._translate_json_labels(item)
    
    def process_special_files(self, files: List[str]) -> bool:
        """
        手动翻译器不需要处理特殊文件
        
        Args:
            files: 特殊文件相对路径列表
            
        Returns:
            bool: 总是返回True
        """
        return True
    
    def post_translation(self) -> None:
        """
        翻译后的额外处理
        
        手动翻译器不需要额外处理
        """
        self.logger.info("手动翻译完成")
    
    def copy_static_assets(self) -> None:
        """
        复制静态资源
        
        手动翻译器默认不复制静态资源，如果需要可以在配置中开启
        """
        copy_static = self.config.get('manual_translator', {}).get('copy_static_assets', False)
        if not copy_static:
            self.logger.info("跳过复制静态资源")
            return
        
        self.logger.info("复制静态资源")
        
        # 定义静态资源扩展名
        static_extensions = self.config.get('manual_translator', {}).get('static_extensions', [
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
            '.css', '.scss', '.less',
            '.woff', '.woff2', '.eot', '.ttf', '.otf',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
        ])
        
        # 统计计数器
        copied_count = 0
        skipped_count = 0
        
        # 遍历源目录
        for root, dirs, files in os.walk(self.source_path):
            # 过滤排除的目录
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in self.exclude_patterns)]
            
            # 处理文件
            for file in files:
                # 获取相对路径
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.source_path)
                
                # 检查是否应该排除
                if any(pattern in rel_path for pattern in self.exclude_patterns):
                    skipped_count += 1
                    continue
                
                # 检查是否是静态资源
                _, ext = os.path.splitext(file)
                if ext.lower() in static_extensions:
                    # 获取目标路径
                    target_file = self.get_target_path(rel_path)
                    
                    # 确保目标目录存在
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    
                    # 复制文件
                    try:
                        shutil.copy2(file_path, target_file)
                        copied_count += 1
                        self.logger.debug(f"复制静态资源: {rel_path}")
                    except Exception as e:
                        self.logger.error(f"复制静态资源失败: {rel_path}: {str(e)}")
        
        self.logger.info(f"静态资源复制完成，共复制 {copied_count} 个文件，跳过 {skipped_count} 个文件") 