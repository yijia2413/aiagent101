import yaml
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化配置管理器"""
        self.config_path = config_path
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return self.get_default_config()
            
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "LLM_GPT": {
                "default_llm": {
                    "api_key": "your-api-key",
                    "api_base": "https://api.openai.com/v1",
                    "api_type": "openai",
                    "timeout": 120,
                    "default_model": {
                        "model_name": "gpt-3.5-turbo",
                        "temperature": 0.01,
                        "max_tokens": 4096
                    }
                }
            }
        }
        
    def get_llm_config(self, llm_name: str = "default_llm") -> Dict[str, Any]:
        """获取LLM配置，自动将api_base转换为base_url"""
        if "LLM_GPT" in self.config and llm_name in self.config["LLM_GPT"]:
            llm_config = self.config["LLM_GPT"][llm_name]
            # 兼容api_base和base_url
            base_url = llm_config.get("base_url") or llm_config.get("api_base")
            if not base_url:
                raise ValueError(f"未找到base_url或api_base字段: {llm_name}")
            config = {
                "config_list": [{
                    "model": llm_config["default_model"]["model_name"],
                    "api_key": llm_config["api_key"],
                    "base_url": base_url,
                    "api_type": llm_config["api_type"],
                    "timeout": llm_config["timeout"]
                }],
                "temperature": llm_config["default_model"]["temperature"],
                "max_tokens": llm_config["default_model"]["max_tokens"]
            }
            return config
        else:
            raise ValueError(f"未找到LLM配置: {llm_name}")
        
    def get_available_llms(self) -> list:
        """获取可用的LLM列表"""
        if "LLM_GPT" in self.config:
            return list(self.config["LLM_GPT"].keys())
        return [] 