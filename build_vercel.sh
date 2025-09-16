#!/bin/bash

# Vercel 构建脚本
echo "开始构建 Crawl4AI 中文文档..."

# 设置 Python 路径 (Vercel 特定)
export PYTHONPATH=/vercel/.pyenv/versions/3.9.0/lib/python3.9/site-packages:$PYTHONPATH

# 安装 MkDocs 和相关依赖
echo "安装 MkDocs 和相关依赖..."
pip install --no-cache-dir mkdocs mkdocs-terminal pymdown-extensions

# 验证安装
echo "验证 MkDocs 安装..."
mkdocs --version

# 使用中文配置构建文档
echo "使用 mkdocs_zh.yml 构建文档..."
mkdocs build -f mkdocs_zh.yml

# 验证构建结果
if [ -d "site" ]; then
    echo "文档构建成功完成"
    FILE_COUNT=$(find site -type f | wc -l)
    echo "站点文件数: $FILE_COUNT"
    
    # 列出主要文件
    echo "主要文件:"
    ls -la site/ | head -10
else
    echo "错误: 构建失败，site 目录不存在"
    exit 1
fi

echo "构建完成"