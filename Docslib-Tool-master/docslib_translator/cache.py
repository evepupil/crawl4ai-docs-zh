"""
缓存模块

该模块提供翻译结果的缓存功能，减少重复翻译请求。
"""

import os
import json
import time
import hashlib
from typing import Dict, Any, Optional

class TranslationCache:
    """翻译缓存类，用于缓存翻译结果"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化缓存
        
        Args:
            config: 缓存配置
        """
        self.enabled = config.get('enabled', True)
        self.cache_dir = config.get('dir', '.cache')
        self.max_size = config.get('max_size', 100 * 1024 * 1024)  # 默认100MB
        self.ttl = config.get('ttl', 30 * 24 * 60 * 60)  # 默认30天
        
        # 创建缓存目录
        if self.enabled and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # 缓存索引
        self.index_file = os.path.join(self.cache_dir, 'index.json')
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """
        加载缓存索引
        
        Returns:
            Dict[str, Any]: 缓存索引
        """
        if not self.enabled or not os.path.exists(self.index_file):
            return {'entries': {}, 'total_size': 0}
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {'entries': {}, 'total_size': 0}
    
    def _save_index(self) -> None:
        """保存缓存索引"""
        if not self.enabled:
            return
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def _generate_key(self, text: str, file_type: str, source_lang: str, target_lang: str) -> str:
        """
        生成缓存键
        
        Args:
            text: 要翻译的文本
            file_type: 文件类型
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            str: 缓存键
        """
        # 使用文本内容、文件类型和语言对生成哈希键
        key_data = f"{text}|{file_type}|{source_lang}|{target_lang}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """
        获取缓存文件路径
        
        Args:
            key: 缓存键
            
        Returns:
            str: 缓存文件路径
        """
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, text: str, file_type: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        获取缓存的翻译结果
        
        Args:
            text: 要翻译的文本
            file_type: 文件类型
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            Optional[str]: 缓存的翻译结果，如果不存在则返回None
        """
        if not self.enabled:
            return None
        
        key = self._generate_key(text, file_type, source_lang, target_lang)
        
        # 检查索引中是否存在该键
        if key not in self.index['entries']:
            return None
        
        # 检查缓存是否过期
        entry = self.index['entries'][key]
        if time.time() - entry['timestamp'] > self.ttl:
            # 缓存过期，删除
            self._remove(key)
            return None
        
        # 读取缓存文件
        cache_path = self._get_cache_path(key)
        if not os.path.exists(cache_path):
            # 缓存文件不存在，从索引中删除
            self._remove(key)
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                return cache_data['translated_text']
        except Exception:
            # 读取失败，从索引中删除
            self._remove(key)
            return None
    
    def set(self, text: str, translated_text: str, file_type: str, source_lang: str, target_lang: str) -> None:
        """
        设置翻译结果缓存
        
        Args:
            text: 原文本
            translated_text: 翻译后的文本
            file_type: 文件类型
            source_lang: 源语言
            target_lang: 目标语言
        """
        if not self.enabled:
            return
        
        key = self._generate_key(text, file_type, source_lang, target_lang)
        cache_path = self._get_cache_path(key)
        
        # 缓存数据
        cache_data = {
            'original_text': text,
            'translated_text': translated_text,
            'file_type': file_type,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'timestamp': time.time()
        }
        
        # 写入缓存文件
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        # 更新索引
        size = os.path.getsize(cache_path)
        self.index['entries'][key] = {
            'file_type': file_type,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'timestamp': cache_data['timestamp'],
            'size': size
        }
        self.index['total_size'] = self.index.get('total_size', 0) + size
        
        # 保存索引
        self._save_index()
        
        # 检查缓存大小是否超过限制，如果超过则清理最旧的缓存
        self._cleanup_if_needed()
    
    def _remove(self, key: str) -> None:
        """
        删除缓存
        
        Args:
            key: 缓存键
        """
        if key in self.index['entries']:
            # 从总大小中减去
            self.index['total_size'] -= self.index['entries'][key].get('size', 0)
            
            # 从索引中删除
            del self.index['entries'][key]
            
            # 删除缓存文件
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
            
            # 保存索引
            self._save_index()
    
    def _cleanup_if_needed(self) -> None:
        """如果缓存大小超过限制，清理最旧的缓存"""
        if self.index['total_size'] <= self.max_size:
            return
        
        # 按时间戳排序
        sorted_entries = sorted(
            self.index['entries'].items(),
            key=lambda x: x[1]['timestamp']
        )
        
        # 删除最旧的缓存，直到总大小低于限制
        for key, _ in sorted_entries:
            self._remove(key)
            if self.index['total_size'] <= self.max_size * 0.8:  # 清理到80%
                break
    
    def clear(self) -> None:
        """清空所有缓存"""
        if not self.enabled:
            return
        
        # 删除所有缓存文件
        for key in list(self.index['entries'].keys()):
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
        
        # 重置索引
        self.index = {'entries': {}, 'total_size': 0}
        self._save_index() 