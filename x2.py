import os
import json
import requests
import re
from typing import Dict, Any, Optional, List


class DocAgent:
    """产品文档自动生成代理"""

    def __init__(self, api_key: Optional[str] = "", api_base: str = "https://api.siliconflow.cn/v1/chat/completions"):
        """初始化代理，设置API认证和基础URL"""
        self.api_key = "sk-kgdfuswbjlbqnaoafzutlflawosyqdckorzrntocym"
        if not self.api_key:
            raise ValueError("需要提供API密钥，可以通过环境变量OPENAI_API_KEY设置或作为参数传入")
        self.api_base = api_base
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def generate_documentation(self, product_info: Dict[str, Any]) -> str:
        """根据产品信息生成文档"""
        prompt = self._build_prompt(product_info)
        doc_content = self._call_llm(prompt)

        # 执行反思审核
        reviewed_content = self._review_and_reflect(doc_content, product_info)
        return reviewed_content

    def _build_prompt(self, product_info: Dict[str, Any]) -> str:
        """构建提示词"""
        return f"""
作为一名专业的技术文档撰写专家，请根据以下产品信息生成一份详细的产品文档：

产品名称: {product_info.get('name', '未命名产品')}
产品简介: {product_info.get('description', '无简介')}
产品类型: {product_info.get('type', '未知类型')}
主要功能: {json.dumps(product_info.get('features', []), ensure_ascii=False)}
技术规格: {json.dumps(product_info.get('specifications', {}), ensure_ascii=False)}
目标用户: {product_info.get('target_users', '未指定')}
使用场景: {product_info.get('use_cases', '未指定')}

请生成一份包含以下章节的Markdown格式文档：
1. 产品概述
2. 功能介绍
3. 技术规格
4. 使用指南
5. 常见问题解答
6. 附录（术语表等）

确保文档内容准确、专业，避免冗余信息，使用适当的标题层级结构。
"""

    def _call_llm(self, prompt: str) -> str:
        """调用LLM API获取响应"""
        data = {
            "model": "Qwen/QwQ-32B",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 4000
        }

        try:
            response = requests.post(self.api_base, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"API调用错误: {e}")
            return f"**文档生成失败**: {str(e)}"

    def _review_and_reflect(self, doc_content: str, product_info: Dict[str, Any]) -> str:
        """审核并反思生成的文档，进行必要的修正"""
        # 构建反思提示词
        reflection_prompt = f"""
请审核以下产品文档，检查是否存在错误、不一致或需要改进的地方：

产品信息参考:
{json.dumps(product_info, ensure_ascii=False, indent=2)}

文档内容:
{doc_content}

请提供一份审核报告，指出：
1. 事实性错误
2. 信息不一致
3. 缺失的关键信息
4. 可以改进的表述
5. 其他问题

然后根据审核报告，生成一份改进后的文档。
"""

        # 调用LLM进行审核和反思
        reflection_response = self._call_llm(reflection_prompt)

        # 提取改进后的文档（假设LLM在响应中包含了改进后的版本）
        # 这里使用简单的正则表达式匹配，实际应用中可能需要更复杂的解析
        match = re.search(r"改进后的文档：(.*)", reflection_response, re.DOTALL)
        if match:
            return match.group(1).strip()

        # 如果无法提取改进后的文档，返回原始文档并附上审核报告
        return f"""
**审核报告**

{reflection_response}

**原始生成文档**

{doc_content}
"""


def save_to_file(content: str, filename: str = "product_documentation_v2.md"):
    """将内容保存到文件"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """主函数示例"""
    # 示例产品信息
    product_info = {
        "name": "智能温度控制器",
        "description": "一款高精度智能温度控制设备，支持远程监控和自动化调节",
        "type": "物联网设备",
        "features": [
            "±0.1°C高精度温度传感",
            "手机APP远程控制",
            "自定义温度曲线",
            "异常温度报警",
            "节能模式"
        ],
        "specifications": {
            "工作温度范围": "-20°C至+80°C",
            "精度": "±0.1°C",
            "电源": "220V AC/5V DC",
            "通信接口": "Wi-Fi, Bluetooth",
            "尺寸": "85mm × 85mm × 35mm",
            "重量": "150g"
        },
        "target_users": "家庭用户、小型企业、实验室",
        "use_cases": "家庭恒温控制、实验室环境监控、小型温室温度管理"
    }

    # 创建代理实例
    agent = DocAgent()

    # 生成文档
    documentation = agent.generate_documentation(product_info)

    # 保存文档
    save_to_file(documentation)
    print("产品文档已生成并保存到 product_documentation_v2.md")


if __name__ == "__main__":
    main()