"""
翻译器模块

该模块提供文档翻译的核心功能。
"""

import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Optional, Tuple, Callable
import logging

# 移除本地配置和日志导入，使用全局配置和日志管理
from docslib_core.utils import get_logger

# 导入本地模块
from .cache import TranslationCache
from .yuanbao_service import YuanbaoTranslationService

# 尝试从统一配置管理系统中获取配置
try:
    from . import get_translator_config, get_translator_prompts
except ImportError:
    # 如果找不到统一配置管理器，使用原始的配置加载方式
    from .config import load_config as get_translator_config
    from .config import load_prompts as get_translator_prompts

class TranslationError(Exception):
    """翻译错误异常"""
    pass

class Translator:
    """翻译器类，提供文档翻译功能"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化翻译器
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认配置文件
        """
        # 加载配置
        try:
            if config_file:
                # 如果提供了配置文件路径，使用原始的加载方式
                from .config import load_config
                self.config = load_config(config_file)
            else:
                # 否则使用统一配置管理系统
                self.config = get_translator_config()
        except Exception as e:
            # 使用默认配置
            self.config = {
                'translation_service': {
                    'provider': 'yuanbao',
                    'base_url': 'http://localhost:8000/v1/',
                    'model': 'deepseek-v3',
                    'api_key': '',
                    'temperature': 0.1,
                    'timeout': 30,
                    'hy_source': 'web',
                    'hy_user': '',
                    'hy_token': '',
                    'agent_id': '',
                    'chat_id': ''
                },
                'translation_settings': {
                    'source_lang': 'en',
                    'target_lang': 'zh',
                    'preserve_format': True,
                    'max_retry': 3,
                    'concurrent_requests': 5
                },
                'logging': {
                    'level': 'INFO',
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                    'file': 'docslib_translator.log',
                    'max_size': 10 * 1024 * 1024,
                    'backup_count': 5
                },
                'cache': {
                    'enabled': True,
                    'dir': '.cache',
                    'max_size': 100 * 1024 * 1024,
                    'ttl': 30 * 24 * 60 * 60
                }
            }
            print(f"加载配置文件失败: {str(e)}，使用默认配置")
        
        # 设置日志记录器
        self.logger = get_logger('docslib_translator', self.config.get('logging', {}))
        self.logger.info("初始化翻译器")
        
        # 加载提示词
        try:
            self.prompts = get_translator_prompts()
        except Exception as e:
            self.logger.error(f"加载提示词配置失败: {str(e)}")
            self.prompts = {}
        
        # 初始化缓存
        self.cache = TranslationCache(self.config.get('cache', {}))
        
        # 初始化翻译服务
        self._init_translation_service()
        
        # 线程锁，用于保护并发访问
        self.lock = threading.RLock()
        
        # 翻译统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cached_requests': 0,
            'total_chars': 0,
            'total_time': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_tokens': 0,
            'avg_time_per_char': 0,
            'avg_time_per_token': 0
        }
    
    def _init_translation_service(self) -> None:
        """初始化翻译服务"""
        service_config = self.config.get('translation_service', {})
        provider = service_config.get('provider', 'yuanbao')
        
        if provider != 'yuanbao':
            self.logger.error(f"不支持的翻译服务提供商: {provider}，目前仅支持yuanbao")
            raise ValueError(f"不支持的翻译服务提供商: {provider}")
        
        self.translation_service = YuanbaoTranslationService(service_config, self.logger)
        
        if not self.translation_service.is_available():
            self.logger.warning("翻译服务不可用，请检查配置")
    
    def _get_file_type(self, file_path: Optional[str] = None, file_type: Optional[str] = None) -> str:
        """
        获取文件类型
        
        Args:
            file_path: 文件路径
            file_type: 文件类型，如果提供则优先使用
            
        Returns:
            str: 文件类型
        """
        if file_type:
            return file_type.lower()
        
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.md':
                return 'markdown'
            elif ext == '.mdx':
                return 'mdx'
            elif ext == '.tsx':
                return 'tsx'
            elif ext == '.jsx':
                return 'jsx'
            elif ext == '.txt':
                return 'txt'
        
        return 'default'
    
    def _get_prompts(self, file_type: str) -> Tuple[Optional[str], Optional[str]]:
        """
        获取指定文件类型的提示词
        
        Args:
            file_type: 文件类型
            
        Returns:
            Tuple[Optional[str], Optional[str]]: 系统提示词和用户提示词
        """
        if not self.prompts:
            return None, None
        
        # 尝试获取指定文件类型的提示词
        prompts = self.prompts.get(file_type)
        
        # 如果没有找到，使用默认提示词
        if not prompts and file_type != 'default':
            prompts = self.prompts.get('default')
        
        if not prompts:
            return None, None
        
        return prompts.get('system'), prompts.get('user')
    
    def translate_text(self, text: str, file_path: Optional[str] = None, file_type: Optional[str] = None) -> str:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            file_path: 文件路径，用于确定文件类型
            file_type: 文件类型，如果提供则优先使用
            
        Returns:
            str: 翻译后的文本
            
        Raises:
            TranslationError: 翻译失败时抛出
        """
        if not text.strip():
            return text
        
        # 获取翻译设置
        translation_settings = self.config.get('translation_settings', {})
        source_lang = translation_settings.get('source_lang', 'en')
        target_lang = translation_settings.get('target_lang', 'zh')
        max_retry = translation_settings.get('max_retry', 3)
        
        # 确定文件类型
        determined_file_type = self._get_file_type(file_path, file_type)
        
        # 更新统计信息
        with self.lock:
            self.stats['total_requests'] += 1
            self.stats['total_chars'] += len(text)
        
        # 检查缓存
        cached_result = self.cache.get(text, determined_file_type, source_lang, target_lang)
        if cached_result:
            self.logger.debug(f"使用缓存的翻译结果，文件类型: {determined_file_type}")
            with self.lock:
                self.stats['cached_requests'] += 1
            return cached_result
        
        # 获取提示词
        system_prompt, user_prompt = self._get_prompts(determined_file_type)
        
        # 尝试翻译，最多重试max_retry次
        for attempt in range(max_retry + 1):
            try:
                start_time = time.time()
                
                success, result, info = self.translation_service.translate(
                    text=text,
                    file_type=determined_file_type,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt
                )
                
                elapsed = time.time() - start_time
                
                if success:
                    # 更新统计信息
                    with self.lock:
                        self.stats['successful_requests'] += 1
                        self.stats['total_time'] += elapsed
                        
                        # 更新token统计
                        input_tokens = info.get('input_tokens', 0)
                        output_tokens = info.get('output_tokens', 0)
                        total_tokens = info.get('total_tokens', 0)
                        
                        self.stats['total_input_tokens'] += input_tokens
                        self.stats['total_output_tokens'] += output_tokens
                        self.stats['total_tokens'] += total_tokens
                        
                        # 计算平均值
                        if self.stats['total_chars'] > 0:
                            self.stats['avg_time_per_char'] = self.stats['total_time'] / self.stats['total_chars']
                        
                        if self.stats['total_tokens'] > 0:
                            self.stats['avg_time_per_token'] = self.stats['total_time'] / self.stats['total_tokens']
                    
                    # 缓存结果
                    self.cache.set(text, result, determined_file_type, source_lang, target_lang)
                    
                    # 记录详细的翻译信息
                    self.logger.info(
                        f"翻译完成: {len(text)}字符, {input_tokens}输入tokens, {output_tokens}输出tokens, "
                        f"耗时{elapsed:.2f}秒, 速度{len(text)/elapsed:.2f}字符/秒, {total_tokens/elapsed:.2f}tokens/秒"
                    )
                    
                    return result
                else:
                    if attempt < max_retry:
                        self.logger.warning(f"翻译失败，尝试重试 ({attempt + 1}/{max_retry}): {result}")
                        time.sleep(1)  # 等待1秒后重试
                    else:
                        # 更新统计信息
                        with self.lock:
                            self.stats['failed_requests'] += 1
                        
                        self.logger.error(f"翻译失败，已达到最大重试次数: {result}")
                        raise TranslationError(f"翻译失败: {result}")
                
            except Exception as e:
                if attempt < max_retry:
                    self.logger.warning(f"翻译过程中发生错误，尝试重试 ({attempt + 1}/{max_retry}): {str(e)}")
                    time.sleep(1)  # 等待1秒后重试
                else:
                    # 更新统计信息
                    with self.lock:
                        self.stats['failed_requests'] += 1
                    
                    self.logger.error(f"翻译过程中发生错误，已达到最大重试次数: {str(e)}")
                    raise TranslationError(f"翻译错误: {str(e)}")
    
    def translate_file(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        翻译文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            
        Returns:
            Dict[str, Any]: 翻译结果信息
            
        Raises:
            TranslationError: 翻译失败时抛出
        """
        self.logger.info(f"开始翻译文件: {input_file} -> {output_file}")
        
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 读取输入文件 - 尝试多种编码
            content = None
            encoding_used = None
            for encoding in ['utf-8', 'gbk', 'latin-1']:
                try:
                    with open(input_file, 'r', encoding=encoding) as f:
                        content = f.read()
                    encoding_used = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                raise TranslationError(f"无法读取文件: {input_file}, 不支持的编码格式")
            
            # 翻译文件内容
            start_time = time.time()
            translated_content = self.translate_text(content, file_path=input_file)
            elapsed = time.time() - start_time
            
            # 写入输出文件 - 始终使用UTF-8编码
            output_encoding = 'utf-8'
            
            with open(output_file, 'w', encoding=output_encoding) as f:
                f.write(translated_content)
            
            self.logger.info(f"文件翻译完成: {input_file}，使用{encoding_used}读取，{output_encoding}写入，耗时: {elapsed:.2f}秒")
            
            # 获取最后一次翻译的token统计
            last_request_stats = {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0
            }
            
            with self.lock:
                if self.stats['successful_requests'] > 0:
                    last_request_stats = {
                        'input_tokens': self.stats['total_input_tokens'],
                        'output_tokens': self.stats['total_output_tokens'],
                        'total_tokens': self.stats['total_tokens']
                    }
            
            return {
                'success': True,
                'input_file': input_file,
                'output_file': output_file,
                'elapsed': elapsed,
                'char_count': len(content),
                'input_tokens': last_request_stats['input_tokens'],
                'output_tokens': last_request_stats['output_tokens'],
                'total_tokens': last_request_stats['total_tokens']
            }
            
        except Exception as e:
            self.logger.error(f"翻译文件失败: {input_file}: {str(e)}", exc_info=True)
            raise TranslationError(f"翻译文件失败: {input_file}: {str(e)}")
    
    def translate_files(self, file_pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        批量翻译文件
        
        Args:
            file_pairs: 输入输出文件路径对列表 [(input_file, output_file), ...]
            
        Returns:
            Dict[str, Any]: 翻译结果信息
        """
        self.logger.info(f"开始批量翻译文件，共 {len(file_pairs)} 个文件")
        
        results = {
            'success': True,
            'total': len(file_pairs),
            'successful': 0,
            'failed': 0,
            'elapsed': 0,
            'char_count': 0,
            'total_tokens': 0,
            'details': []
        }
        
        start_time = time.time()
        
        # 获取并发请求数
        concurrent_requests = self.config.get('translation_settings', {}).get('concurrent_requests', 5)
        
        # 使用线程池并发翻译文件
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            # 提交所有翻译任务
            future_to_file = {
                executor.submit(self._translate_file_wrapper, input_file, output_file): (input_file, output_file)
                for input_file, output_file in file_pairs
            }
            
            # 处理翻译结果
            for future in future_to_file:
                input_file, output_file = future_to_file[future]
                try:
                    result = future.result()
                    results['successful'] += 1
                    results['elapsed'] += result['elapsed']
                    results['char_count'] += result['char_count']
                    results['total_tokens'] += result.get('total_tokens', 0)
                    results['details'].append({
                        'input_file': input_file,
                        'output_file': output_file,
                        'success': True,
                        'elapsed': result['elapsed'],
                        'char_count': result['char_count'],
                        'total_tokens': result.get('total_tokens', 0)
                    })
                except Exception as e:
                    results['failed'] += 1
                    results['details'].append({
                        'input_file': input_file,
                        'output_file': output_file,
                        'success': False,
                        'error': str(e)
                    })
        
        # 更新总耗时
        results['elapsed'] = time.time() - start_time
        
        # 更新成功标志
        results['success'] = results['failed'] == 0
        
        # 计算速度指标
        if results['elapsed'] > 0:
            results['chars_per_second'] = results['char_count'] / results['elapsed']
            results['tokens_per_second'] = results['total_tokens'] / results['elapsed'] if results['total_tokens'] > 0 else 0
        
        self.logger.info(
            f"批量翻译完成，成功: {results['successful']}，失败: {results['failed']}，"
            f"总耗时: {results['elapsed']:.2f}秒，"
            f"总字符: {results['char_count']}，"
            f"总tokens: {results['total_tokens']}，"
            f"速度: {results.get('chars_per_second', 0):.2f}字符/秒，"
            f"{results.get('tokens_per_second', 0):.2f}tokens/秒"
        )
        
        return results
    
    def _translate_file_wrapper(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        文件翻译包装器，用于线程池
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            
        Returns:
            Dict[str, Any]: 翻译结果信息
        """
        try:
            return self.translate_file(input_file, output_file)
        except Exception as e:
            self.logger.error(f"翻译文件失败: {input_file}: {str(e)}")
            raise e
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取翻译统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        with self.lock:
            stats_copy = dict(self.stats)
            
            # 计算平均时间
            if stats_copy['successful_requests'] > 0:
                stats_copy['avg_time'] = stats_copy['total_time'] / stats_copy['successful_requests']
            else:
                stats_copy['avg_time'] = 0
            
            # 计算缓存命中率
            if stats_copy['total_requests'] > 0:
                stats_copy['cache_hit_rate'] = stats_copy['cached_requests'] / stats_copy['total_requests']
            else:
                stats_copy['cache_hit_rate'] = 0
            
            # 计算平均token
            if stats_copy['successful_requests'] > 0:
                stats_copy['avg_input_tokens'] = stats_copy['total_input_tokens'] / stats_copy['successful_requests']
                stats_copy['avg_output_tokens'] = stats_copy['total_output_tokens'] / stats_copy['successful_requests']
                stats_copy['avg_total_tokens'] = stats_copy['total_tokens'] / stats_copy['successful_requests']
            else:
                stats_copy['avg_input_tokens'] = 0
                stats_copy['avg_output_tokens'] = 0
                stats_copy['avg_total_tokens'] = 0
            
            # 计算速度指标
            if stats_copy['total_time'] > 0:
                stats_copy['chars_per_second'] = stats_copy['total_chars'] / stats_copy['total_time']
                stats_copy['tokens_per_second'] = stats_copy['total_tokens'] / stats_copy['total_time'] if stats_copy['total_tokens'] > 0 else 0
            else:
                stats_copy['chars_per_second'] = 0
                stats_copy['tokens_per_second'] = 0
            
            return stats_copy
    
    def reset_stats(self) -> None:
        """重置翻译统计信息"""
        with self.lock:
            self.stats = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'cached_requests': 0,
                'total_chars': 0,
                'total_time': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_tokens': 0,
                'avg_time_per_char': 0,
                'avg_time_per_token': 0
            }
        
        self.logger.info("已重置翻译统计信息")
    
    def clear_cache(self) -> None:
        """清空翻译缓存"""
        self.cache.clear()
        self.logger.info("已清空翻译缓存") 