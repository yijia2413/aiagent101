import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API提供商配置
def get_api_config():
    """根据环境变量选择API提供商"""
    
    # 获取API提供商类型
    api_provider = os.getenv("API_PROVIDER", "openai").lower()
    
    if api_provider == "deepseek":
        return {
            "config_list": [
                {
                    "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                    "api_key": os.getenv("DEEPSEEK_API_KEY"),
                    "base_url": os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
                    "api_type": "openai",  # DeepSeek兼容OpenAI API格式
                }
            ],
            "temperature": float(os.getenv("API_TEMPERATURE", "0.7")),
            "timeout": int(os.getenv("API_TIMEOUT", "120")),
        }
    
    elif api_provider == "azure":
        return {
            "config_list": [
                {
                    "model": os.getenv("AZURE_MODEL", "gpt-4"),
                    "api_key": os.getenv("AZURE_API_KEY"),
                    "base_url": os.getenv("AZURE_API_BASE"),
                    "api_type": "azure",
                    "api_version": os.getenv("AZURE_API_VERSION", "2023-05-15"),
                }
            ],
            "temperature": float(os.getenv("API_TEMPERATURE", "0.7")),
            "timeout": int(os.getenv("API_TIMEOUT", "120")),
        }
    
    elif api_provider == "moonshot":
        return {
            "config_list": [
                {
                    "model": os.getenv("MOONSHOT_MODEL", "moonshot-v1-8k"),
                    "api_key": os.getenv("MOONSHOT_API_KEY"),
                    "base_url": os.getenv("MOONSHOT_API_BASE", "https://api.moonshot.cn/v1"),
                    "api_type": "openai",
                }
            ],
            "temperature": float(os.getenv("API_TEMPERATURE", "0.7")),
            "timeout": int(os.getenv("API_TIMEOUT", "120")),
        }
    
    elif api_provider == "qwen":
        return {
            "config_list": [
                {
                    "model": os.getenv("QWEN_MODEL", "qwen-turbo"),
                    "api_key": os.getenv("QWEN_API_KEY"),
                    "base_url": os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                    "api_type": "openai",
                }
            ],
            "temperature": float(os.getenv("API_TEMPERATURE", "0.7")),
            "timeout": int(os.getenv("API_TIMEOUT", "120")),
        }
    
    else:  # 默认使用OpenAI
        return {
            "config_list": [
                {
                    "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "base_url": os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
                    "api_type": "openai",
                }
            ],
            "temperature": float(os.getenv("API_TEMPERATURE", "0.7")),
            "timeout": int(os.getenv("API_TIMEOUT", "120")),
        }

# 获取当前API配置
OPENAI_CONFIG = get_api_config()

# Agent配置
AGENT_CONFIG = {
    "cache_seed": 42,
    "max_consecutive_auto_reply": 10,
    "human_input_mode": "NEVER",
}

# 打印当前使用的API配置（用于调试）
def print_api_info():
    """打印当前API配置信息"""
    provider = os.getenv("API_PROVIDER", "openai").lower()
    model = OPENAI_CONFIG["config_list"][0]["model"]
    base_url = OPENAI_CONFIG["config_list"][0]["base_url"]
    
    print(f"🔧 当前API配置:")
    print(f"   提供商: {provider.upper()}")
    print(f"   模型: {model}")
    print(f"   API地址: {base_url}")
    print(f"   温度: {OPENAI_CONFIG['temperature']}")
    print(f"   超时: {OPENAI_CONFIG['timeout']}s") 