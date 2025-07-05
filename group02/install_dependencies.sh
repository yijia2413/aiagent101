#!/bin/bash

echo "📦 开始安装AI多Agent产品Demo生成器依赖..."

# 设置PyPI镜像源
PYPI_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"
echo "🔧 使用清华大学PyPI镜像源: $PYPI_INDEX"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 请先安装Python3"
    exit 1
fi

# 检查pip
if ! command -v pip &> /dev/null; then
    echo "❌ 请先安装pip"
    exit 1
fi

# 升级pip
echo "🔧 升级pip..."
python -m pip install --upgrade pip -i $PYPI_INDEX

# 尝试安装autogen的几种方式
echo "🤖 尝试安装AutoGen..."

# 方式1：尝试pyautogen
echo "方式1: 尝试安装 pyautogen..."
if pip install pyautogen>=0.2.0 -i $PYPI_INDEX; then
    echo "✅ pyautogen 安装成功"
    autogen_installed=true
else
    echo "❌ pyautogen 安装失败，尝试其他方式..."
    autogen_installed=false
fi

# 方式2：如果方式1失败，尝试autogen-agentchat
if [ "$autogen_installed" = false ]; then
    echo "方式2: 尝试安装 autogen-agentchat..."
    if pip install autogen-agentchat>=0.2.0 -i $PYPI_INDEX; then
        echo "✅ autogen-agentchat 安装成功"
        autogen_installed=true
    else
        echo "❌ autogen-agentchat 安装失败，尝试从源码安装..."
        autogen_installed=false
    fi
fi

# 方式3：从GitHub源码安装
if [ "$autogen_installed" = false ]; then
    echo "方式3: 从GitHub源码安装..."
    if pip install git+https://github.com/microsoft/autogen.git; then
        echo "✅ 从源码安装AutoGen成功"
        autogen_installed=true
    else
        echo "❌ 从源码安装也失败了"
        autogen_installed=false
    fi
fi

# 方式4：最后尝试，使用预发布版本
if [ "$autogen_installed" = false ]; then
    echo "方式4: 尝试预发布版本..."
    if pip install --pre pyautogen -i $PYPI_INDEX; then
        echo "✅ 预发布版本安装成功"
        autogen_installed=true
    else
        echo "❌ 所有方式都失败了"
        autogen_installed=false
    fi
fi

if [ "$autogen_installed" = false ]; then
    echo "💡 AutoGen安装失败，请尝试手动安装："
    echo "   pip install pyautogen -i $PYPI_INDEX"
    echo "   或者："
    echo "   pip install autogen-agentchat -i $PYPI_INDEX"
    echo "   或者："
    echo "   pip install git+https://github.com/microsoft/autogen.git"
    exit 1
fi

# 安装其他依赖
echo "📦 安装其他依赖包..."

# 核心依赖
pip install openai>=1.0.0 -i $PYPI_INDEX
pip install gradio>=4.0.0 -i $PYPI_INDEX
pip install python-dotenv>=1.0.0 -i $PYPI_INDEX

# Web和API相关
pip install requests>=2.31.0 -i $PYPI_INDEX
pip install flask>=2.3.0 -i $PYPI_INDEX
pip install flask-cors>=4.0.0 -i $PYPI_INDEX

# 数据处理
pip install pandas>=2.0.0 -i $PYPI_INDEX
pip install numpy>=1.24.0 -i $PYPI_INDEX

# 系统和环境
pip install psutil>=5.9.0 -i $PYPI_INDEX

# 错误处理
pip install tenacity>=8.2.0 -i $PYPI_INDEX

echo "✅ 所有依赖安装完成！"
echo "🚀 现在可以运行 python app.py 启动应用" 