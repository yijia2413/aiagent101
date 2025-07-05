#!/bin/bash

echo "🚀 启动AI多Agent产品Demo生成器..."

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

# 检查.env文件
if [ ! -f .env ]; then
    echo "⚠️ 未找到.env文件，正在创建..."
    cp .env.example .env
    echo "📝 请编辑.env文件，配置您的API密钥"
    echo "💡 支持的API提供商: OpenAI, DeepSeek, Azure, Moonshot, 通义千问"
    
    # 检查是否有编辑器
    if command -v nano &> /dev/null; then
        read -p "是否现在编辑.env文件? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            nano .env
        fi
    elif command -v vim &> /dev/null; then
        read -p "是否现在编辑.env文件? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            vim .env
        fi
    else
        echo "请手动编辑.env文件"
    fi
fi

# 检查API密钥
source .env

# 获取API提供商
API_PROVIDER=${API_PROVIDER:-openai}
API_PROVIDER=$(echo "$API_PROVIDER" | tr '[:upper:]' '[:lower:]')

echo "🔧 当前API提供商: $API_PROVIDER"

# 根据提供商检查对应的API密钥
api_key_found=false
case $API_PROVIDER in
    "deepseek")
        if [ -n "$DEEPSEEK_API_KEY" ] && [ "$DEEPSEEK_API_KEY" != "your_deepseek_api_key_here" ]; then
            api_key_found=true
            echo "✅ DeepSeek API密钥已配置"
        else
            echo "❌ 请在.env文件中设置有效的DEEPSEEK_API_KEY"
        fi
        ;;
    "azure")
        if [ -n "$AZURE_API_KEY" ] && [ "$AZURE_API_KEY" != "your_azure_api_key_here" ]; then
            api_key_found=true
            echo "✅ Azure API密钥已配置"
        else
            echo "❌ 请在.env文件中设置有效的AZURE_API_KEY"
        fi
        ;;
    "moonshot")
        if [ -n "$MOONSHOT_API_KEY" ] && [ "$MOONSHOT_API_KEY" != "your_moonshot_api_key_here" ]; then
            api_key_found=true
            echo "✅ Moonshot API密钥已配置"
        else
            echo "❌ 请在.env文件中设置有效的MOONSHOT_API_KEY"
        fi
        ;;
    "qwen")
        if [ -n "$QWEN_API_KEY" ] && [ "$QWEN_API_KEY" != "your_qwen_api_key_here" ]; then
            api_key_found=true
            echo "✅ 通义千问API密钥已配置"
        else
            echo "❌ 请在.env文件中设置有效的QWEN_API_KEY"
        fi
        ;;
    *)
        if [ -n "$OPENAI_API_KEY" ] && [ "$OPENAI_API_KEY" != "your_openai_api_key_here" ]; then
            api_key_found=true
            echo "✅ OpenAI API密钥已配置"
        else
            echo "❌ 请在.env文件中设置有效的OPENAI_API_KEY"
        fi
        ;;
esac

if [ "$api_key_found" = false ]; then
    echo "💡 请编辑.env文件，设置对应的API密钥后重新运行"
    exit 1
fi

# 安装依赖
echo "📦 检查并安装依赖包..."
pip install -r requirements.txt

# 创建生成目录
mkdir -p generated_demo

# 启动应用
echo "🌟 启动Web应用..."
echo "📍 访问地址: http://localhost:7860"
echo "🔄 正在启动，请稍候..."

python app.py 