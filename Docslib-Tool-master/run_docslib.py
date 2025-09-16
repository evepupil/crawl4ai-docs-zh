#!/usr/bin/env python
"""
DocsLib CLI 启动器

此脚本用于直接运行 DocsLib CLI，绕过常规的导入机制
"""

import os
import sys
import importlib.util
import runpy

def add_module_to_path(module_name):
    """将模块目录添加到 Python 路径"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.join(current_dir, module_name)
    
    if os.path.exists(module_path) and module_path not in sys.path:
        sys.path.insert(0, module_path)
        return True
    return False

def import_module_from_path(module_name, module_path):
    """从指定路径导入模块"""
    try:
        spec = importlib.util.spec_from_file_location(
            module_name,
            os.path.join(module_path, "__init__.py")
        )
        if not spec:
            return False
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return True
    except Exception as e:
        print(f"警告: 无法导入 {module_name}: {e}")
        return False

def main():
    """主函数"""
    # 获取命令行参数
    args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
    
    # 添加所有必要模块到路径
    modules = ["docslib_core", "docslib_translator", "docslib_detector", "docslib_worker", "docslib_cli"]
    for module in modules:
        add_module_to_path(module)
    
    # 确保所有模块都可以导入
    current_dir = os.path.dirname(os.path.abspath(__file__))
    success = True
    
    for module in modules:
        module_path = os.path.join(current_dir, module)
        if not import_module_from_path(module, module_path):
            success = False
    
    if not success:
        print("错误: 无法导入所有必要模块。")
        print("请运行 python fix_imports.py 修复导入问题，或使用管理员权限安装包。")
        return 1
    
    # 修改命令行参数，移除脚本名称
    sys.argv = ["docslib"] + args
    
    try:
        # 运行 docslib_cli 的 main 模块
        runpy.run_module("docslib_cli.main", run_name="__main__")
        return 0
    except Exception as e:
        print(f"错误: 运行 docslib_cli 失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 