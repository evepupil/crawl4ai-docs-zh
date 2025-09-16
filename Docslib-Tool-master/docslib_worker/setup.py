#!/usr/bin/env python
"""
DocsLib Worker 安装脚本
"""

from setuptools import setup, find_packages

setup(
    name="docslib-worker",
    version="0.1.0",
    description="DocsLib 文档翻译工作器",
    long_description="用于将文档框架（如MkDocs、Docusaurus等）的文档翻译成其他语言",
    author="DocsLib Team",
    author_email="info@docslib.example.com",
    url="https://github.com/docslib/docslib-worker",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "docslib-core>=0.1.0",
        "docslib-translator>=0.1.0",
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