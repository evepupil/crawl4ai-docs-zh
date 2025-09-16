"""
GitBook框架检测器
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional

from docslib_detector.core.detector_base import DetectorBase

class GitBookDetector(DetectorBase):
    """GitBook文档框架检测器"""
    
    def __init__(self, repo_path: str, logger: Optional[logging.Logger] = None):
        """初始化GitBook检测器"""
        super().__init__(repo_path, logger)
        self._config_file = None
        self._config_data = None
        self._summary_file = None
        self._gitbook_version = None
    
    @property
    def framework_type(self) -> str:
        """返回文档框架类型"""
        return "gitbook"
    
    def detect(self) -> bool:
        """
        检测仓库是否使用GitBook框架
        
        Returns:
            bool: 如果是GitBook框架返回True，否则返回False
        """
        self.logger.debug("开始检测GitBook框架")
        
        # 重置检测结果
        self._confidence = 0.0
        self._detection_results = {}
        
        # 检查是否存在book.json或.gitbook.yaml配置文件
        config_files = ['book.json', '.gitbook.yaml', '.gitbook.yml']
        for file in config_files:
            if self.file_exists(file):
                self._config_file = file
                self.logger.debug(f"找到GitBook配置文件: {file}")
                self._detection_results['config_file'] = file
                self._confidence += 0.4
                
                # 解析配置文件
                try:
                    config_content = self.read_file(file)
                    if config_content:
                        if file.endswith('.json'):
                            self._config_data = json.loads(config_content)
                        else:  # YAML文件
                            import yaml
                            self._config_data = yaml.safe_load(config_content)
                        
                        self._detection_results['config_data'] = self._config_data
                        self._confidence += 0.1
                        
                        # 检查是否配置了多语言支持
                        if 'languages' in self._config_data:
                            self._detection_results['has_languages'] = True
                            self._detection_results['languages'] = self._config_data['languages']
                            self._confidence += 0.1
                except Exception as e:
                    self.logger.warning(f"解析GitBook配置文件失败: {str(e)}")
                
                break
        
        # 检查是否存在SUMMARY.md文件（GitBook的目录结构文件）
        summary_paths = ['SUMMARY.md', 'zh/SUMMARY.md', 'en/SUMMARY.md']
        for path in summary_paths:
            if self.file_exists(path):
                self._summary_file = path
                self.logger.debug(f"找到SUMMARY.md文件: {path}")
                self._detection_results['summary_file'] = path
                self._confidence += 0.3
                break
        
        # 检查是否存在README.md作为首页
        if self.file_exists('README.md'):
            self.logger.debug("找到README.md文件")
            self._detection_results['has_readme'] = True
            self._confidence += 0.1
        
        # 检查是否存在GLOSSARY.md（术语表）
        if self.file_exists('GLOSSARY.md'):
            self.logger.debug("找到GLOSSARY.md文件")
            self._detection_results['has_glossary'] = True
            self._confidence += 0.1
        
        # 检查是否存在package.json并包含gitbook依赖
        if self.file_exists('package.json'):
            try:
                package_content = self.read_file('package.json')
                if package_content:
                    package_data = json.loads(package_content)
                    
                    # 检查依赖中是否包含gitbook
                    dependencies = package_data.get('dependencies', {})
                    dev_dependencies = package_data.get('devDependencies', {})
                    
                    if 'gitbook' in dependencies:
                        self._gitbook_version = dependencies['gitbook']
                        self._detection_results['gitbook_version'] = self._gitbook_version
                        self._confidence += 0.2
                    elif 'gitbook' in dev_dependencies:
                        self._gitbook_version = dev_dependencies['gitbook']
                        self._detection_results['gitbook_version'] = self._gitbook_version
                        self._confidence += 0.2
                    elif 'gitbook-cli' in dependencies or 'gitbook-cli' in dev_dependencies:
                        self._detection_results['has_gitbook_cli'] = True
                        self._confidence += 0.2
            except Exception as e:
                self.logger.warning(f"解析package.json失败: {str(e)}")
        
        # 检查是否存在_book目录（GitBook构建输出目录）
        if self.dir_exists('_book'):
            self.logger.debug("找到_book目录")
            self._detection_results['has_book_dir'] = True
            self._confidence += 0.1
        
        # 检查是否存在node_modules/gitbook目录
        if self.dir_exists('node_modules/gitbook'):
            self.logger.debug("找到node_modules/gitbook目录")
            self._detection_results['has_gitbook_modules'] = True
            self._confidence += 0.1
        
        # 检查是否存在多语言目录结构
        lang_dirs = []
        for item in os.listdir(self.repo_path):
            if os.path.isdir(os.path.join(self.repo_path, item)) and len(item) == 2:
                if self.file_exists(os.path.join(item, 'SUMMARY.md')):
                    lang_dirs.append(item)
        
        if lang_dirs:
            self.logger.debug(f"找到可能的语言目录: {', '.join(lang_dirs)}")
            self._detection_results['language_dirs'] = lang_dirs
            self._confidence += 0.1
        
        # 限制最大置信度为1.0
        self._confidence = min(self._confidence, 1.0)
        
        self.logger.info(f"GitBook检测完成，置信度: {self._confidence:.2f}")
        return self._confidence > 0.5
    
    def get_framework_info(self) -> Dict[str, Any]:
        """
        获取GitBook框架的详细信息
        
        Returns:
            Dict[str, Any]: 包含框架版本、配置等信息的字典
        """
        info = {
            "framework": "GitBook",
            "type": "static",
            "config_file": self._config_file,
            "summary_file": self._summary_file,
            "version": self._gitbook_version
        }
        
        # 添加多语言支持信息
        if self._config_data and 'languages' in self._config_data:
            info['multilingual'] = True
            info['languages'] = self._config_data['languages']
        elif self._detection_results.get('language_dirs'):
            info['multilingual'] = True
            info['languages'] = self._detection_results['language_dirs']
        else:
            info['multilingual'] = False
        
        # 添加插件信息
        if self._config_data and 'plugins' in self._config_data:
            info['plugins'] = self._config_data['plugins']
        
        # 检查文档结构
        md_files = self.list_files('', '*.md')
        info['md_files_count'] = len(md_files)
        
        # 检查是否使用了GitBook.com还是本地CLI
        if self._detection_results.get('has_gitbook_modules') or self._detection_results.get('has_gitbook_cli'):
            info['deployment_type'] = 'cli'
        elif self.file_exists('.gitbook.yaml') or self.file_exists('.gitbook.yml'):
            info['deployment_type'] = 'gitbook.com'
        else:
            info['deployment_type'] = 'unknown'
        
        return info 