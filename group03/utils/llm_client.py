import requests
import json
from typing import Dict, Any, Optional

class LLMClient:
    """Client for interacting with the LLM API"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, messages: list, model: str = "Pro/deepseek-ai/DeepSeek-V3", temperature: float = 0.7) -> str:
        """Send a chat completion request to the API"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 4000
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=600
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"LLM API call failed: {str(e)}")
    
    def generate_requirements_analysis(self, user_input: str) -> str:
        """Generate requirements analysis from user input"""
        messages = [
            {
                "role": "system",
                "content": """你是一个专业的产品需求分析师。请分析用户输入的需求，输出详细的需求分析报告。

报告应包含：
1. 项目概述
2. 核心功能点列表
3. 用户角色和权限
4. 技术要求
5. 非功能性需求（性能、安全等）

请用中文输出，格式清晰，内容详细。"""
            },
            {
                "role": "user",
                "content": f"请分析以下需求：{user_input}"
            }
        ]
        return self.chat_completion(messages)
    
    def generate_design_report(self, requirements: str) -> str:
        """Generate design report from requirements"""
        messages = [
            {
                "role": "system",
                "content": """你是一个专业的系统架构师。基于需求分析报告，设计详细的技术方案。

设计报告应包含：
1. 系统架构设计
2. 数据库设计
3. API接口设计
4. 前端页面结构
5. 文件组织结构
6. 技术栈选择

请用中文输出，提供具体的实现方案。"""
            },
            {
                "role": "user",
                "content": f"基于以下需求分析报告，请设计技术方案：\n{requirements}"
            }
        ]
        return self.chat_completion(messages)
    
    def generate_code(self, design_report: str, file_type: str) -> str:
        """Generate code based on design report"""
        messages = [
            {
                "role": "system",
                "content": f"""你是一个专业的全栈开发工程师。基于设计报告，生成{file_type}代码。

要求：
1. 代码要完整可运行
2. 包含必要的注释
3. 遵循最佳实践
4. 代码结构清晰
5. 如果是HTML，要包含完整的页面结构
6. 如果是CSS，要包含响应式设计
7. 如果是JavaScript，要包含必要的交互功能

请只输出代码内容，不要包含其他说明文字。"""
            },
            {
                "role": "user",
                "content": f"基于以下设计报告，生成{file_type}代码：\n{design_report}"
            }
        ]
        return self.chat_completion(messages)
    
    def generate_test_plan(self, code_files: Dict[str, str]) -> str:
        """Generate test plan for the code"""
        code_summary = "\n".join([f"文件: {filename}\n内容概要: {content[:200]}..." 
                                 for filename, content in code_files.items()])
        
        messages = [
            {
                "role": "system",
                "content": """你是一个专业的测试工程师。基于提供的代码文件，制定详细的测试计划。

测试计划应包含：
1. 功能测试用例
2. 界面测试要点
3. 用户交互测试
4. 边界条件测试
5. 错误处理测试

请用中文输出，提供具体的测试步骤。"""
            },
            {
                "role": "user",
                "content": f"基于以下代码文件，制定测试计划：\n{code_summary}"
            }
        ]
        return self.chat_completion(messages)
