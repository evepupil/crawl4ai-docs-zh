#!/usr/bin/env python
"""
DocsLib Core 安装脚本
"""

from setuptools import setup, find_packages

setup(
    name="docslib-core",
    version="0.1.0",
    description="DocsLib 核心功能模块",
    long_description="提供DocsLib项目的核心功能，包括配置管理、日志记录、进度跟踪等",
    author="DocsLib Team",
    author_email="info@docslib.example.com",
    url="https://github.com/docslib/docslib-core",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyyaml>=6.0",
    ],
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