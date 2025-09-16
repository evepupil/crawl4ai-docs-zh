#!/usr/bin/env python
"""
DocsLib 诊断工具

用于检测和修复 DocsLib 工具集的常见问题
"""

import os
import sys
import importlib
import platform
import subprocess
import pkg_resources

# 颜色输出函数
def print_color(text, color="green"):
    """打印彩色文本"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    
    # Windows CMD不支持ANSI颜色，除非使用了特殊处理
    if platform.system() == "Windows" and "ANSICON" not in os.environ:
        print(text)
    else:
        print(f"{colors.get(color, colors['green'])}{text}{colors['reset']}")

def check_python_version():
    """检查Python版本"""
    print_color("检查Python版本...", "blue")
    
    major, minor, _ = platform.python_version_tuple()
    version_str = f"{major}.{minor}"
    
    if int(major) < 3 or (int(major) == 3 and int(minor) < 8):
        print_color(f"⚠️ 警告: Python版本过低 ({version_str}). DocsLib需要Python 3.8或更高版本。", "red")
        return False
    else:
        print_color(f"✓ Python版本 ({version_str}) 符合要求.", "green")
        return True

def check_package_installed(package_name):
    """检查包是否已安装"""
    try:
        pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False

def try_import_module(module_name):
    """尝试导入模块"""
    try:
        module = importlib.import_module(module_name)
        return True, None
    except ImportError as e:
        return False, str(e)

def check_modules():
    """检查必要模块是否可以导入"""
    print_color("\n检查必要模块...", "blue")
    
    modules = [
        ("docslib_core", "核心功能模块"),
        ("docslib_translator", "翻译引擎"),
        ("docslib_detector", "框架检测器"),
        ("docslib_worker", "文档工作器"),
        ("docslib_cli", "命令行接口")
    ]
    
    all_ok = True
    issues = []
    
    for module_name, description in modules:
        success, error = try_import_module(module_name)
        if success:
            print_color(f"✓ {module_name} ({description}) 导入成功", "green")
        else:
            all_ok = False
            package_name = module_name.replace("_", "-")
            if check_package_installed(package_name):
                issues.append(f"❌ {module_name} 已安装但无法导入: {error}")
            else:
                issues.append(f"❌ {module_name} 未安装")
    
    for issue in issues:
        print_color(issue, "red")
    
    return all_ok

def check_path():
    """检查Python路径"""
    print_color("\n检查Python路径...", "blue")
    
    for path in sys.path:
        print_color(f"  {path}", "yellow")
    
    return True

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"错误: {e}\n输出: {e.stdout}\n错误输出: {e.stderr}"

def fix_issues():
    """尝试修复问题"""
    print_color("\n尝试修复问题...", "blue")
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查安装脚本是否存在
    install_script = os.path.join(current_dir, "install.py")
    if not os.path.exists(install_script):
        print_color(f"❌ 未找到安装脚本: {install_script}", "red")
        return False
    
    # 运行安装脚本
    print_color("运行安装脚本...", "blue")
    success, output = run_command([sys.executable, install_script])
    
    if success:
        print_color("✓ 安装脚本执行成功", "green")
        return True
    else:
        print_color(f"❌ 安装脚本执行失败: {output}", "red")
        return False

def check_cli_command():
    """检查CLI命令是否可用"""
    print_color("\n检查CLI命令...", "blue")
    
    success, output = run_command([sys.executable, "-m", "docslib_cli", "--help"])
    
    if success:
        print_color("✓ docslib_cli 命令可用", "green")
        return True
    else:
        print_color(f"❌ docslib_cli 命令不可用: {output}", "red")
        return False

def main():
    """主函数"""
    print_color("DocsLib 诊断工具", "blue")
    print_color("=" * 50, "blue")
    
    # 检查Python版本
    python_ok = check_python_version()
    
    # 检查模块导入
    modules_ok = check_modules()
    
    # 检查路径
    path_ok = check_path()
    
    # 检查CLI命令
    cli_ok = check_cli_command()
    
    # 总结
    print_color("\n诊断总结", "blue")
    print_color("=" * 50, "blue")
    
    if python_ok and modules_ok and path_ok and cli_ok:
        print_color("✅ 所有检查通过，DocsLib工具集应该可以正常工作。", "green")
        return 0
    else:
        print_color("⚠️ 发现一些问题需要解决:", "yellow")
        
        if not python_ok:
            print_color("  - Python版本过低，请升级到Python 3.8或更高版本", "yellow")
        
        if not modules_ok:
            print_color("  - 一些必要模块无法导入", "yellow")
        
        if not cli_ok:
            print_color("  - CLI命令不可用", "yellow")
        
        print_color("\n是否尝试修复这些问题? [y/N]", "yellow")
        choice = input().strip().lower()
        
        if choice == 'y':
            if fix_issues():
                print_color("\n🎉 问题修复完成，请重新运行诊断工具检查结果。", "green")
            else:
                print_color("\n❌ 无法自动修复问题，请尝试手动安装:", "red")
                print_color("  1. 确保Python版本 >= 3.8", "yellow")
                print_color("  2. 运行以下命令:", "yellow")
                print_color("     pip install -e docslib_core", "blue")
                print_color("     pip install -e docslib_translator", "blue")
                print_color("     pip install -e docslib_detector", "blue")
                print_color("     pip install -e docslib_worker", "blue")
                print_color("     pip install -e docslib_cli", "blue")
                print_color("     pip install -e .", "blue")
        else:
            print_color("\n退出诊断，未进行修复。", "yellow")
        
        return 1

if __name__ == "__main__":
    sys.exit(main()) 