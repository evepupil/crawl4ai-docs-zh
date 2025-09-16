"""
DocsLib CLI 主入口模块

允许将包作为模块直接执行: python -m docslib_cli
"""

import sys
from docslib_cli.main import main

if __name__ == "__main__":
    sys.exit(main()) 