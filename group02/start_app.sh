#!/bin/bash

echo "🚀 启动AI多Agent产品Demo生成器..."
echo "📍 当前目录: $(pwd)"
echo "🐍 使用Python版本: $(/Users/jiangchang/.pyenv/versions/3.8.20/bin/python --version)"

# 设置pyenv镜像源环境变量
export PYTHON_BUILD_MIRROR_URL="https://mirrors.huaweicloud.com/python/"

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: 没有找到.env文件，请复制.env.example并配置API密钥"
    echo "   cp .env.example .env"
    echo "   然后编辑.env文件，设置你的API密钥"
    exit 1
fi

# 启动应用
echo "🌟 启动应用..."
/Users/jiangchang/.pyenv/versions/3.8.20/bin/python app.py 