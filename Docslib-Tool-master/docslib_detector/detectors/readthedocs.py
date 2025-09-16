"""
ReadTheDocs框架检测器
"""

import os
import re
import yaml
import logging
from typing import Dict, Any, List, Optional

from docslib_detector.core.detector_base import DetectorBase

class ReadTheDocsDetector(DetectorBase):
    """ReadTheDocs文档框架检测器"""
    
    def __init__(self, repo_path: str, logger: Optional[logging.Logger] = None):
        """初始化ReadTheDocs检测器"""
        super().__init__(repo_path, logger)
        self._config_file = None
        self._config_data = None
        self._sphinx_conf = None
        self._rtd_config = None
    
    @property
    def framework_type(self) -> str:
        """返回文档框架类型"""
        return "readthedocs"
    
    def detect(self) -> bool:
        """
        检测仓库是否使用ReadTheDocs框架
        
        Returns:
            bool: 如果是ReadTheDocs框架返回True，否则返回False
        """
        self.logger.debug("开始检测ReadTheDocs框架")
        
        # 重置检测结果
        self._confidence = 0.0
        self._detection_results = {}
        
        # 检查是否存在.readthedocs.yaml或.readthedocs.yml配置文件
        rtd_config_files = ['.readthedocs.yaml', '.readthedocs.yml']
        for file in rtd_config_files:
            if self.file_exists(file):
                self._rtd_config = file
                self.logger.debug(f"找到ReadTheDocs配置文件: {file}")
                self._detection_results['rtd_config_file'] = file
                self._confidence += 0.5
                
                # 解析配置文件
                try:
                    config_content = self.read_file(file)
                    if config_content:
                        config_data = yaml.safe_load(config_content)
                        self._detection_results['rtd_config_data'] = config_data
                        self._confidence += 0.1
                except Exception as e:
                    self.logger.warning(f"解析ReadTheDocs配置文件失败: {str(e)}")
                
                break
        
        # 检查是否存在conf.py (Sphinx配置文件)
        sphinx_conf_paths = ['conf.py', 'docs/conf.py', 'source/conf.py']
        for path in sphinx_conf_paths:
            if self.file_exists(path):
                self._sphinx_conf = path
                self.logger.debug(f"找到Sphinx配置文件: {path}")
                self._detection_results['sphinx_conf'] = path
                self._confidence += 0.3
                
                # 检查conf.py中是否有ReadTheDocs相关配置
                conf_content = self.read_file(path)
                if conf_content:
                    if re.search(r'sphinx_rtd_theme', conf_content):
                        self.logger.debug("在conf.py中找到sphinx_rtd_theme")
                        self._detection_results['has_rtd_theme'] = True
                        self._confidence += 0.1
                    
                    if re.search(r'readthedocs', conf_content, re.IGNORECASE):
                        self.logger.debug("在conf.py中找到readthedocs关键字")
                        self._detection_results['has_rtd_keyword'] = True
                        self._confidence += 0.1
                break
        
        # 检查是否存在index.rst文件
        index_paths = ['index.rst', 'docs/index.rst', 'source/index.rst']
        for path in index_paths:
            if self.file_exists(path):
                self.logger.debug(f"找到index.rst文件: {path}")
                self._detection_results['has_index_rst'] = True
                self._confidence += 0.1
                break
        
        # 检查是否存在requirements.txt并包含sphinx或sphinx_rtd_theme
        if self.file_exists('requirements.txt'):
            req_content = self.read_file('requirements.txt')
            if req_content:
                if re.search(r'sphinx[>=<]', req_content):
                    self.logger.debug("在requirements.txt中找到sphinx依赖")
                    self._detection_results['has_sphinx_requirement'] = True
                    self._confidence += 0.1
                
                if re.search(r'sphinx_rtd_theme', req_content):
                    self.logger.debug("在requirements.txt中找到sphinx_rtd_theme依赖")
                    self._detection_results['has_rtd_theme_requirement'] = True
                    self._confidence += 0.1
        
        # 检查是否存在docs目录下的rst文件
        if self.dir_exists('docs'):
            rst_files = self.list_files('docs', '*.rst')
            if rst_files:
                self.logger.debug(f"在docs目录下找到 {len(rst_files)} 个RST文件")
                self._detection_results['rst_files_count'] = len(rst_files)
                self._confidence += 0.1
        
        # 检查是否存在make.bat或Makefile (常见于Sphinx项目)
        if self.file_exists('make.bat') or self.file_exists('Makefile'):
            self.logger.debug("找到make.bat或Makefile")
            self._detection_results['has_make_files'] = True
            self._confidence += 0.1
        
        # 检查是否存在_build或_static目录 (常见于Sphinx项目)
        if self.dir_exists('_build') or self.dir_exists('docs/_build'):
            self.logger.debug("找到_build目录")
            self._detection_results['has_build_dir'] = True
            self._confidence += 0.1
        
        if self.dir_exists('_static') or self.dir_exists('docs/_static'):
            self.logger.debug("找到_static目录")
            self._detection_results['has_static_dir'] = True
            self._confidence += 0.1
        
        # 限制最大置信度为1.0
        self._confidence = min(self._confidence, 1.0)
        
        self.logger.info(f"ReadTheDocs检测完成，置信度: {self._confidence:.2f}")
        return self._confidence > 0.5
    
    def get_framework_info(self) -> Dict[str, Any]:
        """
        获取ReadTheDocs框架的详细信息
        
        Returns:
            Dict[str, Any]: 包含框架版本、配置等信息的字典
        """
        info = {
            "framework": "ReadTheDocs",
            "type": "dynamic",
            "rtd_config_file": self._rtd_config,
            "sphinx_conf": self._sphinx_conf,
        }
        
        # 检查是否使用了多语言支持
        if self._sphinx_conf:
            conf_content = self.read_file(self._sphinx_conf)
            if conf_content:
                # 检查是否配置了语言
                language_match = re.search(r'language\s*=\s*[\'"]([^\'"]+)[\'"]', conf_content)
                if language_match:
                    info['language'] = language_match.group(1)
                
                # 检查是否使用了sphinx-intl
                if re.search(r'sphinx-intl', conf_content) or re.search(r'locale_dirs', conf_content):
                    info['multilingual'] = True
                else:
                    info['multilingual'] = False
        
        # 检查文档源格式
        if self._detection_results.get('rst_files_count', 0) > 0:
            info['source_format'] = 'reStructuredText'
        elif len(self.list_files('docs', '*.md')) > 0:
            info['source_format'] = 'Markdown'
        else:
            info['source_format'] = 'Unknown'
        
        # 检查主题
        if self._detection_results.get('has_rtd_theme', False):
            info['theme'] = 'sphinx_rtd_theme'
        
        return info 