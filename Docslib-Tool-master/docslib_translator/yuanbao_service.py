"""
元宝AI翻译服务模块

该模块提供与元宝AI翻译API的交互功能。
"""

import json
import time
import re
from typing import Dict, Any, Optional, Tuple, List
import logging
import requests
from openai import OpenAI

# 导入全局日志管理
from docslib_core.utils import get_logger

class YuanbaoTranslationService:
    """元宝AI翻译服务类"""
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化元宝AI翻译服务
        
        Args:
            config: 服务配置
            logger: 日志记录器，如果为None则创建新的日志记录器
        """
        # 基本配置
        self.base_url = config.get('base_url', 'http://localhost:8000/v1/')
        self.model = config.get('model', 'deepseek-v3')
        self.api_key = config.get('api_key', '')
        self.timeout = config.get('timeout', 30)
        self.temperature = config.get('temperature', 0.1)
        
        # 元宝特有参数
        self.hy_source = config.get('hy_source', 'web')
        self.hy_user = config.get('hy_user', '')
        self.hy_token = config.get('hy_token', '')
        self.agent_id = config.get('agent_id', '')
        self.chat_id = config.get('chat_id', '')
        
        # 日志记录器
        self.logger = logger or get_logger('docslib_translator')
        
        # 初始化OpenAI客户端
        self.client = OpenAI(base_url=self.base_url, api_key=self.hy_token)
        self.logger.info(f"已初始化腾讯元宝AI服务，模型: {self.model}")
        # 验证配置
        if not self.hy_user or not self.hy_token:
            self.logger.warning("元宝AI配置不完整，翻译功能可能不可用")
    
    def is_available(self) -> bool:
        """
        检查翻译服务是否可用
        
        Returns:
            bool: 服务是否可用
        """
        return bool(self.hy_user and self.hy_token)
    
    def translate(self, 
                 text: str, 
                 file_type: str, 
                 source_lang: str, 
                 target_lang: str,
                 system_prompt: Optional[str] = None,
                 user_prompt: Optional[str] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            file_type: 文件类型
            source_lang: 源语言
            target_lang: 目标语言
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            
        Returns:
            Tuple[bool, str, Dict[str, Any]]: 
                - 是否成功
                - 翻译结果或错误信息
                - 额外信息（如API响应详情）
        """
        if not self.is_available():
            self.logger.error("元宝AI翻译服务不可用，请检查配置")
            return False, "翻译服务不可用，请检查配置", {}
        
        try:
            self.logger.info(f"开始翻译 {file_type} 类型文件，源语言: {source_lang}，目标语言: {target_lang}")
            self.logger.debug(f"翻译文本长度: {len(text)} 字符")
            
            # 构建消息
            messages = self._build_messages(text, file_type, source_lang, target_lang, system_prompt, user_prompt)
            
            # 估算token数量
            input_tokens = self._estimate_tokens(messages)
            
            # 记录开始时间
            start_time = time.time()
            # 调用API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                stream=True,
                extra_body={
                    "hy_source": self.hy_source,
                    "hy_user": self.hy_user,
                    "hy_token": self.hy_token,
                    "agent_id": self.agent_id,
                    "chat_id": self.chat_id,
                    "should_remove_conversation": False,
                },
            )
            
            # 拼接流式响应
            translated_text = ""
            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    line = (json.loads(chunk.choices[0].delta.content).get("msg", "") or "")
                    translated_text += line
            
            # 记录结束时间
            end_time = time.time()
            elapsed = end_time - start_time
            
            # 估算输出token数量
            output_tokens = self._estimate_tokens([{"role": "assistant", "content": translated_text}])
            
            self.logger.info(f"翻译完成，耗时: {elapsed:.2f}秒，输入tokens: {input_tokens}，输出tokens: {output_tokens}")
            
            return True, translated_text, {
                'elapsed': elapsed,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'file_type': file_type,
                'char_count': len(text),
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': input_tokens + output_tokens
            }
            
        except Exception as e:
            self.logger.error(f"翻译过程中发生错误: {str(e)}", exc_info=True)
            return False, f"翻译错误: {str(e)}", {'error': str(e)}
    
    def _build_messages(self, 
                       text: str, 
                       file_type: str, 
                       source_lang: str, 
                       target_lang: str,
                       system_prompt: Optional[str] = None,
                       user_prompt: Optional[str] = None) -> List[Dict[str, str]]:
        """
        构建API请求消息
        
        Args:
            text: 要翻译的文本
            file_type: 文件类型
            source_lang: 源语言
            target_lang: 目标语言
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            
        Returns:
            List[Dict[str, str]]: 消息列表
        """
        # 构建消息
        messages = []
        
        # 添加系统提示词
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        else:
            # 默认系统提示词
            messages.append({
                "role": "system",
                "content": f"你是一个专业的文档翻译助手，负责将{source_lang}文档翻译成{target_lang}。请保持原始格式和结构不变。"
            })
        
        # 添加用户提示词和文本
        if user_prompt:
            user_content = user_prompt.replace("{text}", text)
        else:
            user_content = f"请将以下{file_type}文本从{source_lang}翻译成{target_lang}，保持原文格式和结构不变：\n\n{text}"
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        return messages
    
    def _estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        估算消息的token数量
        
        Args:
            messages: 消息列表
            
        Returns:
            int: 估算的token数量
        """
        # 简单估算：假设1个汉字约等于1.5个token，1个英文单词约等于1.3个token
        total_tokens = 0
        
        for message in messages:
            content = message.get("content", "")
            
            # 计算中文字符数
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
            
            # 计算英文单词数
            english_words = len(re.findall(r'[a-zA-Z]+', content))
            
            # 计算数字、标点和空格
            other_chars = len(re.sub(r'[\u4e00-\u9fff]|[a-zA-Z]+', '', content))
            
            # 估算token
            message_tokens = chinese_chars * 1.5 + english_words * 1.3 + other_chars * 0.5
            
            # 添加角色标记的token（大约10个token）
            message_tokens += 10
            
            total_tokens += int(message_tokens)
        
        return total_tokens 