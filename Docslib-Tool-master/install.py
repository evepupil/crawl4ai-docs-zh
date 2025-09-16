#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DocsLib 自动安装脚本

此脚本自动按正确顺序安装 DocsLib 工具集的所有组件
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

# 定义颜色代码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Windows CMD 不支持 ANSI 颜色代码，使用简单版本
if platform.system() == 'Windows' and not os.environ.get('TERM'):
    class Colors:
        HEADER = ''
        BLUE = ''
        GREEN = ''
        YELLOW = ''
        RED = ''
        ENDC = ''
        BOLD = ''
        UNDERLINE = ''

def print_header(text):
    """打印带颜色的标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {text} ==={Colors.ENDC}\n")

def print_step(text, step_num, total_steps):
    """打印安装步骤"""
    print(f"{Colors.BLUE}[{step_num}/{total_steps}] {text}...{Colors.ENDC}")

def print_success(text):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_error(text):
    """打印错误消息"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def run_command(cmd, cwd=None):
    """
    运行命令并返回结果
    
    Args:
        cmd (str): 要运行的命令
        cwd (str, optional): 工作目录
        
    Returns:
        tuple: (成功状态, 输出/错误信息)
    """
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            cwd=cwd,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # 确保即使stderr或stdout为None也能正常工作
        stderr = e.stderr.strip() if hasattr(e, 'stderr') and e.stderr else ""
        stdout = e.stdout.strip() if hasattr(e, 'stdout') and e.stdout else ""
        return False, stderr or stdout or f"命令执行失败，退出代码: {e.returncode}"
    except Exception as e:
        return False, f"执行命令时发生错误: {str(e)}"

def check_python_version():
    """检查 Python 版本是否满足要求"""
    print_step("检查 Python 版本", 1, 9)
    
    python_version = sys.version_info
    required_version = (3, 8)
    
    if python_version >= required_version:
        print_success(f"Python 版本 {python_version.major}.{python_version.minor}.{python_version.micro} 满足要求")
        return True
    else:
        print_error(f"Python 版本过低：{python_version.major}.{python_version.minor}.{python_version.micro}")
        print_warning(f"DocsLib 需要 Python {required_version[0]}.{required_version[1]} 或更高版本")
        return False

def check_pip():
    """检查 pip 是否可用"""
    print_step("检查 pip 可用性", 2, 9)
    
    success, output = run_command("pip --version")
    if success:
        print_success(f"pip 可用: {output}")
        return True
    else:
        print_error("pip 不可用")
        print_warning("请确保已正确安装 pip")
        return False

def get_project_root():
    """获取项目根目录"""
    current_dir = Path(os.path.abspath(os.path.dirname(__file__)))
    return current_dir

def install_component(component_path, step, total_steps, component_name):
    """安装指定组件"""
    print_step(f"安装 {component_name}", step, total_steps)
    
    component_dir = get_project_root() / component_path
    
    if not component_dir.exists():
        print_error(f"组件目录 {component_path} 不存在")
        return False
    
    success, output = run_command(f"pip install -e .", cwd=str(component_dir))
    
    if success:
        print_success(f"{component_name} 安装成功")
        return True
    else:
        print_error(f"{component_name} 安装失败")
        print_warning(f"错误信息: {output}")
        return False

def check_imports():
    """检查是否可以导入所有模块"""
    print_step("验证模块导入", 8, 9)
    
    modules = [
        "docslib_core", 
        "docslib_translator", 
        "docslib_detector", 
        "docslib_worker", 
        "docslib_cli"
    ]
    
    all_success = True
    for module in modules:
        try:
            __import__(module)
            print_success(f"成功导入 {module}")
        except ImportError as e:
            print_error(f"无法导入 {module}: {str(e)}")
            all_success = False
    
    return all_success

def create_config_dir():
    """创建配置目录"""
    print_step("创建配置目录", 9, 9)
    
    if platform.system() == 'Windows':
        config_dir = Path(os.path.expanduser("~")) / ".docslib"
    else:
        config_dir = Path(os.path.expanduser("~")) / ".docslib"
    
    logs_dir = config_dir / "logs"
    
    try:
        config_dir.mkdir(exist_ok=True)
        logs_dir.mkdir(exist_ok=True)
        print_success(f"配置目录创建成功: {config_dir}")
        return True
    except Exception as e:
        print_error(f"创建配置目录失败: {str(e)}")
        return False

def display_final_message(all_success):
    """显示最终安装消息"""
    if all_success:
        print_header("安装完成")
        print(f"{Colors.GREEN}DocsLib 工具集已成功安装!{Colors.ENDC}")
        print("\n使用以下命令查看帮助:")
        print(f"  {Colors.BOLD}docslib --help{Colors.ENDC}")
        print(f"  {Colors.BOLD}docslib translator --help{Colors.ENDC}")
        print(f"  {Colors.BOLD}docslib worker --help{Colors.ENDC}")
        print("\n如果遇到导入错误，请尝试使用备用工具:")
        print(f"  {Colors.BOLD}python fix_imports.py{Colors.ENDC}")
        print(f"  {Colors.BOLD}python run_docslib.py worker translate <源目录> <目标目录>{Colors.ENDC}")
    else:
        print_header("安装未完成")
        print(f"{Colors.YELLOW}DocsLib 工具集安装过程中遇到一些问题{Colors.ENDC}")
        print("\n请尝试运行以下命令手动安装组件:")
        print(f"  {Colors.BOLD}pip install -e docslib_core{Colors.ENDC}")
        print(f"  {Colors.BOLD}pip install -e docslib_translator{Colors.ENDC}")
        print(f"  {Colors.BOLD}pip install -e docslib_detector{Colors.ENDC}")
        print(f"  {Colors.BOLD}pip install -e docslib_worker{Colors.ENDC}")
        print(f"  {Colors.BOLD}pip install -e docslib_cli{Colors.ENDC}")
        print(f"  {Colors.BOLD}pip install -e .{Colors.ENDC}")
        print("\n如果问题仍然存在，请使用诊断工具:")
        print(f"  {Colors.BOLD}python fix_imports.py{Colors.ENDC}")

def main():
    """主函数"""
    print_header("DocsLib 安装程序")
    print("将按顺序安装 DocsLib 工具集的所有组件")
    print("此过程可能需要几分钟...")
    
    # 初始化成功状态追踪
    success_status = []
    
    # 检查 Python 版本
    success_status.append(check_python_version())
    
    # 检查 pip
    success_status.append(check_pip())
    
    # 安装组件
    components = [
        ("docslib_core", "DocsLib Core", 3),
        ("docslib_translator", "DocsLib Translator", 4),
        ("docslib_detector", "DocsLib Detector", 5),
        ("docslib_worker", "DocsLib Worker", 6),
        ("docslib_cli", "DocsLib CLI", 7),
    ]
    
    for component_path, component_name, step in components:
        success = install_component(component_path, step, 9, component_name)
        success_status.append(success)
        
        # 安装后暂停一下，给 Python 时间更新导入路径
        time.sleep(1)
    
    # 安装主包
    print_step("安装主包", 8, 9)
    success, output = run_command("pip install -e .")
    if success:
        print_success("主包安装成功")
        success_status.append(True)
    else:
        print_error("主包安装失败")
        print_warning(f"错误信息: {output}")
        success_status.append(False)
    
    # 验证导入
    success_status.append(check_imports())
    
    # 创建配置目录
    success_status.append(create_config_dir())
    
    # 显示最终消息
    all_success = all(success_status)
    display_final_message(all_success)
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main()) 