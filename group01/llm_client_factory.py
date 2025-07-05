#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM客户端工厂类
负责创建和缓存不同类型的模型客户端实例
"""

from typing import Dict, Type, Any
import autogen
from config_manager import ConfigManager

class LLMClientFactory:
    """
    模型客户端工厂类, 负责创建和缓存不同类型的模型客户端实例
    """
    # 缓存已创建的模型客户端实例
    _instances: Dict[str, Dict[str, Any]] = {}
    
    # 支持的模型客户端类型映射
    _client_types: Dict[str, str] = {
        "openai": "openai",
        "dashscope": "openai",  # 阿里云通义千问使用OpenAI兼容模式
        "deepseek": "openai",   # DeepSeek使用OpenAI兼容模式
    }
    
    @classmethod
    def clear_cache(cls) -> None:
        """清除缓存的模型客户端实例"""
        cls._instances.clear()
    
    @classmethod
    def get_llm_model_config(cls, llm_key: str, model_key: str = "default_model") -> Dict[str, Any]:
        """
        根据关键值从配置文件中读取LLM-MODEL的相关参数
        """
        config_manager = ConfigManager()
        config = config_manager.config
        
        if "LLM_GPT" not in config:
            raise Exception("LLM_GPT配置在配置文件中不存在")
            
        llm_dict = config["LLM_GPT"].get(llm_key, None)
        
        if llm_dict is None:
            raise Exception(f"LLM配置 {llm_key} 在配置文件中不存在")
        
        # 获取模型配置
        model_dict = llm_dict.get(model_key, None)
        if model_dict is None:
            raise Exception(f"模型配置 {model_key} 在配置文件中不存在")
        
        # 兼容api_base和base_url
        base_url = llm_dict.get("base_url") or llm_dict.get("api_base")
        if not base_url:
            raise Exception(f"未找到base_url或api_base字段: {llm_key}")
        
        # 构建AutoGen配置（移除不支持的参数）
        llm_model_config_dict = {
            "config_list": [{
                "model": model_dict.get("model_name"),
                "api_key": llm_dict.get("api_key"),
                "base_url": base_url,
                "api_type": llm_dict.get("api_type", "openai"),
                "timeout": llm_dict.get("timeout", 120)
            }],
            "temperature": model_dict.get("temperature", 0.01),
            "max_tokens": model_dict.get("max_tokens", 4096)
        }
        
        return llm_model_config_dict
    
    @classmethod
    def create_client(cls, llm_key: str, model_key: str = "default_model") -> Dict[str, Any]:
        """
        根据关键值从配置文件中读取LLM-MODEL的相关参数来创建模型客户端实例
        """
        llm_model_dict = cls.get_llm_model_config(llm_key, model_key)
        
        # 根据API类型确定客户端类型
        api_type = llm_model_dict["config_list"][0].get("api_type", "openai")
        client_type = cls._client_types.get(api_type, "openai")
        
        if client_type not in cls._client_types:
            raise ValueError(f"不支持的模型客户端类型: {client_type}")
        
        # 获取模型名称
        llm_model_key = f"{llm_key}_{model_key}"
        
        # 缓存实例
        cls._instances[llm_model_key] = llm_model_dict
        
        return llm_model_dict
    
    @classmethod
    def get_client_by_name(cls, llm_key: str, model_key: str = "default_model") -> Dict[str, Any]:
        """
        根据模型名称获取模型客户端实例
        Returns:
            模型客户端配置字典
        """
        llm_model_key = f"{llm_key}_{model_key}"
        
        if llm_model_key in cls._instances:
            return cls._instances[llm_model_key]
        
        client_config = cls.create_client(llm_key=llm_key, model_key=model_key)
        return client_config
    
    @classmethod
    def get_available_llms(cls) -> list:
        """获取可用的LLM列表"""
        config_manager = ConfigManager()
        config = config_manager.config
        
        if "LLM_GPT" in config:
            return list(config["LLM_GPT"].keys())
        return []
    
    @classmethod
    def test_connection(cls, llm_key: str, model_key: str = "default_model") -> tuple[bool, str]:
        """
        测试LLM连接
        Returns:
            (是否成功, 消息)
        """
        try:
            # 获取配置
            config = cls.get_client_by_name(llm_key, model_key)
            
            # 创建测试Agent
            test_agent = autogen.AssistantAgent(
                name="测试Agent",
                system_message="你是一个测试助手，请简单回复'测试成功'。",
                llm_config=config
            )
            
            user_proxy = autogen.UserProxyAgent(
                name="用户",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=1,
                llm_config=config,
                code_execution_config={"use_docker": False}
            )
            
            # 测试对话
            user_proxy.initiate_chat(
                test_agent,
                message="你好，请简单回复'测试成功'。"
            )
            
            return True, "API连接测试成功！"
            
        except Exception as e:
            return False, f"API连接测试失败: {str(e)}" 