#!/usr/bin/env python
"""
DocsLib 翻译器安装脚本
"""

from setuptools import setup, find_packages

setup(
    name="docslib-translator",
    version="0.1.0",
    description="DocsLib 文档翻译工具",
    author="DocsLib Team",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=5.1",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "docslib-translator=docslib_translator.__main__:main",
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