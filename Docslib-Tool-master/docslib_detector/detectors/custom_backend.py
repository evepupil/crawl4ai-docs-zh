"""
自定义后端框架检测器
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional

from docslib_detector.core.detector_base import DetectorBase

class CustomBackendDetector(DetectorBase):
    """自定义后端文档框架检测器"""
    
    def __init__(self, repo_path: str, logger: Optional[logging.Logger] = None):
        """初始化自定义后端检测器"""
        super().__init__(repo_path, logger)
        self._backend_tech = None
        self._db_tech = None
    
    @property
    def framework_type(self) -> str:
        """返回文档框架类型"""
        return "custom_backend"
    
    def detect(self) -> bool:
        """
        检测仓库是否使用自定义后端框架
        
        Returns:
            bool: 如果是自定义后端框架返回True，否则返回False
        """
        self.logger.debug("开始检测自定义后端框架")
        
        # 重置检测结果
        self._confidence = 0.0
        self._detection_results = {}
        
        # 检查是否存在后端技术栈的标志
        
        # 1. 检查是否存在package.json（Node.js应用）
        if self.file_exists('package.json'):
            try:
                package_content = self.read_file('package.json')
                if package_content:
                    package_data = json.loads(package_content)
                    dependencies = package_data.get('dependencies', {})
                    
                    # 检查是否有Express、Koa、NestJS等后端框架
                    backend_frameworks = ['express', 'koa', 'nest', 'hapi', 'fastify', 'next', 'nuxt']
                    found_frameworks = []
                    
                    for framework in backend_frameworks:
                        if framework in dependencies or f'@{framework}/core' in dependencies:
                            found_frameworks.append(framework)
                    
                    if found_frameworks:
                        self._backend_tech = 'nodejs'
                        self._detection_results['nodejs_frameworks'] = found_frameworks
                        self.logger.debug(f"检测到Node.js后端框架: {', '.join(found_frameworks)}")
                        self._confidence += 0.3
                    
                    # 检查是否有数据库相关依赖
                    db_techs = ['mongoose', 'sequelize', 'typeorm', 'prisma', 'knex', 'mongodb', 'mysql', 'pg', 'sqlite3']
                    found_dbs = []
                    
                    for db in db_techs:
                        if db in dependencies:
                            found_dbs.append(db)
                    
                    if found_dbs:
                        self._db_tech = found_dbs[0]
                        self._detection_results['db_technologies'] = found_dbs
                        self.logger.debug(f"检测到数据库技术: {', '.join(found_dbs)}")
                        self._confidence += 0.1
            except Exception as e:
                self.logger.warning(f"解析package.json失败: {str(e)}")
        
        # 2. 检查是否存在requirements.txt（Python应用）
        if self.file_exists('requirements.txt'):
            req_content = self.read_file('requirements.txt')
            if req_content:
                # 检查是否有Django、Flask、FastAPI等后端框架
                python_frameworks = ['django', 'flask', 'fastapi', 'pyramid', 'tornado', 'bottle']
                found_frameworks = []
                
                for framework in python_frameworks:
                    if re.search(rf'{framework}[>=<]', req_content, re.IGNORECASE):
                        found_frameworks.append(framework)
                
                if found_frameworks:
                    self._backend_tech = 'python'
                    self._detection_results['python_frameworks'] = found_frameworks
                    self.logger.debug(f"检测到Python后端框架: {', '.join(found_frameworks)}")
                    self._confidence += 0.3
                
                # 检查是否有数据库相关依赖
                db_techs = ['sqlalchemy', 'psycopg2', 'pymysql', 'pymongo', 'django-db', 'peewee']
                found_dbs = []
                
                for db in db_techs:
                    if re.search(rf'{db}[>=<]', req_content, re.IGNORECASE):
                        found_dbs.append(db)
                
                if found_dbs:
                    self._db_tech = found_dbs[0]
                    self._detection_results['db_technologies'] = found_dbs
                    self.logger.debug(f"检测到数据库技术: {', '.join(found_dbs)}")
                    self._confidence += 0.1
        
        # 3. 检查是否存在composer.json（PHP应用）
        if self.file_exists('composer.json'):
            try:
                composer_content = self.read_file('composer.json')
                if composer_content:
                    composer_data = json.loads(composer_content)
                    dependencies = composer_data.get('require', {})
                    
                    # 检查是否有Laravel、Symfony等后端框架
                    php_frameworks = ['laravel', 'symfony', 'slim', 'lumen', 'yii', 'cakephp']
                    found_frameworks = []
                    
                    for framework in php_frameworks:
                        for dep in dependencies:
                            if framework in dep.lower():
                                found_frameworks.append(framework)
                                break
                    
                    if found_frameworks:
                        self._backend_tech = 'php'
                        self._detection_results['php_frameworks'] = found_frameworks
                        self.logger.debug(f"检测到PHP后端框架: {', '.join(found_frameworks)}")
                        self._confidence += 0.3
            except Exception as e:
                self.logger.warning(f"解析composer.json失败: {str(e)}")
        
        # 4. 检查是否存在.env或配置文件
        env_files = ['.env', '.env.example', '.env.local', 'config.json', 'config.yaml', 'config.yml']
        for file in env_files:
            if self.file_exists(file):
                self._detection_results['has_env_file'] = file
                self.logger.debug(f"找到环境配置文件: {file}")
                self._confidence += 0.1
                break
        
        # 5. 检查是否存在数据库迁移文件或模型文件
        migration_paths = [
            'migrations', 'db/migrations', 'database/migrations',  # 通用
            'app/models', 'models', 'src/models', 'src/entity',    # 模型
            'prisma/schema.prisma'                                # Prisma
        ]
        
        for path in migration_paths:
            if self.dir_exists(path) or self.file_exists(path):
                self._detection_results['has_db_structure'] = path
                self.logger.debug(f"找到数据库结构文件/目录: {path}")
                self._confidence += 0.1
                break
        
        # 6. 检查是否存在API路由文件
        api_paths = [
            'routes', 'app/routes', 'src/routes', 'api',
            'controllers', 'app/controllers', 'src/controllers',
            'app/api', 'src/api'
        ]
        
        for path in api_paths:
            if self.dir_exists(path):
                self._detection_results['has_api_routes'] = path
                self.logger.debug(f"找到API路由目录: {path}")
                self._confidence += 0.1
                break
        
        # 7. 检查是否存在docker-compose.yml（常见于后端服务）
        if self.file_exists('docker-compose.yml') or self.file_exists('docker-compose.yaml'):
            self._detection_results['has_docker_compose'] = True
            self.logger.debug("找到docker-compose配置文件")
            self._confidence += 0.1
        
        # 8. 检查是否有国际化配置目录
        i18n_paths = ['locales', 'i18n', 'translations', 'lang']
        for path in i18n_paths:
            if self.dir_exists(path):
                self._detection_results['has_i18n'] = path
                self.logger.debug(f"找到国际化目录: {path}")
                self._confidence += 0.1
                break
        
        # 限制最大置信度为1.0
        self._confidence = min(self._confidence, 1.0)
        
        self.logger.info(f"自定义后端框架检测完成，置信度: {self._confidence:.2f}")
        return self._confidence > 0.5
    
    def get_framework_info(self) -> Dict[str, Any]:
        """
        获取自定义后端框架的详细信息
        
        Returns:
            Dict[str, Any]: 包含框架版本、配置等信息的字典
        """
        info = {
            "framework": "CustomBackend",
            "type": "dynamic",
            "backend_technology": self._backend_tech,
            "database_technology": self._db_tech
        }
        
        # 添加检测到的框架信息
        if self._backend_tech == 'nodejs':
            info['frameworks'] = self._detection_results.get('nodejs_frameworks', [])
        elif self._backend_tech == 'python':
            info['frameworks'] = self._detection_results.get('python_frameworks', [])
        elif self._backend_tech == 'php':
            info['frameworks'] = self._detection_results.get('php_frameworks', [])
        
        # 添加数据库信息
        if 'db_technologies' in self._detection_results:
            info['database_details'] = self._detection_results['db_technologies']
        
        # 检查API路由
        if 'has_api_routes' in self._detection_results:
            info['api_routes_path'] = self._detection_results['has_api_routes']
        
        # 检查国际化支持
        if 'has_i18n' in self._detection_results:
            info['multilingual'] = True
            info['i18n_path'] = self._detection_results['has_i18n']
        else:
            info['multilingual'] = False
        
        # 检查Docker支持
        info['has_docker'] = self._detection_results.get('has_docker_compose', False)
        
        return info 