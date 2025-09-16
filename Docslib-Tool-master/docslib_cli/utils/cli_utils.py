"""
CLI 实用工具

提供通用的 CLI 功能，如输出格式化、进度显示等。
"""

import sys
import os
import time
from typing import Dict, List, Any, Optional, Callable
import json
import yaml

# 颜色代码
class Colors:
    """终端颜色代码"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(text: str, color: str) -> None:
    """
    打印彩色文本
    
    Args:
        text: 要打印的文本
        color: 颜色代码
    """
    print(f"{color}{text}{Colors.ENDC}")

def print_success(text: str) -> None:
    """打印成功消息"""
    print_colored(f"✓ {text}", Colors.GREEN)

def print_error(text: str) -> None:
    """打印错误消息"""
    print_colored(f"✗ {text}", Colors.RED)

def print_warning(text: str) -> None:
    """打印警告消息"""
    print_colored(f"! {text}", Colors.YELLOW)

def print_info(text: str) -> None:
    """打印信息消息"""
    print_colored(f"ℹ {text}", Colors.BLUE)

def print_header(text: str) -> None:
    """打印标题"""
    print("\n" + "=" * 80)
    print_colored(f" {text} ", Colors.HEADER + Colors.BOLD)
    print("=" * 80 + "\n")

def print_json(data: Dict[str, Any], indent: int = 2) -> None:
    """
    以 JSON 格式打印数据
    
    Args:
        data: 要打印的数据
        indent: 缩进空格数
    """
    print(json.dumps(data, indent=indent, ensure_ascii=False))

def print_yaml(data: Dict[str, Any]) -> None:
    """
    以 YAML 格式打印数据
    
    Args:
        data: 要打印的数据
    """
    print(yaml.dump(data, allow_unicode=True))

class ProgressBar:
    """简单的进度条实现"""
    
    def __init__(self, total: int, prefix: str = '', suffix: str = '', decimals: int = 1, 
                 length: int = 50, fill: str = '█', print_end: str = "\r"):
        """
        初始化进度条
        
        Args:
            total: 总迭代次数
            prefix: 前缀字符串
            suffix: 后缀字符串
            decimals: 百分比的小数位数
            length: 进度条的字符长度
            fill: 进度条填充字符
            print_end: 打印结束字符
        """
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.print_end = print_end
        self.iteration = 0
        self.start_time = time.time()
        
    def update(self, iteration: Optional[int] = None) -> None:
        """
        更新进度条
        
        Args:
            iteration: 当前迭代次数，如果为 None 则自增 1
        """
        if iteration is not None:
            self.iteration = iteration
        else:
            self.iteration += 1
            
        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (self.iteration / float(self.total)))
        filled_length = int(self.length * self.iteration // self.total)
        bar = self.fill * filled_length + '-' * (self.length - filled_length)
        
        # 计算剩余时间
        elapsed = time.time() - self.start_time
        if self.iteration > 0:
            eta = elapsed * (self.total / self.iteration - 1)
            eta_str = f"ETA: {int(eta // 60)}m {int(eta % 60)}s"
        else:
            eta_str = "ETA: --"
            
        # 打印进度条
        sys.stdout.write(f'\r{self.prefix} |{bar}| {percent}% {self.suffix} {eta_str}{self.print_end}')
        sys.stdout.flush()
        
        # 如果完成则换行
        if self.iteration == self.total:
            elapsed_str = f"用时: {int(elapsed // 60)}m {int(elapsed % 60)}s"
            sys.stdout.write(f'\r{self.prefix} |{bar}| {percent}% {self.suffix} {elapsed_str}\n')
            sys.stdout.flush()

def confirm_action(prompt: str = "确定要继续吗?") -> bool:
    """
    请求用户确认操作
    
    Args:
        prompt: 提示信息
        
    Returns:
        bool: 用户是否确认
    """
    response = input(f"{prompt} (y/n): ").lower().strip()
    return response == 'y' or response == 'yes'

def select_option(options: List[str], prompt: str = "请选择一个选项:") -> int:
    """
    让用户从列表中选择一个选项
    
    Args:
        options: 选项列表
        prompt: 提示信息
        
    Returns:
        int: 选择的选项索引
    """
    print(prompt)
    for i, option in enumerate(options):
        print(f"{i+1}. {option}")
        
    while True:
        try:
            choice = int(input("输入选项编号: "))
            if 1 <= choice <= len(options):
                return choice - 1
            print_error(f"请输入 1 到 {len(options)} 之间的数字")
        except ValueError:
            print_error("请输入有效的数字")

def get_input(prompt: str, default: Optional[str] = None, validator: Optional[Callable[[str], bool]] = None) -> str:
    """
    获取用户输入，支持默认值和验证
    
    Args:
        prompt: 提示信息
        default: 默认值
        validator: 验证函数
        
    Returns:
        str: 用户输入
    """
    prompt_text = f"{prompt} [{default}]: " if default else f"{prompt}: "
    
    while True:
        response = input(prompt_text).strip()
        
        if not response and default:
            response = default
            
        if validator and not validator(response):
            print_error("输入无效，请重试")
            continue
            
        return response 