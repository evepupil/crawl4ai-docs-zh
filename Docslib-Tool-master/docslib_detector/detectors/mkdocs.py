"""
MkDocs框架检测器
"""

import os
import re
import yaml
import logging
from typing import Dict, Any, List, Optional

from docslib_detector.core.detector_base import DetectorBase

class MkDocsDetector(DetectorBase):
    """MkDocs文档框架检测器"""
    
    def __init__(self, repo_path: str, logger: Optional[logging.Logger] = None):
        """初始化MkDocs检测器"""
        super().__init__(repo_path, logger)
        self._config_file = None
        self._config_data = None
        self._mkdocs_root = None
    
    @property
    def framework_type(self) -> str:
        """返回文档框架类型"""
        return "mkdocs"
    
    def detect(self) -> bool:
        """
        检测仓库是否使用MkDocs框架
        
        Returns:
            bool: 如果是MkDocs框架返回True，否则返回False
        """
        self.logger.debug("开始检测MkDocs框架")
        
        # 重置检测结果
        self._confidence = 0.0
        self._detection_results = {}
        
        # 首先检查根目录
        if self._check_directory(self.repo_path):
            self._mkdocs_root = self.repo_path
            return True
        
        # 如果根目录不是MkDocs项目，检查常见的子目录
        common_subdirs = ['docs', 'documentation', 'doc', 'mkdocs']
        for subdir in common_subdirs:
            subdir_path = os.path.join(self.repo_path, subdir)
            if os.path.isdir(subdir_path):
                self.logger.debug(f"检查子目录: {subdir}")
                if self._check_directory(subdir_path):
                    self._mkdocs_root = subdir_path
                    return True
        
        return False
    
    def _check_directory(self, directory: str) -> bool:
        """
        检查指定目录是否为MkDocs项目
        
        Args:
            directory: 要检查的目录路径
            
        Returns:
            bool: 如果是MkDocs项目返回True，否则返回False
        """
        # 重置置信度，用于当前目录的检测
        local_confidence = 0.0
        
        # 检查是否存在mkdocs.yml或mkdocs.yaml
        config_files = ['mkdocs.yml', 'mkdocs.yaml']
        for file in config_files:
            config_path = os.path.join(directory, file)
            if os.path.isfile(config_path):
                self._config_file = config_path
                self.logger.debug(f"找到MkDocs配置文件: {config_path}")
                self._detection_results['config_file'] = config_path
                local_confidence += 0.6
                
                # 尝试解析配置文件
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_content = f.read()
                    
                    if config_content:
                        self._config_data = yaml.safe_load(config_content)
                        self._detection_results['config_data'] = self._config_data
                        local_confidence += 0.1
                        
                        # 检查配置文件中的关键字段
                        if 'site_name' in self._config_data:
                            self._detection_results['site_name'] = self._config_data['site_name']
                            local_confidence += 0.1
                        
                        if 'theme' in self._config_data:
                            self._detection_results['theme'] = self._config_data['theme']
                            local_confidence += 0.1
                except Exception as e:
                    self.logger.warning(f"解析MkDocs配置文件失败: {str(e)}")
                
                break
        
        # 如果没有找到配置文件，可能不是MkDocs
        if not self._config_file:
            self.logger.debug(f"未在{directory}中找到MkDocs配置文件")
            return False
        
        # 检查是否存在docs目录
        docs_dir = os.path.join(directory, 'docs')
        if os.path.isdir(docs_dir):
            self.logger.debug(f"找到docs目录: {docs_dir}")
            self._detection_results['has_docs_dir'] = True
            local_confidence += 0.1
            
            # 检查docs目录下是否有markdown文件
            try:
                md_files = []
                for root, _, files in os.walk(docs_dir):
                    for file in files:
                        if file.endswith('.md'):
                            md_files.append(os.path.join(root, file))
                
                if md_files:
                    self._detection_results['md_files_count'] = len(md_files)
                    local_confidence += 0.1
                    self.logger.debug(f"docs目录下找到 {len(md_files)} 个Markdown文件")
            except Exception as e:
                self.logger.warning(f"检查Markdown文件失败: {str(e)}")
        
        # 检查是否存在requirements.txt并包含mkdocs
        req_path = os.path.join(directory, 'requirements.txt')
        if os.path.isfile(req_path):
            try:
                with open(req_path, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                
                if req_content and re.search(r'mkdocs[>=<]', req_content):
                    self._detection_results['has_mkdocs_requirement'] = True
                    local_confidence += 0.1
                    self.logger.debug("requirements.txt中包含mkdocs依赖")
            except Exception as e:
                self.logger.warning(f"读取requirements.txt失败: {str(e)}")
        
        # 更新总体置信度
        self._confidence = local_confidence
        
        # 限制最大置信度为1.0
        self._confidence = min(self._confidence, 1.0)
        
        self.logger.info(f"MkDocs检测完成，置信度: {self._confidence:.2f}")
        return self._confidence > 0.5
    
    def get_framework_info(self) -> Dict[str, Any]:
        """
        获取MkDocs框架的详细信息
        
        Returns:
            Dict[str, Any]: 包含框架版本、配置等信息的字典
        """
        info = {
            "framework": "mkdocs",
            "type": "static",
            "config_file": self._config_file,
            "mkdocs_root": self._mkdocs_root,
            "docs_dir": "docs",
        }
        
        if self._config_data:
            # 提取关键配置信息
            info.update({
                "site_name": self._config_data.get('site_name', ''),
                "theme": self._config_data.get('theme', ''),
                "plugins": self._config_data.get('plugins', []),
                "nav": bool(self._config_data.get('nav') or self._config_data.get('pages')),
            })
            
            # 检查是否使用了多语言插件
            plugins = self._config_data.get('plugins', [])
            if isinstance(plugins, list) and 'i18n' in plugins:
                info['multilingual'] = True
            elif isinstance(plugins, dict) and 'i18n' in plugins:
                info['multilingual'] = True
            else:
                info['multilingual'] = False
        
        return info 