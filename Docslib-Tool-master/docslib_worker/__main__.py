"""
主入口模块

使用 python -m docslib_worker 运行包
"""

import sys
from docslib_worker.cli.worker_cli import main

if __name__ == '__main__':
    sys.exit(main()) 