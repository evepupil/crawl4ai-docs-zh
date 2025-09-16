"""
MkDocs框架翻译器

用于翻译MkDocs文档框架的文档和配置文件
"""

import os
import yaml
from typing import Dict, Any, List, Optional, Tuple

# 导入基础翻译器
from docslib_worker.translators.base_translator import BaseTranslator
from docslib_worker.core.translator_registry import register_translator

# 导入进度管理相关内容
from docslib_core.progress import FileStatus

@register_translator(framework_type='mkdocs', is_default=True)
class MkDocsTranslator(BaseTranslator):
    """MkDocs框架翻译器"""
    
    def __init__(self, source_path: str, target_path: str, config_path: Optional[str] = None):
        """
        初始化MkDocs翻译器
        
        Args:
            source_path: 源文档目录路径
            target_path: 目标翻译文档路径
            config_path: 配置文件路径
        """
        super().__init__(source_path, target_path, config_path)
        
        # MkDocs特有的设置
        self.mkdocs_config_file = 'mkdocs.yml'
        self.docs_dir = 'docs'  # 默认的文档目录
        self.site_dir = 'site'  # 默认的生成站点目录
        
        # MkDocs框架特定的文件类型设置
        self.translate_extensions = ['.md', '.markdown']  # 只翻译Markdown文件
        self.special_files = [self.mkdocs_config_file]  # MkDocs特有的特殊文件
        self.exclude_patterns = [
            '__pycache__', 
            '.git', 
            '.github', 
            'node_modules',
            'site',  # 默认输出目录
            'venv',
            '.venv',
            '.env'
        ]
        
        # 检测MkDocs配置文件是否存在
        self.mkdocs_config_path = os.path.join(self.source_path, self.mkdocs_config_file)
        if os.path.exists(self.mkdocs_config_path):
            # 加载MkDocs配置
            self._load_mkdocs_config()
        else:
            self.logger.warning(f"未找到MkDocs配置文件: {self.mkdocs_config_path}")
    
    @property
    def framework_type(self) -> str:
        """返回文档框架类型"""
        return "mkdocs"
    
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
                    continue
                
                # 检查是否是特殊文件
                if file in self.special_files:
                    special_files.append(rel_path)
                    continue
                
                # 检查是否是需要翻译的文件类型
                _, ext = os.path.splitext(file)
                if ext.lower() in self.translate_extensions:
                    # 对于MkDocs，只翻译docs目录下的Markdown文件
                    rel_dir = os.path.dirname(rel_path)
                    if rel_dir.startswith(self.docs_dir) or rel_dir == self.docs_dir:
                        all_files.append(rel_path)
        
        # 更新进度管理器中的文件列表
        self.progress_manager.register_files(all_files, file_type='normal')
        self.progress_manager.register_files(special_files, file_type='special')
        
        self.logger.info(f"找到 {len(all_files)} 个需要翻译的文件")
        
        # 返回所有需要处理的文件（普通文件和特殊文件）
        return all_files + special_files
    
    def _load_mkdocs_config(self) -> None:
        """加载MkDocs配置文件"""
        try:
            with open(self.mkdocs_config_path, 'r', encoding='utf-8') as f:
                self.mkdocs_config = yaml.safe_load(f)
                
            # 更新文档目录设置
            if self.mkdocs_config and 'docs_dir' in self.mkdocs_config:
                self.docs_dir = self.mkdocs_config['docs_dir']
                self.logger.info(f"使用自定义文档目录: {self.docs_dir}")
                
            # 更新生成站点目录设置
            if self.mkdocs_config and 'site_dir' in self.mkdocs_config:
                self.site_dir = self.mkdocs_config['site_dir']
                self.logger.info(f"使用自定义生成站点目录: {self.site_dir}")
                
            # 添加自定义生成站点目录到排除列表
            if self.site_dir and self.site_dir not in self.exclude_patterns:
                self.exclude_patterns.append(self.site_dir)
                
        except Exception as e:
            self.logger.error(f"加载MkDocs配置文件失败: {str(e)}")
            self.mkdocs_config = None
    
    def process_special_files(self, files: List[str]) -> bool:
        """
        处理MkDocs特殊文件，主要是mkdocs.yml配置文件
        
        Args:
            files: 特殊文件相对路径列表
            
        Returns:
            bool: 处理成功返回True，否则返回False
        """
        self.logger.info(f"处理MkDocs特殊文件，共 {len(files)} 个文件")
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
            
            if os.path.basename(file_path) == self.mkdocs_config_file:
                self.logger.info(f"处理MkDocs配置文件 ({processed_count}/{total_special_files}): {file_path}")
                try:
                    if self._translate_mkdocs_config(file_path):
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
                        error_msg = f"翻译MkDocs配置文件失败: {file_path}"
                        self.logger.error(error_msg)
                        self.progress_manager.update_file_status(file_path, FileStatus.UNTRANSLATED, error=error_msg, file_type='special')
                        success = False
                except Exception as e:
                    error_msg = f"处理MkDocs配置文件异常: {str(e)}"
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
    
    def _translate_mkdocs_config(self, config_rel_path: str) -> bool:
        """
        翻译MkDocs配置文件
        
        Args:
            config_rel_path: 配置文件相对路径
            
        Returns:
            bool: 翻译成功返回True，否则返回False
        """
        try:
            source_config_path = os.path.join(self.source_path, config_rel_path)
            
            # 读取原始配置
            with open(source_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 创建新配置的副本
            new_config = config.copy()
            
            # 翻译网站标题和描述
            if 'site_name' in new_config:
                original_site_name = new_config['site_name']
                self.logger.info(f"翻译网站标题: {original_site_name}")
                new_config['site_name'] = self.translator.translate_text(original_site_name)
            
            if 'site_description' in new_config:
                original_description = new_config['site_description']
                self.logger.info(f"翻译网站描述: {original_description}")
                new_config['site_description'] = self.translator.translate_text(original_description)
            
            # 处理导航结构
            if 'nav' in new_config:
                self.logger.info("翻译导航结构")
                new_config['nav'] = self._translate_nav_items(new_config['nav'])
            
            # 修改docs_dir和site_dir路径，添加目标语言后缀
            target_lang = self.config.get('global', {}).get('target_lang', 'zh')
            
            # 更新文档目录配置
            if 'docs_dir' in new_config:
                docs_dir = new_config['docs_dir']
                if docs_dir == 'docs' or os.path.basename(docs_dir) == 'docs':
                    new_docs_dir = f"docs_{target_lang}"
                    self.logger.info(f"更新文档目录: {docs_dir} -> {new_docs_dir}")
                    new_config['docs_dir'] = new_docs_dir
            
            # 更新站点目录配置
            if 'site_dir' in new_config:
                site_dir = new_config['site_dir']
                if site_dir == 'site' or os.path.basename(site_dir) == 'site':
                    new_site_dir = f"site_{target_lang}"
                    self.logger.info(f"更新站点目录: {site_dir} -> {new_site_dir}")
                    new_config['site_dir'] = new_site_dir
            
            # 获取目标文件路径
            target_config_file = self.get_target_path(config_rel_path)
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(target_config_file), exist_ok=True)
            
            # 保存翻译后的配置
            with open(target_config_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(new_config, f, allow_unicode=True, sort_keys=False)
            
            self.logger.info(f"MkDocs配置文件翻译完成: {target_config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"翻译MkDocs配置文件失败: {str(e)}", exc_info=True)
            return False
    
    def _translate_nav_items(self, nav_items):
        """
        递归翻译导航项
        
        Args:
            nav_items: 导航项列表或字典
            
        Returns:
            翻译后的导航项
        """
        if isinstance(nav_items, list):
            # 处理列表
            translated_items = []
            for item in nav_items:
                translated_items.append(self._translate_nav_items(item))
            return translated_items
        
        elif isinstance(nav_items, dict):
            # 处理字典
            translated_dict = {}
            for title, link in nav_items.items():
                # 翻译标题
                translated_title = self.translator.translate_text(title)
                # 递归处理链接
                translated_dict[translated_title] = self._translate_nav_items(link)
            return translated_dict
        
        else:
            # 处理字符串（文件路径）
            return nav_items  # 不翻译文件路径
    
    def post_translation(self) -> None:
        """
        翻译后的额外处理
        
        例如：处理主题文件、生成索引等
        """
        self.logger.info("执行MkDocs翻译后处理")
        
        # 复制静态资源
        self.copy_static_assets()
        
        # 处理主题文件
        self._process_theme_files()
    
    def _process_theme_files(self) -> None:
        """处理主题相关文件"""
        # TODO: 实现主题文件处理逻辑
        pass 