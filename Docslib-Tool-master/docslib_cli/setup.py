#!/usr/bin/env python
"""
DocsLib CLI 安装脚本
"""

from setuptools import setup, find_packages

setup(
    name="docslib-cli",
    version="0.1.0",
    description="DocsLib 命令行工具",
    long_description="提供DocsLib项目的命令行接口，包括翻译器和文档工作器的命令",
    author="DocsLib Team",
    author_email="info@docslib.example.com",
    url="https://github.com/docslib/docslib-cli",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "docslib-core>=0.1.0",
        "docslib-worker>=0.1.0",
        "docslib-translator>=0.1.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        'console_scripts': [
            'docslib=docslib_cli.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 