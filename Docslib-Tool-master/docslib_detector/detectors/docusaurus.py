"""
Docusaurus框架检测器
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional

from docslib_detector.core.detector_base import DetectorBase

class DocusaurusDetector(DetectorBase):
    """Docusaurus文档框架检测器"""
    
    def __init__(self, repo_path: str, logger: Optional[logging.Logger] = None):
        """初始化Docusaurus检测器"""
        super().__init__(repo_path, logger)
        self._config_file = None
        self._config_data = None
        self._package_json = None
        self._docusaurus_root = None
    
    @property
    def framework_type(self) -> str:
        """返回文档框架类型"""
        return "docusaurus"
    
    def detect(self) -> bool:
        """
        检测仓库是否使用Docusaurus框架
        
        Returns:
            bool: 如果是Docusaurus框架返回True，否则返回False
        """
        self.logger.debug("开始检测Docusaurus框架")
        
        # 重置检测结果
        self._confidence = 0.0
        self._detection_results = {}
        
        # 首先检查根目录
        if self._check_directory(self.repo_path):
            self._docusaurus_root = self.repo_path
            return True
        
        # 如果根目录不是Docusaurus项目，检查常见的子目录
        common_subdirs = ['website', 'docs', 'documentation', 'doc']
        for subdir in common_subdirs:
            subdir_path = os.path.join(self.repo_path, subdir)
            if os.path.isdir(subdir_path):
                self.logger.debug(f"检查子目录: {subdir}")
                if self._check_directory(subdir_path):
                    self._docusaurus_root = subdir_path
                    return True
        
        return False
    
    def _check_directory(self, directory: str) -> bool:
        """
        检查指定目录是否为Docusaurus项目
        
        Args:
            directory: 要检查的目录路径
            
        Returns:
            bool: 如果是Docusaurus项目返回True，否则返回False
        """
        # 重置置信度，用于当前目录的检测
        local_confidence = 0.0
        
        # 检查package.json是否存在并包含docusaurus依赖
        package_json_path = os.path.join(directory, 'package.json')
        if os.path.isfile(package_json_path):
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_content = f.read()
                
                if package_content:
                    package_data = json.loads(package_content)
                    self._package_json = package_data
                    
                    # 检查依赖中是否包含docusaurus
                    dependencies = package_data.get('dependencies', {})
                    dev_dependencies = package_data.get('devDependencies', {})
                    
                    docusaurus_deps = []
                    for dep_name in list(dependencies.keys()) + list(dev_dependencies.keys()):
                        if '@docusaurus' in dep_name or dep_name == 'docusaurus':
                            docusaurus_deps.append(dep_name)
                    
                    if docusaurus_deps:
                        self.logger.debug(f"在{directory}/package.json中找到Docusaurus依赖: {', '.join(docusaurus_deps)}")
                        self._detection_results['docusaurus_deps'] = docusaurus_deps
                        local_confidence += 0.5
            except Exception as e:
                self.logger.warning(f"解析{directory}/package.json失败: {str(e)}")
        
        # 检查是否存在docusaurus.config.js或docusaurus.config.ts
        config_files = ['docusaurus.config.js', 'docusaurus.config.ts']
        for file in config_files:
            config_path = os.path.join(directory, file)
            if os.path.isfile(config_path):
                self._config_file = config_path
                self.logger.debug(f"找到Docusaurus配置文件: {config_path}")
                self._detection_results['config_file'] = config_path
                local_confidence += 0.3
                
                # 简单分析配置文件内容
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_content = f.read()
                    
                    if config_content:
                        # 检查是否包含典型的Docusaurus配置
                        if re.search(r'module\.exports\s*=\s*{', config_content) or re.search(r'export\s+default\s+{', config_content):
                            local_confidence += 0.1
                        
                        # 检查是否配置了多语言支持
                        if re.search(r'i18n\s*:', config_content):
                            self._detection_results['has_i18n'] = True
                            local_confidence += 0.1
                except Exception as e:
                    self.logger.warning(f"读取配置文件{config_path}失败: {str(e)}")
                
                break
        
        # 检查目录结构
        key_dirs = {
            'docs': 'docs目录',
            'src': 'src目录',
            'blog': 'blog目录',
            'i18n': 'i18n目录',
            'static': 'static目录'
        }
        
        key_files = {
            'sidebars.js': 'sidebars.js文件',
            'sidebars.ts': 'sidebars.ts文件'
        }
        
        for path, desc in key_dirs.items():
            if os.path.isdir(os.path.join(directory, path)):
                self._detection_results[f'has_{path}'] = True
                self.logger.debug(f"找到{desc}: {os.path.join(directory, path)}")
                local_confidence += 0.05
        
        for path, desc in key_files.items():
            if os.path.isfile(os.path.join(directory, path)):
                self._detection_results[f'has_{path.replace(".", "_")}'] = True
                self.logger.debug(f"找到{desc}: {os.path.join(directory, path)}")
                local_confidence += 0.05
        
        # 检查是否存在babel.config.js（Docusaurus常用）
        if os.path.isfile(os.path.join(directory, 'babel.config.js')):
            self._detection_results['has_babel_config'] = True
            local_confidence += 0.05
        
        # 更新总体置信度
        self._confidence = local_confidence
        
        # 限制最大置信度为1.0
        self._confidence = min(self._confidence, 1.0)
        
        self.logger.info(f"Docusaurus检测完成，置信度: {self._confidence:.2f}")
        return self._confidence > 0.5
    
    def get_framework_info(self) -> Dict[str, Any]:
        """
        获取Docusaurus框架的详细信息
        
        Returns:
            Dict[str, Any]: 包含框架版本、配置等信息的字典
        """
        info = {
            "framework": "Docusaurus",
            "type": "static",
            "config_file": self._config_file,
            "docusaurus_root": self._docusaurus_root
        }
        
        # 提取版本信息
        if self._package_json:
            dependencies = self._package_json.get('dependencies', {})
            dev_dependencies = self._package_json.get('devDependencies', {})
            
            # 尝试获取Docusaurus版本
            docusaurus_version = None
            for deps in [dependencies, dev_dependencies]:
                if '@docusaurus/core' in deps:
                    docusaurus_version = deps['@docusaurus/core']
                elif 'docusaurus' in deps:
                    docusaurus_version = deps['docusaurus']
            
            if docusaurus_version:
                info['version'] = docusaurus_version
        
        if self._docusaurus_root:
            # 检查目录结构
            dirs_to_check = ['docs', 'blog', 'src', 'i18n', 'static']
            for dir_name in dirs_to_check:
                dir_path = os.path.join(self._docusaurus_root, dir_name)
                if os.path.isdir(dir_path):
                    info[f'{dir_name}_dir'] = True
                    
                    # 如果有docs目录，计算文档数量
                    if dir_name == 'docs':
                        try:
                            md_files = []
                            for root, _, files in os.walk(dir_path):
                                for file in files:
                                    if file.endswith('.md') or file.endswith('.mdx'):
                                        md_files.append(os.path.join(root, file))
                            info['docs_count'] = len(md_files)
                        except Exception as e:
                            self.logger.warning(f"计算文档数量失败: {str(e)}")
                    
                    # 如果有i18n目录，检测支持的语言
                    if dir_name == 'i18n':
                        try:
                            langs = []
                            for item in os.listdir(dir_path):
                                if os.path.isdir(os.path.join(dir_path, item)):
                                    langs.append(item)
                            info['supported_languages'] = langs
                        except Exception as e:
                            self.logger.warning(f"检测支持的语言失败: {str(e)}")
            
            # 检查是否有sidebars.js或sidebars.ts
            for sidebar_file in ['sidebars.js', 'sidebars.ts']:
                if os.path.isfile(os.path.join(self._docusaurus_root, sidebar_file)):
                    info['has_sidebars'] = True
                    break
        
        return info 