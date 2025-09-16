"""
Docusaurus 框架翻译器

用于翻译 Docusaurus 文档框架的文档和配置文件
"""

import os
import json
import re
from typing import Dict, Any, List, Optional, Tuple
import fnmatch # Added for fnmatch
import shutil
# 导入基础翻译器
from docslib_worker.translators.base_translator import BaseTranslator
from docslib_worker.core.translator_registry import register_translator

# 导入进度管理相关内容
from docslib_core.progress import FileStatus

# 确保使用与检测器相同的框架类型名称
@register_translator(framework_type='docusaurus')
class DocusaurusTranslator(BaseTranslator):
    """Docusaurus 框架翻译器"""
    
    def __init__(self, source_path: str, target_path: str, config_path: Optional[str] = None):
        """
        初始化 Docusaurus 翻译器
        
        Args:
            source_path: 源文档目录路径
            target_path: 目标翻译文档路径
            config_path: 配置文件路径
        """
        super().__init__(source_path, target_path, config_path)
        
        # 加载 Docusaurus 特有配置
        self.docusaurus_config = self.config_manager.get_config('docusaurus_translator').get('docusaurus_translator', {})
        
        # Docusaurus 特有的设置
        self.config_file = 'docusaurus.config.js'
        self.sidebar_file = 'sidebars.js'
        self.sidebar_json_file = 'sidebars.json'  # JSON格式的侧边栏文件
        self.docs_dir = 'docs'  # 默认的文档目录
        self.blog_dir = 'blog'  # 默认的博客目录
        self.i18n_dir = 'i18n'  # 国际化目录
        self.static_dir = 'static'  # 静态资源目录
        self.src_dir = 'src'  # 源码目录
        
        # Docusaurus 框架特定的文件类型设置 - 从配置文件加载
        self.translate_extensions = self.docusaurus_config.get('translate_extensions', 
            ['.md', '.mdx', '.jsx', '.tsx', '.js', '.ts'])
        
        self.special_files = self.docusaurus_config.get('special_files', 
            [self.config_file, self.sidebar_file, self.sidebar_json_file])
        
        self.exclude_patterns = self.docusaurus_config.get('exclude_patterns', [
            '__pycache__', 
            '.git', 
            '.github', 
            'node_modules',
            'build',  # 默认构建目录
            '.docusaurus',  # Docusaurus 缓存目录
            'venv',
            '.venv',
            '.env',
            'translated_docs',  # 已翻译的文档目录
            'versioned_docs',  # 版本化的文档目录（旧版本）
            'node_modules',  # npm 模块
            'lib',  # 编译后的库文件
            'dist'  # 发布目录
        ])
        
        # 可翻译目录列表 - 从配置文件加载
        self.translatable_dirs = self.docusaurus_config.get('translatable_dirs', [
            'docs',          # 标准文档目录
            'blog',          # 博客目录
            'src',           # 源代码目录
            'website/docs',  # 有些项目将文档放在 website/docs 下
            'website/blog',  # 有些项目将博客放在 website/blog 下
            'website/src',   # 有些项目将源代码放在 website/src 下
            'packages/docs', # monorepo 结构中的文档目录
            'website/pages', # 有些旧版本使用 pages 而不是 src/pages
            'i18n',          # 国际化目录
            'content/docs',  # 有些项目使用 content/docs 目录
            'content/blog'   # 有些项目使用 content/blog 目录
        ])
        
        # 静态资源模式 - 从配置文件加载
        self.static_asset_patterns = self.docusaurus_config.get('static_asset_patterns', [
            '*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg', '*.ico',
            '*.css', '*.scss', '*.less',
            '*.woff', '*.woff2', '*.eot', '*.ttf', '*.otf',
            '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx', '*.ppt', '*.pptx'
        ])
        
        # 检测 Docusaurus 配置文件是否存在
        self.config_path = os.path.join(self.source_path, self.config_file)
        if os.path.exists(self.config_path):
            # 加载 Docusaurus 配置
            self._load_docusaurus_config()
        else:
            self.logger.warning(f"未找到 Docusaurus 配置文件: {self.config_path}")
            
        # 记录配置信息
        self.logger.info(f"Docusaurus翻译器配置:")
        self.logger.info(f"- 静态资源复制: {self.docusaurus_config.get('copy_static_assets', True)}")
        self.logger.info(f"- 可翻译文件类型: {len(self.translate_extensions)} 种")
        self.logger.info(f"- 可翻译目录: {len(self.translatable_dirs)} 个")
        self.logger.info(f"- 排除模式: {len(self.exclude_patterns)} 个")
    
    @property
    def framework_type(self) -> str:
        """返回文档框架类型"""
        return "docusaurus"
    
    def get_files_to_translate(self) -> List[str]:
        """
        获取需要翻译的文件列表
        
        Returns:
            List[str]: 需要翻译的文件相对路径列表
        """
        self.logger.info(f"扫描目录: {self.source_path}")
        
        # 获取所有文件
        all_files = []
        special_files = []
        
        # 调试计数器
        total_files_count = 0
        excluded_by_pattern_count = 0
        special_files_count = 0
        not_translatable_ext_count = 0
        not_in_translatable_dir_count = 0
        
        # 打印排除模式，便于调试
        self.logger.info(f"排除模式: {self.exclude_patterns}")
        self.logger.info(f"可翻译扩展名: {self.translate_extensions}")
        self.logger.info(f"可翻译目录: {self.translatable_dirs}")
        
        # 用于检测同名文件
        file_paths_by_name = {}
        
        for root, dirs, files in os.walk(self.source_path):
            # 打印当前处理的目录和文件数量
            rel_root = os.path.relpath(root, self.source_path)
            self.logger.debug(f"处理目录: {rel_root}，包含 {len(files)} 个文件")
            
            # 过滤排除的目录 - 使用宽松的匹配方式
            original_dirs_count = len(dirs)
            # 只排除完全匹配的目录名
            dirs[:] = [d for d in dirs if d not in self.exclude_patterns]
            if original_dirs_count > len(dirs):
                self.logger.debug(f"排除了 {original_dirs_count - len(dirs)} 个目录，在 {rel_root}")
            
            # 处理文件
            for file in files:
                total_files_count += 1
                
                # 获取相对路径
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.source_path)
                
                # 检查是否有同名文件
                if file in file_paths_by_name:
                    file_paths_by_name[file].append(rel_path)
                else:
                    file_paths_by_name[file] = [rel_path]
                
                # 检查是否应该排除 - 使用宽松的匹配方式
                should_exclude = False
                for pattern in self.exclude_patterns:
                    # 只排除完全匹配的文件名
                    if file == pattern:
                        should_exclude = True
                        break
                
                if should_exclude:
                    excluded_by_pattern_count += 1
                    self.logger.debug(f"排除文件 (模式匹配): {rel_path}")
                    continue
                
                # 检查是否是特殊文件
                if file in self.special_files:
                    special_files.append(rel_path)
                    special_files_count += 1
                    self.logger.debug(f"添加特殊文件: {rel_path}")
                    continue
                
                # 检查是否是需要翻译的文件类型
                _, ext = os.path.splitext(file)
                if ext.lower() in self.translate_extensions:
                    # 检查文件是否在可翻译目录中
                    rel_path_norm = os.path.normpath(rel_path)
                    rel_dir = os.path.dirname(rel_path_norm)
                    
                    # 更灵活的目录匹配逻辑
                    is_translatable = False
                    
                    # 1. 直接检查是否在可翻译目录列表中
                    if any(rel_dir == dir or rel_dir.startswith(f"{dir}{os.sep}") for dir in self.translatable_dirs):
                        is_translatable = True
                    
                    # 2. 检查文件路径是否包含可翻译目录（对于嵌套结构）
                    if not is_translatable:
                        for dir in self.translatable_dirs:
                            dir_parts = dir.split('/')
                            rel_parts = rel_path_norm.split(os.sep)
                            
                            # 检查是否有任何部分匹配
                            for i in range(len(rel_parts) - len(dir_parts) + 1):
                                if rel_parts[i:i+len(dir_parts)] == dir_parts:
                                    is_translatable = True
                                    break
                            
                            if is_translatable:
                                break
                    
                    # 3. 特殊处理：对于根目录下的markdown文件，也应该翻译
                    if not is_translatable and rel_dir == '' and ext.lower() in ['.md', '.mdx']:
                        is_translatable = True
                        self.logger.debug(f"特殊处理：根目录下的markdown文件: {rel_path}")
                        
                    # 4. 特殊处理：对于JS/TS文件，只翻译src/pages目录下的文件
                    if not is_translatable and ext.lower() in ['.js', '.ts'] and ('src/pages' in rel_path_norm or 'src\\pages' in rel_path_norm):
                        is_translatable = True
                    
                    if is_translatable:
                        all_files.append(rel_path)
                        self.logger.debug(f"添加文件到翻译列表: {rel_path}")
                    else:
                        not_in_translatable_dir_count += 1
                        self.logger.debug(f"排除文件 (不在可翻译目录中): {rel_path}, 目录: {rel_dir}")
                else:
                    not_translatable_ext_count += 1
                    self.logger.debug(f"排除文件 (不可翻译的扩展名): {rel_path}, 扩展名: {ext.lower()}")
        
        # 检查同名文件并输出警告
        duplicate_files = {name: paths for name, paths in file_paths_by_name.items() if len(paths) > 1}
        if duplicate_files:
            self.logger.warning(f"检测到 {len(duplicate_files)} 个同名文件:")
            for name, paths in duplicate_files.items():
                if any(path in all_files for path in paths):
                    self.logger.warning(f"  - {name}: {', '.join(paths)}")
        
        # 更新进度管理器中的文件列表
        self.progress_manager.register_files(all_files, file_type='normal')
        self.progress_manager.register_files(special_files, file_type='special')
        
        # 打印详细的扫描统计信息
        self.logger.info(f"扫描统计: 总文件数: {total_files_count}")
        self.logger.info(f"- 排除的文件 (模式匹配): {excluded_by_pattern_count}")
        self.logger.info(f"- 特殊文件: {special_files_count}")
        self.logger.info(f"- 不可翻译扩展名: {not_translatable_ext_count}")
        self.logger.info(f"- 不在可翻译目录中: {not_in_translatable_dir_count}")
        self.logger.info(f"- 添加到翻译列表: {len(all_files)}")
        self.logger.info(f"找到 {len(all_files)} 个需要翻译的普通文件和 {len(special_files)} 个特殊文件")
        
        # 返回所有需要处理的文件（普通文件和特殊文件）
        return all_files + special_files
    
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
        
        # 规范化路径，确保使用正确的路径分隔符
        source_rel_path_norm = os.path.normpath(source_rel_path)
        
        # 解析路径
        rel_dir_parts = source_rel_path_norm.split(os.sep)
        
        # 检查路径是否在需要翻译的子目录中
        if rel_dir_parts and rel_dir_parts[0] in self.translatable_dirs:
            # 修改第一级目录，添加语言后缀
            rel_dir_parts[0] = f"{rel_dir_parts[0]}_{target_lang}"
            # 重建相对路径
            target_rel_path = os.path.join(*rel_dir_parts)
            return os.path.join(self.target_path, target_rel_path)
        
        # 处理特殊情况：检查是否在嵌套的可翻译目录中
        for dir_path in self.translatable_dirs:
            dir_parts = dir_path.split('/')
            if len(rel_dir_parts) >= len(dir_parts):
                # 检查路径前缀是否匹配
                if rel_dir_parts[:len(dir_parts)] == dir_parts:
                    # 找到匹配的目录，修改路径
                    new_rel_dir_parts = rel_dir_parts.copy()
                    new_rel_dir_parts[len(dir_parts)-1] = f"{new_rel_dir_parts[len(dir_parts)-1]}_{target_lang}"
                    target_rel_path = os.path.join(*new_rel_dir_parts)
                    return os.path.join(self.target_path, target_rel_path)
        
        # 如果不在特殊子目录中，则保持原路径不变
        return os.path.join(self.target_path, source_rel_path)
    
    def _load_docusaurus_config(self) -> None:
        """加载 Docusaurus 配置文件"""
        try:
            # 由于 docusaurus.config.js 是 JavaScript 文件，不能直接解析
            # 这里我们只读取文件内容，用于后续处理
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_content = f.read()
                
            # 尝试提取一些基本配置信息
            # 注意：这只是一个简单的正则提取，不是完整的 JS 解析
            
            # 提取 title
            title_match = re.search(r'title:\s*[\'"]([^\'"]+)[\'"]', self.config_content)
            if title_match:
                self.site_title = title_match.group(1)
                self.logger.info(f"站点标题: {self.site_title}")
            
            # 提取 tagline
            tagline_match = re.search(r'tagline:\s*[\'"]([^\'"]+)[\'"]', self.config_content)
            if tagline_match:
                self.site_tagline = tagline_match.group(1)
                self.logger.info(f"站点标语: {self.site_tagline}")
            
            # 尝试提取自定义的文档目录
            docs_path_match = re.search(r'path:\s*[\'"]([^\'"]+)[\'"].*?sidebarPath', self.config_content, re.DOTALL)
            if docs_path_match:
                self.docs_dir = docs_path_match.group(1)
                self.logger.info(f"使用自定义文档目录: {self.docs_dir}")
                
        except Exception as e:
            self.logger.error(f"加载 Docusaurus 配置文件失败: {str(e)}")
            self.config_content = None
    
    def process_special_files(self, files: List[str]) -> bool:
        """
        处理 Docusaurus 特殊文件，主要是 docusaurus.config.js 和 sidebars.js
        
        Args:
            files: 特殊文件相对路径列表
            
        Returns:
            bool: 处理成功返回True，否则返回False
        """
        self.logger.info(f"处理 Docusaurus 特殊文件，共 {len(files)} 个文件")
        success = True
        
        # 获取特殊文件总数
        total_special_files = len(files)
        processed_count = 0
        
        for file_path in files:
            # 获取文件状态
            file_status = self.progress_manager.get_file_status(file_path, file_type='special')
            
            # 如果文件已经处理完成，则跳过
            if file_status and file_status['status'] == FileStatus.TRANSLATED:
                self.logger.info(f"特殊文件已处理，跳过: {file_path}")
                processed_count += 1
                continue
            
            # 更新进度信息
            processed_count += 1
            
            file_name = os.path.basename(file_path)
            if file_name == self.config_file:
                self.logger.info(f"处理 Docusaurus 配置文件 ({processed_count}/{total_special_files}): {file_path}")
                try:
                    if self._translate_docusaurus_config(file_path):
                        # 处理成功
                        self.progress_manager.update_file_status(file_path, FileStatus.TRANSLATED, file_type='special')
                        
                        # 获取当前处理进度
                        stats = self.progress_manager.get_stats()
                        translated_special = stats['translated_special_files']
                        total_special = stats['total_special_files']
                        remaining_special = total_special - translated_special
                        percent_special = (translated_special / total_special * 100) if total_special > 0 else 0
                        
                        # 打印特殊文件处理进度
                        self.logger.info(
                            f"特殊文件处理完成: {file_path} - 进度: {translated_special}/{total_special} "
                            f"({percent_special:.2f}%) - 剩余: {remaining_special} 个特殊文件"
                        )
                    else:
                        # 处理失败
                        error_msg = f"翻译 Docusaurus 配置文件失败: {file_path}"
                        self.logger.error(error_msg)
                        self.progress_manager.update_file_status(file_path, FileStatus.UNTRANSLATED, error=error_msg, file_type='special')
                        success = False
                except Exception as e:
                    error_msg = f"处理 Docusaurus 配置文件异常: {str(e)}"
                    self.logger.error(error_msg, exc_info=True)
                    self.progress_manager.update_file_status(file_path, FileStatus.UNTRANSLATED, error=error_msg, file_type='special')
                    success = False
            elif file_name == self.sidebar_file:
                self.logger.info(f"处理 Docusaurus 侧边栏配置文件 ({processed_count}/{total_special_files}): {file_path}")
                try:
                    if self._translate_sidebar_config(file_path):
                        # 处理成功
                        self.progress_manager.update_file_status(file_path, FileStatus.TRANSLATED, file_type='special')
                        
                        # 获取当前处理进度
                        stats = self.progress_manager.get_stats()
                        translated_special = stats['translated_special_files']
                        total_special = stats['total_special_files']
                        remaining_special = total_special - translated_special
                        percent_special = (translated_special / total_special * 100) if total_special > 0 else 0
                        
                        # 打印特殊文件处理进度
                        self.logger.info(
                            f"特殊文件处理完成: {file_path} - 进度: {translated_special}/{total_special} "
                            f"({percent_special:.2f}%) - 剩余: {remaining_special} 个特殊文件"
                        )
                    else:
                        # 处理失败
                        error_msg = f"翻译 Docusaurus 侧边栏配置文件失败: {file_path}"
                        self.logger.error(error_msg)
                        self.progress_manager.update_file_status(file_path, FileStatus.UNTRANSLATED, error=error_msg, file_type='special')
                        success = False
                except Exception as e:
                    error_msg = f"处理 Docusaurus 侧边栏配置文件异常: {str(e)}"
                    self.logger.error(error_msg, exc_info=True)
                    self.progress_manager.update_file_status(file_path, FileStatus.UNTRANSLATED, error=error_msg, file_type='special')
                    success = False
            elif file_name == self.sidebar_json_file:
                self.logger.info(f"处理 Docusaurus 侧边栏 JSON 文件 ({processed_count}/{total_special_files}): {file_path}")
                try:
                    if self._translate_sidebar_json_config(file_path):
                        # 处理成功
                        self.progress_manager.update_file_status(file_path, FileStatus.TRANSLATED, file_type='special')
                        
                        # 获取当前处理进度
                        stats = self.progress_manager.get_stats()
                        translated_special = stats['translated_special_files']
                        total_special = stats['total_special_files']
                        remaining_special = total_special - translated_special
                        percent_special = (translated_special / total_special * 100) if total_special > 0 else 0
                        
                        # 打印特殊文件处理进度
                        self.logger.info(
                            f"特殊文件处理完成: {file_path} - 进度: {translated_special}/{total_special} "
                            f"({percent_special:.2f}%) - 剩余: {remaining_special} 个特殊文件"
                        )
                    else:
                        # 处理失败
                        error_msg = f"翻译 Docusaurus 侧边栏 JSON 文件失败: {file_path}"
                        self.logger.error(error_msg)
                        self.progress_manager.update_file_status(file_path, FileStatus.UNTRANSLATED, error=error_msg, file_type='special')
                        success = False
                except Exception as e:
                    error_msg = f"处理 Docusaurus 侧边栏 JSON 文件异常: {str(e)}"
                    self.logger.error(error_msg, exc_info=True)
                    self.progress_manager.update_file_status(file_path, FileStatus.UNTRANSLATED, error=error_msg, file_type='special')
                    success = False
            else:
                # 其他特殊文件暂不处理
                self.logger.warning(f"未实现的特殊文件处理 ({processed_count}/{total_special_files}): {file_path}")
                self.progress_manager.update_file_status(file_path, FileStatus.UNTRANSLATED, error="未实现的特殊文件处理", file_type='special')
        
        # 处理完成后打印最终统计信息
        stats = self.progress_manager.get_stats()
        self.logger.info(
            f"特殊文件处理完成: {stats['translated_special_files']}/{stats['total_special_files']} 个文件 "
            f"({stats['translated_special_files']/stats['total_special_files']*100:.2f}%)"
        )
        
        return success
    
    def _translate_docusaurus_config(self, config_rel_path: str) -> bool:
        """
        翻译 Docusaurus 配置文件
        
        Args:
            config_rel_path: 配置文件相对路径
            
        Returns:
            bool: 翻译成功返回True，否则返回False
        """
        try:
            source_config_path = os.path.join(self.source_path, config_rel_path)
            
            # 读取原始配置
            with open(source_config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # 翻译站点标题和标语
            # 注意：这里使用正则表达式替换，因为 JS 文件不能直接解析为对象
            
            # 翻译 title
            title_match = re.search(r'(title:\s*[\'"])([^\'"]+)([\'"])', config_content)
            if title_match:
                original_title = title_match.group(2)
                self.logger.info(f"翻译网站标题: {original_title}")
                translated_title = self.translator.translate_text(original_title)
                config_content = config_content.replace(
                    title_match.group(0),
                    f"{title_match.group(1)}{translated_title}{title_match.group(3)}"
                )
            
            # 翻译 tagline
            tagline_match = re.search(r'(tagline:\s*[\'"])([^\'"]+)([\'"])', config_content)
            if tagline_match:
                original_tagline = tagline_match.group(2)
                self.logger.info(f"翻译网站标语: {original_tagline}")
                translated_tagline = self.translator.translate_text(original_tagline)
                config_content = config_content.replace(
                    tagline_match.group(0),
                    f"{tagline_match.group(1)}{translated_tagline}{tagline_match.group(3)}"
                )
            
            # 翻译导航栏项目
            nav_items_match = re.search(r'(items:\s*\[)(.*?)(\])', config_content, re.DOTALL)
            if nav_items_match:
                nav_items_text = nav_items_match.group(2)
                # 翻译导航项的标签
                label_matches = re.finditer(r'(label:\s*[\'"])([^\'"]+)([\'"])', nav_items_text)
                for match in label_matches:
                    original_label = match.group(2)
                    self.logger.info(f"翻译导航标签: {original_label}")
                    translated_label = self.translator.translate_text(original_label)
                    nav_items_text = nav_items_text.replace(
                        match.group(0),
                        f"{match.group(1)}{translated_label}{match.group(3)}"
                    )
                
                # 更新导航栏内容
                config_content = config_content.replace(
                    nav_items_match.group(0),
                    f"{nav_items_match.group(1)}{nav_items_text}{nav_items_match.group(3)}"
                )
            
            # 修改 i18n 配置，添加目标语言
            target_lang = self.config.get('global', {}).get('target_lang', 'zh')
            
            # 检查是否已有 i18n 配置
            i18n_match = re.search(r'(i18n:\s*\{)(.*?)(\})', config_content, re.DOTALL)
            if i18n_match:
                i18n_config = i18n_match.group(2)
                # 检查是否已包含目标语言
                if f"locale: '{target_lang}'" not in i18n_config and f'locale: "{target_lang}"' not in i18n_config:
                    # 添加目标语言到 locales 数组
                    locales_match = re.search(r'(locales:\s*\[)(.*?)(\])', i18n_config, re.DOTALL)
                    if locales_match:
                        locales = locales_match.group(2)
                        if locales.strip():
                            # 如果已有其他语言，添加逗号和新语言
                            new_locales = f"{locales}, '{target_lang}'"
                        else:
                            # 如果是空数组，直接添加新语言
                            new_locales = f"'{target_lang}'"
                        
                        i18n_config = i18n_config.replace(
                            locales_match.group(0),
                            f"{locales_match.group(1)}{new_locales}{locales_match.group(3)}"
                        )
                    
                    # 更新 i18n 配置
                    config_content = config_content.replace(
                        i18n_match.group(0),
                        f"{i18n_match.group(1)}{i18n_config}{i18n_match.group(3)}"
                    )
            else:
                # 如果没有 i18n 配置，添加一个基本配置
                i18n_config = f"""
  i18n: {{
    defaultLocale: 'en',
    locales: ['en', '{target_lang}'],
  }},"""
                # 在 module.exports 后插入 i18n 配置
                config_content = re.sub(
                    r'(module\.exports\s*=\s*\{)',
                    f"\\1{i18n_config}",
                    config_content
                )
            
            # 获取目标文件路径
            target_config_file = self.get_target_path(config_rel_path)
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(target_config_file), exist_ok=True)
            
            # 保存翻译后的配置
            with open(target_config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            self.logger.info(f"Docusaurus 配置文件翻译完成: {target_config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"翻译 Docusaurus 配置文件失败: {str(e)}", exc_info=True)
            return False
    
    def _translate_sidebar_config(self, sidebar_rel_path: str) -> bool:
        """
        翻译 Docusaurus 侧边栏配置文件
        
        Args:
            sidebar_rel_path: 侧边栏配置文件相对路径
            
        Returns:
            bool: 翻译成功返回True，否则返回False
        """
        try:
            source_sidebar_path = os.path.join(self.source_path, sidebar_rel_path)
            
            # 读取原始配置
            with open(source_sidebar_path, 'r', encoding='utf-8') as f:
                sidebar_content = f.read()
            
            # 翻译侧边栏标签
            # 查找所有的标签定义
            label_matches = re.finditer(r'(label:\s*[\'"])([^\'"]+)([\'"])', sidebar_content)
            for match in label_matches:
                original_label = match.group(2)
                self.logger.info(f"翻译侧边栏标签: {original_label}")
                translated_label = self.translator.translate_text(original_label)
                sidebar_content = sidebar_content.replace(
                    match.group(0),
                    f"{match.group(1)}{translated_label}{match.group(3)}"
                )
            
            # 获取目标文件路径
            target_sidebar_file = self.get_target_path(sidebar_rel_path)
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(target_sidebar_file), exist_ok=True)
            
            # 保存翻译后的配置
            with open(target_sidebar_file, 'w', encoding='utf-8') as f:
                f.write(sidebar_content)
            
            self.logger.info(f"Docusaurus 侧边栏配置文件翻译完成: {target_sidebar_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"翻译 Docusaurus 侧边栏配置文件失败: {str(e)}", exc_info=True)
            return False
    
    def _translate_sidebar_json_config(self, sidebar_rel_path: str) -> bool:
        """
        翻译 Docusaurus 侧边栏 JSON 配置文件
        
        Args:
            sidebar_rel_path: 侧边栏 JSON 配置文件相对路径
            
        Returns:
            bool: 翻译成功返回True，否则返回False
        """
        try:
            source_sidebar_path = os.path.join(self.source_path, sidebar_rel_path)
            
            # 读取原始配置
            with open(source_sidebar_path, 'r', encoding='utf-8') as f:
                sidebar_content = f.read()
            
            # 解析 JSON 内容
            sidebar_data = json.loads(sidebar_content)
            
            # 递归翻译侧边栏项目
            self._translate_sidebar_json_items(sidebar_data)
            
            # 将翻译后的 JSON 内容写回文件
            target_sidebar_file = self.get_target_path(sidebar_rel_path)
            os.makedirs(os.path.dirname(target_sidebar_file), exist_ok=True)
            with open(target_sidebar_file, 'w', encoding='utf-8') as f:
                json.dump(sidebar_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Docusaurus 侧边栏 JSON 配置文件翻译完成: {target_sidebar_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"翻译 Docusaurus 侧边栏 JSON 配置文件失败: {str(e)}", exc_info=True)
            return False
    
    def _translate_sidebar_json_items(self, data: Any) -> None:
        """
        递归翻译 JSON 侧边栏中的 label 字段
        
        Args:
            data: JSON 数据
        """
        if isinstance(data, dict):
            # 如果是字典，检查是否有 label 字段
            for key, value in data.items():
                if key == 'label' and isinstance(value, str):
                    # 翻译 label 字段
                    self.logger.info(f"翻译侧边栏 JSON 标签: {value}")
                    data[key] = self.translator.translate_text(value)
                elif isinstance(value, (dict, list)):
                    # 递归处理嵌套的字典或列表
                    self._translate_sidebar_json_items(value)
        elif isinstance(data, list):
            # 如果是列表，递归处理每个元素
            for item in data:
                self._translate_sidebar_json_items(item)
    
    def post_translation(self) -> None:
        """
        翻译后的额外处理
        
        创建i18n目录结构，复制静态资源等
        """
        self.logger.info("执行翻译后处理...")
        
        # 创建i18n目录结构
        self._create_i18n_structure()
        
        # 复制静态资源
        copy_static = self.translator_config.get('copy_static_assets', True)
        if copy_static:
            self.logger.info("复制静态资源...")
            self.copy_static_assets()
        else:
            self.logger.info("已禁用静态资源复制，跳过")
        
        # 复制未翻译的文件
        copy_untranslated = self.translator_config.get('copy_untranslated_files', False)
        if copy_untranslated:
            self.logger.info("复制未翻译文件...")
            self.copy_untranslated_files()
        else:
            self.logger.info("已禁用复制未翻译文件，跳过")
        
        # 复制docs目录下的JSON文件
        self.copy_docs_json_files()
        
        # 复制根目录下的重要文件
        self.copy_important_files()
        
        self.logger.info("翻译后处理完成")
    
    def copy_untranslated_files(self) -> None:
        """
        复制未翻译的文件到目标目录
        
        这个方法会将所有未翻译的文件直接复制到目标目录，保持原始内容
        """
        # 检查是否启用了复制未翻译文件的功能
        if not self.translator_config.get('copy_untranslated_files', False):
            self.logger.info("未启用复制未翻译文件功能，跳过")
            return
        
        self.logger.info("复制未翻译的文件...")
        
        # 获取所有未翻译的文件
        untranslated_files = self.progress_manager.get_files_by_status(FileStatus.UNTRANSLATED, file_type='normal')
        
        if not untranslated_files:
            self.logger.info("没有未翻译的文件需要复制")
            return
        
        self.logger.info(f"找到 {len(untranslated_files)} 个未翻译的文件")
        
        # 复制文件
        copied_count = 0
        skipped_count = 0
        error_count = 0
        
        for rel_path in untranslated_files:
            source_file = os.path.join(self.source_path, rel_path)
            target_file = self.get_target_path(rel_path)
            
            # 检查源文件是否存在
            if not os.path.exists(source_file):
                self.logger.warning(f"源文件不存在，跳过: {source_file}")
                skipped_count += 1
                continue
            
            # 检查目标文件是否已存在
            if os.path.exists(target_file):
                # 检查是否是已翻译的文件（可能是同名文件在不同目录）
                target_rel_path = os.path.relpath(target_file, self.target_path)
                source_rel_path = rel_path
                
                # 使用完整路径检查文件状态
                file_status = self.progress_manager.get_file_status(source_rel_path, file_type='normal')
                if file_status and file_status['status'] == FileStatus.TRANSLATED:
                    self.logger.debug(f"文件已翻译，跳过复制: {source_rel_path}")
                    skipped_count += 1
                    continue
                
                self.logger.debug(f"目标文件已存在，但未翻译，将覆盖: {target_file}")
            
            try:
                # 确保目标目录存在
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                
                # 复制文件
                shutil.copy2(source_file, target_file)
                copied_count += 1
                
                # 更新文件状态
                self.progress_manager.update_file_status(rel_path, FileStatus.TRANSLATED, file_type='normal')
                
                self.logger.debug(f"复制未翻译文件: {rel_path} -> {target_file}")
            except Exception as e:
                self.logger.error(f"复制文件失败: {rel_path}: {str(e)}")
                error_count += 1
        
        self.logger.info(f"复制未翻译文件完成: 复制 {copied_count} 个，跳过 {skipped_count} 个，失败 {error_count} 个")
    
    def copy_static_assets(self, asset_patterns: Optional[List[str]] = None) -> None:
        """
        复制静态资源文件
        
        Args:
            asset_patterns: 静态资源匹配模式列表，如果为None则使用默认配置
        """
        # 检查配置中是否禁用了静态资源复制
        copy_static = self.translator_config.get('copy_static_assets', True)
        if not copy_static:
            self.logger.info("静态资源复制已在配置中禁用，跳过复制")
            return
            
        patterns = asset_patterns or self.static_asset_patterns
        if not patterns:
            self.logger.info("没有定义静态资源模式，跳过复制")
            return
        
        self.logger.info(f"复制静态资源文件")
        
        copied_count = 0
        skipped_count = 0
        error_count = 0
        not_exist_count = 0
        
        # 重要文件列表，这些文件不应该被删除
        important_files = [
            'package.json', 
            'package-lock.json', 
            'yarn.lock', 
            'pnpm-lock.yaml',
            'babel.config.js',
            'tsconfig.json',
            'webpack.config.js',
            'next.config.js',
            'docusaurus.config.js',
            '.gitignore',
            '.npmrc',
            '.yarnrc',
            'README.md',
            'LICENSE'
        ]
        
        for root, dirs, files in os.walk(self.source_path):
            # 过滤排除的目录 - 使用宽松的匹配方式
            # 只排除完全匹配的目录名
            dirs[:] = [d for d in dirs if d not in self.exclude_patterns]
            
            # 计算相对路径
            rel_dir = os.path.relpath(root, self.source_path)
            
            # 复制匹配的文件
            for filename in files:
                rel_path = os.path.join(rel_dir, filename)
                if rel_dir == '.':
                    rel_path = filename
                
                # 检查是否应该排除 - 使用宽松的匹配方式
                should_exclude = False
                for pattern in self.exclude_patterns:
                    # 只排除完全匹配的文件名
                    if filename == pattern:
                        should_exclude = True
                        break
                
                if should_exclude:
                    skipped_count += 1
                    continue
                
                if any(fnmatch.fnmatch(rel_path, pattern) for pattern in patterns):
                    source_file = os.path.join(root, filename)
                    
                    # 检查源文件是否存在
                    if not os.path.exists(source_file):
                        self.logger.debug(f"源文件不存在，跳过: {rel_path}")
                        not_exist_count += 1
                        continue
                    
                    # 使用自定义的get_target_path方法获取目标路径
                    target_file = self.get_target_path(rel_path)
                    
                    try:
                        # 确保目标目录存在
                        os.makedirs(os.path.dirname(target_file), exist_ok=True)
                        
                        try:
                            # 检查目标文件是否已存在
                            if os.path.exists(target_file):
                                # 如果是重要文件，且在根目录，则不删除，跳过复制
                                is_important = filename in important_files and rel_dir == '.'
                                if is_important:
                                    self.logger.info(f"跳过重要文件: {rel_path}")
                                    skipped_count += 1
                                    continue
                                
                                # 只有在文件被占用或无法访问时才尝试删除
                                try:
                                    # 尝试打开文件，看是否可以访问
                                    with open(target_file, 'rb'):
                                        pass
                                    # 如果可以访问，则不需要删除，直接覆盖
                                except (PermissionError, OSError):
                                    # 文件被占用，尝试删除
                                    try:
                                        os.remove(target_file)
                                        self.logger.debug(f"删除被占用的文件: {rel_path}")
                                    except Exception as e:
                                        self.logger.warning(f"无法删除被占用的文件: {rel_path}: {str(e)}")
                                        skipped_count += 1
                                        continue
                            
                            # 复制文件
                            shutil.copy2(source_file, target_file)
                            copied_count += 1
                            self.logger.debug(f"复制静态资源: {rel_path} -> {os.path.relpath(target_file, self.target_path)}")
                        except PermissionError as e:
                            self.logger.error(f"权限错误，无法复制文件: {rel_path}: {str(e)}")
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
        
        self.logger.info(f"静态资源复制完成，共复制 {copied_count} 个文件，跳过 {skipped_count} 个文件，不存在 {not_exist_count} 个文件，失败 {error_count} 个文件")
    
    def _create_i18n_structure(self) -> None:
        """
        创建 Docusaurus i18n 目录结构
        
        Docusaurus 的 i18n 目录结构如下：
        - i18n/
          - [语言代码]/
            - docusaurus-plugin-content-docs/
              - [版本]/
                - [文档文件]
            - docusaurus-plugin-content-blog/
              - [博客文件]
            - docusaurus-theme-classic/
              - navbar.json
              - footer.json
        """
        # 获取目标语言
        target_lang = self.config.get('global', {}).get('target_lang', 'zh')
        
        # 创建 i18n 目录
        i18n_dir = os.path.join(self.target_path, 'i18n', target_lang)
        os.makedirs(i18n_dir, exist_ok=True)
        
        # 创建 docusaurus-plugin-content-docs 目录
        docs_i18n_dir = os.path.join(i18n_dir, 'docusaurus-plugin-content-docs')
        
        # 检查是否有版本目录
        versions_dir = os.path.join(self.source_path, 'versioned_docs')
        if os.path.exists(versions_dir):
            # 有版本目录，创建版本目录
            for version_dir in os.listdir(versions_dir):
                version_i18n_dir = os.path.join(docs_i18n_dir, version_dir)
                os.makedirs(version_i18n_dir, exist_ok=True)
        else:
            # 没有版本目录，创建 current 目录
            current_i18n_dir = os.path.join(docs_i18n_dir, 'current')
            os.makedirs(current_i18n_dir, exist_ok=True)
            
            # 复制已翻译的文档文件到 current 目录
            translated_files = self.progress_manager.get_files_by_status(FileStatus.TRANSLATED, file_type='normal')
            
            # 只处理docs目录下的文件
            docs_files = [f for f in translated_files if f.startswith(f"{self.docs_dir}/") or f.startswith(f"{self.docs_dir}\\")]
            
            # 复制文件
            for rel_path in docs_files:
                # 获取相对于docs目录的路径
                if rel_path.startswith(f"{self.docs_dir}/"):
                    rel_to_docs = rel_path[len(f"{self.docs_dir}/"):]
                else:  # Windows路径
                    rel_to_docs = rel_path[len(f"{self.docs_dir}\\"):]
                
                # 源文件路径（已翻译的文件）
                source_file = self.get_target_path(rel_path)
                
                # 目标文件路径（i18n目录）
                target_file = os.path.join(current_i18n_dir, rel_to_docs)
                
                # 确保目标目录存在
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                
                # 复制文件
                try:
                    shutil.copy2(source_file, target_file)
                    self.logger.debug(f"复制文件到i18n目录: {source_file} -> {target_file}")
                except Exception as e:
                    self.logger.error(f"复制文件到i18n目录失败: {rel_path}: {str(e)}")
        
        # 创建 docusaurus-plugin-content-blog 目录
        blog_i18n_dir = os.path.join(i18n_dir, 'docusaurus-plugin-content-blog')
        os.makedirs(blog_i18n_dir, exist_ok=True)
        
        # 复制已翻译的博客文件到 blog 目录
        translated_files = self.progress_manager.get_files_by_status(FileStatus.TRANSLATED, file_type='normal')
        
        # 只处理blog目录下的文件
        blog_files = [f for f in translated_files if f.startswith(f"{self.blog_dir}/") or f.startswith(f"{self.blog_dir}\\")]
        
        # 复制文件
        for rel_path in blog_files:
            # 获取相对于blog目录的路径
            if rel_path.startswith(f"{self.blog_dir}/"):
                rel_to_blog = rel_path[len(f"{self.blog_dir}/"):]
            else:  # Windows路径
                rel_to_blog = rel_path[len(f"{self.blog_dir}\\"):]
            
            # 源文件路径（已翻译的文件）
            source_file = self.get_target_path(rel_path)
            
            # 目标文件路径（i18n目录）
            target_file = os.path.join(blog_i18n_dir, rel_to_blog)
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            
            # 复制文件
            try:
                shutil.copy2(source_file, target_file)
                self.logger.debug(f"复制文件到i18n目录: {source_file} -> {target_file}")
            except Exception as e:
                self.logger.error(f"复制文件到i18n目录失败: {rel_path}: {str(e)}")
        
        # 创建 docusaurus-theme-classic 目录
        theme_i18n_dir = os.path.join(i18n_dir, 'docusaurus-theme-classic')
        os.makedirs(theme_i18n_dir, exist_ok=True)
        
        self.logger.info(f"创建 Docusaurus i18n 目录结构: {i18n_dir}")

    def translate_file(self, source_file: str, target_file: str) -> Dict[str, Any]:
        """
        翻译单个文件
        
        Args:
            source_file: 源文件路径
            target_file: 目标文件路径
            
        Returns:
            Dict[str, Any]: 翻译结果
        """
        # 获取文件相对路径
        source_rel_path = os.path.relpath(source_file, self.source_path)
        
        # 检查文件是否已经翻译过
        file_status = self.progress_manager.get_file_status(source_rel_path, file_type='normal')
        if file_status and file_status['status'] == FileStatus.TRANSLATED:
            self.logger.debug(f"文件已翻译，跳过: {source_rel_path}")
            return {'success': True, 'message': '文件已翻译'}
        
        # 确保目标目录存在
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        
        # 获取文件扩展名
        _, ext = os.path.splitext(source_file)
        ext = ext.lower()
        
        # 根据文件类型选择翻译方法
        if ext in ['.md', '.mdx']:
            # Markdown 文件
            return self._translate_markdown_file(source_file, target_file)
        elif ext in ['.html', '.htm']:
            # HTML 文件
            return self._translate_html_file(source_file, target_file)
        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
            # JavaScript/TypeScript 文件
            if 'src/pages' in source_rel_path.replace('\\', '/'):
                # 只翻译 src/pages 目录下的 JS/TS 文件
                return self._translate_js_file(source_file, target_file)
            else:
                # 其他 JS/TS 文件直接复制
                try:
                    shutil.copy2(source_file, target_file)
                    return {'success': True, 'message': '文件已复制'}
                except Exception as e:
                    return {'success': False, 'message': f'复制文件失败: {str(e)}'}
        else:
            # 其他文件直接复制
            try:
                shutil.copy2(source_file, target_file)
                return {'success': True, 'message': '文件已复制'}
            except Exception as e:
                return {'success': False, 'message': f'复制文件失败: {str(e)}'} 

    def _translate_markdown_file(self, source_file: str, target_file: str) -> Dict[str, Any]:
        """
        翻译Markdown文件
        
        Args:
            source_file: 源文件路径
            target_file: 目标文件路径
            
        Returns:
            Dict[str, Any]: 翻译结果
        """
        try:
            # 获取文件相对路径（用于日志和错误报告）
            source_rel_path = os.path.relpath(source_file, self.source_path)
            
            # 调用翻译器翻译文件
            self.logger.info(f"翻译Markdown文件: {source_rel_path}")
            result = self.translator.translate_file(source_file, target_file)
            
            if result['success']:
                self.logger.debug(f"Markdown文件翻译成功: {source_rel_path}")
                return {'success': True, 'message': '翻译成功'}
            else:
                self.logger.error(f"Markdown文件翻译失败: {source_rel_path}: {result.get('message', '未知错误')}")
                return {'success': False, 'message': result.get('message', '翻译失败')}
                
        except Exception as e:
            self.logger.error(f"翻译Markdown文件异常: {os.path.relpath(source_file, self.source_path)}: {str(e)}", exc_info=True)
            return {'success': False, 'message': str(e)}
            
    def _translate_html_file(self, source_file: str, target_file: str) -> Dict[str, Any]:
        """
        翻译HTML文件
        
        Args:
            source_file: 源文件路径
            target_file: 目标文件路径
            
        Returns:
            Dict[str, Any]: 翻译结果
        """
        try:
            # 获取文件相对路径（用于日志和错误报告）
            source_rel_path = os.path.relpath(source_file, self.source_path)
            
            # 调用翻译器翻译文件
            self.logger.info(f"翻译HTML文件: {source_rel_path}")
            result = self.translator.translate_file(source_file, target_file)
            
            if result['success']:
                self.logger.debug(f"HTML文件翻译成功: {source_rel_path}")
                return {'success': True, 'message': '翻译成功'}
            else:
                self.logger.error(f"HTML文件翻译失败: {source_rel_path}: {result.get('message', '未知错误')}")
                return {'success': False, 'message': result.get('message', '翻译失败')}
                
        except Exception as e:
            self.logger.error(f"翻译HTML文件异常: {os.path.relpath(source_file, self.source_path)}: {str(e)}", exc_info=True)
            return {'success': False, 'message': str(e)}
            
    def _translate_js_file(self, source_file: str, target_file: str) -> Dict[str, Any]:
        """
        翻译JavaScript/TypeScript文件
        
        Args:
            source_file: 源文件路径
            target_file: 目标文件路径
            
        Returns:
            Dict[str, Any]: 翻译结果
        """
        try:
            # 获取文件相对路径（用于日志和错误报告）
            source_rel_path = os.path.relpath(source_file, self.source_path)
            
            # 调用翻译器翻译文件
            self.logger.info(f"翻译JS/TS文件: {source_rel_path}")
            result = self.translator.translate_file(source_file, target_file)
            
            if result['success']:
                self.logger.debug(f"JS/TS文件翻译成功: {source_rel_path}")
                return {'success': True, 'message': '翻译成功'}
            else:
                self.logger.error(f"JS/TS文件翻译失败: {source_rel_path}: {result.get('message', '未知错误')}")
                return {'success': False, 'message': result.get('message', '翻译失败')}
                
        except Exception as e:
            self.logger.error(f"翻译JS/TS文件异常: {os.path.relpath(source_file, self.source_path)}: {str(e)}", exc_info=True)
            return {'success': False, 'message': str(e)} 

    def copy_docs_json_files(self) -> None:
        """
        复制docs目录下的JSON文件
        
        这个方法会将docs目录下的所有JSON文件复制到目标目录，保持原始内容
        """
        self.logger.info("复制docs目录下的JSON文件...")
        
        # 获取docs目录路径
        docs_dir = os.path.join(self.source_path, self.docs_dir)
        if not os.path.exists(docs_dir):
            self.logger.warning(f"文档目录不存在: {docs_dir}")
            return
        
        # 复制文件
        copied_count = 0
        skipped_count = 0
        error_count = 0
        
        # 遍历docs目录
        for root, dirs, files in os.walk(docs_dir):
            # 过滤排除的目录 - 使用宽松的匹配方式
            # 只排除完全匹配的目录名
            dirs[:] = [d for d in dirs if d not in self.exclude_patterns]
            
            # 计算相对路径
            rel_dir = os.path.relpath(root, self.source_path)
            
            # 处理文件
            for file in files:
                # 只处理JSON文件
                if not file.lower().endswith('.json'):
                    continue
                
                # 获取相对路径
                rel_path = os.path.join(rel_dir, file)
                source_file = os.path.join(self.source_path, rel_path)
                target_file = self.get_target_path(rel_path)
                
                # 检查目标文件是否已存在
                if os.path.exists(target_file):
                    self.logger.debug(f"目标JSON文件已存在，跳过: {rel_path}")
                    skipped_count += 1
                    continue
                
                try:
                    # 确保目标目录存在
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    
                    # 复制文件
                    shutil.copy2(source_file, target_file)
                    copied_count += 1
                    
                    self.logger.debug(f"复制JSON文件: {rel_path} -> {target_file}")
                except Exception as e:
                    self.logger.error(f"复制JSON文件失败: {rel_path}: {str(e)}")
                    error_count += 1
        
        self.logger.info(f"复制docs目录下的JSON文件完成: 复制 {copied_count} 个，跳过 {skipped_count} 个，失败 {error_count} 个") 

    def copy_important_files(self) -> None:
        """
        复制根目录下的重要文件
        
        这个方法会将根目录下的重要文件（如package.json等）复制到目标目录
        """
        self.logger.info("复制根目录下的重要文件...")
        
        # 重要文件列表
        important_files = [
            'package.json', 
            'package-lock.json', 
            'yarn.lock', 
            'pnpm-lock.yaml',
            'babel.config.js',
            'tsconfig.json',
            'webpack.config.js',
            'next.config.js',
            '.gitignore',
            '.npmrc',
            '.yarnrc',
            'README.md',
            'LICENSE'
        ]
        
        # 复制文件
        copied_count = 0
        skipped_count = 0
        error_count = 0
        
        for filename in important_files:
            source_file = os.path.join(self.source_path, filename)
            
            # 检查源文件是否存在
            if not os.path.exists(source_file):
                skipped_count += 1
                continue
            
            # 目标文件路径
            target_file = os.path.join(self.target_path, filename)
            
            try:
                # 复制文件
                shutil.copy2(source_file, target_file)
                copied_count += 1
                self.logger.info(f"复制重要文件: {filename}")
            except Exception as e:
                self.logger.error(f"复制重要文件失败: {filename}: {str(e)}")
                error_count += 1
        
        self.logger.info(f"复制重要文件完成: 复制 {copied_count} 个，跳过 {skipped_count} 个，失败 {error_count} 个") 