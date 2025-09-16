"""
混合型API框架检测器
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional

from docslib_detector.core.detector_base import DetectorBase

class HybridAPIDetector(DetectorBase):
    """混合型API文档框架检测器"""
    
    def __init__(self, repo_path: str, logger: Optional[logging.Logger] = None):
        """初始化混合型API检测器"""
        super().__init__(repo_path, logger)
        self._frontend_tech = None
        self._api_tech = None
    
    @property
    def framework_type(self) -> str:
        """返回文档框架类型"""
        return "hybrid_api"
    
    def detect(self) -> bool:
        """
        检测仓库是否使用混合型API框架
        
        Returns:
            bool: 如果是混合型API框架返回True，否则返回False
        """
        self.logger.debug("开始检测混合型API框架")
        
        # 重置检测结果
        self._confidence = 0.0
        self._detection_results = {}
        
        # 检测静态部分（前端）
        static_confidence = self._detect_static_part()
        
        # 检测API部分（后端）
        api_confidence = self._detect_api_part()
        
        # 如果同时检测到静态部分和API部分，则可能是混合型框架
        if static_confidence > 0 and api_confidence > 0:
            self._confidence = (static_confidence + api_confidence) / 2
            self.logger.info(f"检测到混合型框架，静态部分置信度: {static_confidence:.2f}, API部分置信度: {api_confidence:.2f}")
        else:
            self._confidence = 0.0
        
        # 检查是否有明确的前后端分离标志
        if self._detection_results.get('has_api_config', False) and self._detection_results.get('has_frontend_config', False):
            self._confidence += 0.2
            self.logger.debug("检测到前后端分离配置")
        
        # 限制最大置信度为1.0
        self._confidence = min(self._confidence, 1.0)
        
        self.logger.info(f"混合型API框架检测完成，置信度: {self._confidence:.2f}")
        return self._confidence > 0.5
    
    def _detect_static_part(self) -> float:
        """
        检测静态部分（前端）
        
        Returns:
            float: 静态部分的置信度
        """
        confidence = 0.0
        
        # 1. 检查是否存在package.json（前端项目）
        if self.file_exists('package.json'):
            try:
                package_content = self.read_file('package.json')
                if package_content:
                    package_data = json.loads(package_content)
                    dependencies = package_data.get('dependencies', {})
                    dev_dependencies = package_data.get('devDependencies', {})
                    all_deps = {**dependencies, **dev_dependencies}
                    
                    # 检查是否有前端框架
                    frontend_frameworks = {
                        'react': ['react', 'react-dom', 'create-react-app', 'next'],
                        'vue': ['vue', 'nuxt', '@vue/cli'],
                        'angular': ['@angular/core', '@angular/cli'],
                        'svelte': ['svelte', 'sveltekit']
                    }
                    
                    for tech, libs in frontend_frameworks.items():
                        for lib in libs:
                            if lib in all_deps:
                                self._frontend_tech = tech
                                self._detection_results['frontend_framework'] = tech
                                self._detection_results['frontend_library'] = lib
                                self.logger.debug(f"检测到前端框架: {tech} ({lib})")
                                confidence += 0.3
                                break
                        if self._frontend_tech:
                            break
                    
                    # 检查是否有静态站点生成器
                    ssg_tools = ['gatsby', 'next', 'nuxt', 'gridsome', 'eleventy', '11ty', 'vuepress', 'vitepress']
                    for tool in ssg_tools:
                        if tool in all_deps:
                            self._detection_results['ssg_tool'] = tool
                            self.logger.debug(f"检测到静态站点生成器: {tool}")
                            confidence += 0.2
                            break
                    
                    # 检查是否有API客户端库
                    api_clients = ['axios', 'fetch-api', 'superagent', 'request', 'got', 'ky', 'apollo-client', 'graphql']
                    for client in api_clients:
                        if client in all_deps:
                            self._detection_results['api_client'] = client
                            self.logger.debug(f"检测到API客户端库: {client}")
                            confidence += 0.1
                            break
            except Exception as e:
                self.logger.warning(f"解析package.json失败: {str(e)}")
        
        # 2. 检查是否存在前端构建配置文件
        frontend_configs = [
            'webpack.config.js', 'vite.config.js', 'rollup.config.js',
            'babel.config.js', '.babelrc', 'tsconfig.json',
            'angular.json', 'vue.config.js', 'next.config.js'
        ]
        
        for config in frontend_configs:
            if self.file_exists(config):
                self._detection_results['frontend_config'] = config
                self._detection_results['has_frontend_config'] = True
                self.logger.debug(f"找到前端构建配置文件: {config}")
                confidence += 0.1
                break
        
        # 3. 检查典型的前端目录结构
        frontend_dirs = ['src', 'public', 'static', 'assets', 'components', 'pages']
        found_dirs = []
        
        for dir_name in frontend_dirs:
            if self.dir_exists(dir_name):
                found_dirs.append(dir_name)
        
        if found_dirs:
            self._detection_results['frontend_dirs'] = found_dirs
            self.logger.debug(f"找到前端目录: {', '.join(found_dirs)}")
            confidence += min(0.1 * len(found_dirs), 0.3)
        
        return min(confidence, 1.0)
    
    def _detect_api_part(self) -> float:
        """
        检测API部分（后端）
        
        Returns:
            float: API部分的置信度
        """
        confidence = 0.0
        
        # 1. 检查是否存在API相关配置文件
        api_configs = [
            'swagger.json', 'swagger.yaml', 'openapi.json', 'openapi.yaml',
            'api.json', 'api.yaml', '.env.api', 'api.config.js'
        ]
        
        for config in api_configs:
            if self.file_exists(config):
                self._detection_results['api_config'] = config
                self._detection_results['has_api_config'] = True
                self.logger.debug(f"找到API配置文件: {config}")
                confidence += 0.3
                break
        
        # 2. 检查是否存在API目录
        api_dirs = ['api', 'apis', 'services', 'endpoints', 'controllers']
        for dir_name in api_dirs:
            if self.dir_exists(dir_name):
                self._detection_results['api_dir'] = dir_name
                self.logger.debug(f"找到API目录: {dir_name}")
                confidence += 0.2
                break
        
        # 3. 检查是否有API相关文件
        api_files = self.list_files('', '*.api.*')
        if api_files:
            self._detection_results['api_files'] = api_files
            self.logger.debug(f"找到API文件: {len(api_files)}个")
            confidence += 0.1
        
        # 4. 检查package.json中是否有API相关依赖
        if self.file_exists('package.json'):
            try:
                package_content = self.read_file('package.json')
                if package_content:
                    package_data = json.loads(package_content)
                    dependencies = package_data.get('dependencies', {})
                    
                    # 检查是否有API相关库
                    api_libs = [
                        'express', 'koa', 'fastify', 'hapi', 'restify',
                        'swagger', 'openapi', 'graphql', 'apollo-server',
                        'json-server', 'axios', 'fetch', 'api-client'
                    ]
                    
                    found_libs = []
                    for lib in api_libs:
                        for dep in dependencies:
                            if lib in dep:
                                found_libs.append(dep)
                                break
                    
                    if found_libs:
                        self._api_tech = found_libs[0]
                        self._detection_results['api_libraries'] = found_libs
                        self.logger.debug(f"检测到API库: {', '.join(found_libs)}")
                        confidence += 0.2
            except Exception as e:
                self.logger.warning(f"解析package.json失败: {str(e)}")
        
        # 5. 检查是否存在代理配置（前端代理到API）
        proxy_configs = ['proxy.conf.js', 'setupProxy.js', '.proxyrc', 'vue.config.js']
        for config in proxy_configs:
            if self.file_exists(config):
                content = self.read_file(config)
                if content and ('proxy' in content or 'Proxy' in content):
                    self._detection_results['has_proxy_config'] = config
                    self.logger.debug(f"找到API代理配置: {config}")
                    confidence += 0.2
                    break
        
        return min(confidence, 1.0)
    
    def get_framework_info(self) -> Dict[str, Any]:
        """
        获取混合型API框架的详细信息
        
        Returns:
            Dict[str, Any]: 包含框架版本、配置等信息的字典
        """
        info = {
            "framework": "HybridAPI",
            "type": "hybrid",
            "frontend_technology": self._frontend_tech,
            "api_technology": self._api_tech
        }
        
        # 添加前端信息
        if self._frontend_tech:
            frontend_info = {
                "framework": self._frontend_tech,
                "library": self._detection_results.get('frontend_library'),
                "config_file": self._detection_results.get('frontend_config'),
                "directories": self._detection_results.get('frontend_dirs', [])
            }
            
            if 'ssg_tool' in self._detection_results:
                frontend_info['ssg_tool'] = self._detection_results['ssg_tool']
            
            info['frontend_details'] = frontend_info
        
        # 添加API信息
        api_info = {
            "config_file": self._detection_results.get('api_config'),
            "directory": self._detection_results.get('api_dir'),
            "libraries": self._detection_results.get('api_libraries', [])
        }
        
        if 'has_proxy_config' in self._detection_results:
            api_info['proxy_config'] = self._detection_results['has_proxy_config']
        
        info['api_details'] = api_info
        
        # 检查API客户端
        if 'api_client' in self._detection_results:
            info['api_client'] = self._detection_results['api_client']
        
        # 检查是否有明确的前后端分离
        info['clear_separation'] = (
            self._detection_results.get('has_api_config', False) and 
            self._detection_results.get('has_frontend_config', False)
        )
        
        return info 