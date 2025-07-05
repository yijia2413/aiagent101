import os
import json
import requests
from typing import Dict, Any, List, Optional


class DocAgent:
    def __init__(self, api_key: str, api_base: str = "https://api.siliconflow.cn/v1/chat/completions"):
        self.api_key = api_key
        self.api_base = api_base
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def generate_product_doc(self, product_info: Dict[str, Any]) -> str:
        """根据产品信息生成产品文档"""
        prompt = self._construct_prompt(product_info)
        response = self._call_llm(prompt)
        return response

    def _construct_prompt(self, product_info: Dict[str, Any]) -> str:
        """构建提示词"""
        prompt = """你是一位专业的产品文档撰写专家。请根据以下产品信息撰写一份详细的产品文档。
### 产品信息
"""
        for key, value in product_info.items():
            prompt += f"**{key}**: {value}\n"

        prompt += """
### 文档要求
1. 结构清晰，包含产品概述、功能特性、技术规格、使用说明和常见问题解答等部分
2. 使用专业、简洁的语言
3. 确保内容准确、完整
4. 格式规范，层次分明

请生成完整的产品文档："""
        return prompt

    def _call_llm(self, prompt: str) -> str:
        """调用LLM API生成响应"""
        payload = {
            "model": "Qwen/QwQ-32B",
            "messages": [
                {"role": "system", "content": "你是一个专业的产品文档撰写专家。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 2000
        }

        try:
            response = requests.post(self.api_base, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            print(f"API请求错误: {e}")
            return "生成文档时出错，请检查API配置和网络连接。"


def main():
    # 从环境变量获取API密钥
    api_key = "sk-kgdfuswbjlbqnaoafzutlflawosyqdckorzrntoc"

    # 创建文档生成代理
    agent = DocAgent(api_key)

    # 产品信息示例
    product_info = {
        "产品名称": "智能温控水杯",
        "产品定位": "高端智能生活用品",
        "目标用户": "注重生活品质的上班族和商务人士",
        "核心功能": "48小时恒温、手机APP控制、健康饮水提醒、水温实时显示",
        "技术参数": "电池容量2000mAh，充电时间2小时，保温温度范围40-60℃，材质为医用级不锈钢",
        "优势特点": "1. 采用航空级保温材料；2. 支持无线充电；3. 智能算法学习用户饮水习惯",
        "应用场景": "办公室、出差旅行、居家休息",
        "竞品分析": "相比市场同类产品，续航时间延长50%，重量减轻20%，具备APP智能联动功能"
    }

    # 生成产品文档
    print("正在生成产品文档...")
    document = agent.generate_product_doc(product_info)

    # 保存文档
    with open("product_documentation.md", "w", encoding="utf-8") as f:
        f.write(document)

    print("产品文档已生成并保存为 product_documentation.md")


if __name__ == "__main__":
    main()