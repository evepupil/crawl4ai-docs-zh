#!/usr/bin/env python
"""
DocsLib 文档框架检测器安装脚本
"""

from setuptools import setup, find_packages

setup(
    name="docslib-detector",
    version="0.1.0",
    description="DocsLib 文档框架检测工具",
    author="DocsLib Team",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=5.1",
    ],
    entry_points={
        "console_scripts": [
            "docslib-detector=docslib_detector.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
) 