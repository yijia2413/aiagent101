import os
import autogen
from autogen import AssistantAgent, UserProxyAgent
import json
import uuid
from datetime import datetime

# 配置API密钥和模型地址
config_list = [
    {
        'model': 'qwen3',
        'api_key': 'sk-kgdfuswbjlbqnaoafzutlflawosyqdckorzrntocymg',
        'api_base': 'https://api.siliconflow.cn/v1',
        'timeout': 120,
        'temperature': 0.1,
    }
]

# 初始化文档模板库
DOC_TEMPLATES = {
    "app": {
        "sections": ["产品概述", "用户画像", "功能模块", "信息架构", "交互流程", "数据指标", "运营方案"],
        "overview": "### 产品概述\n\n**产品名称**：{product_name}\n\n**产品定位**：{product_positioning}\n\n**目标用户**：{target_users}\n\n**核心价值**：{core_value}\n\n**竞品分析**：{competitor_analysis}"
    },
    "web": {
        "sections": ["产品概述", "用户需求", "功能列表", "UI设计", "技术方案", "数据埋点"],
        "overview": "### 产品概述\n\n**产品名称**：{product_name}\n\n**网站类型**：{website_type}\n\n**目标用户**：{target_users}\n\n**核心功能**：{core_features}\n\n**独特卖点**：{unique_selling_points}"
    },
    "hardware": {
        "sections": ["产品概述", "技术规格", "使用场景", "供应链方案", "成本分析", "用户体验设计"],
        "overview": "### 产品概述\n\n**产品名称**：{product_name}\n\n**产品类型**：{product_type}\n\n**目标用户**：{target_users}\n\n**核心功能**：{core_features}\n\n**技术亮点**：{technical_advantages}"
    }
}


class ProductDesignAgent:
    def __init__(self):
        # 初始化主程序
        self.llm_config = {
            "config_list": config_list,
            "timeout": 120,  # 保留timeout参数
        }

        # 初始化代理
        self.designer = AssistantAgent(
            name="designer",
            system_message="你是一位经验丰富的产品设计师，擅长撰写高质量的产品设计文档。根据用户需求，生成详细、专业的产品设计文档。使用专业术语，确保逻辑清晰、内容完整。",
            llm_config=self.llm_config,
        )

        self.reviewer = AssistantAgent(
            name="reviewer",
            system_message="你是一位资深的产品经理，擅长审核产品设计文档。检查文档的完整性、可行性和逻辑性，提供专业的修改建议。",
            llm_config=self.llm_config,
        )

        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            function_map={
                "generate_product_design_doc": self.generate_product_design_doc,
                "refine_design_doc": self.refine_design_doc,
                "export_to_format": self.export_to_format,
            },
        )

        # 文档存储
        self.documents = {}

    def generate_product_design_doc(self, product_info):
        """根据产品信息生成设计文档"""
        product_type = product_info.get("product_type", "app").lower()
        template = DOC_TEMPLATES.get(product_type, DOC_TEMPLATES["app"])

        # 创建文档ID
        doc_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 初始化文档结构
        document = {
            "id": doc_id,
            "product_info": product_info,
            "creation_time": timestamp,
            "sections": {},
            "version": "1.0",
            "history": []
        }

        # 生成概述部分
        overview_section = template["overview"].format(
            product_name=product_info.get("product_name", "未命名产品"),
            product_positioning=product_info.get("product_positioning", "未定义"),
            target_users=product_info.get("target_users", "未定义"),
            core_value=product_info.get("core_value", "未定义"),
            competitor_analysis=product_info.get("competitor_analysis", "未定义"),
            website_type=product_info.get("website_type", "未定义"),
            core_features=product_info.get("core_features", "未定义"),
            unique_selling_points=product_info.get("unique_selling_points", "未定义"),
            product_type=product_info.get("product_type", "未定义"),
            technical_advantages=product_info.get("technical_advantages", "未定义")
        )

        document["sections"]["产品概述"] = overview_section

        # 存储文档
        self.documents[doc_id] = document

        # 为其他部分生成内容
        for section in template["sections"]:
            if section != "产品概述":  # 已经生成
                prompt = f"""
                为产品"{product_info.get("product_name", "未命名产品")}"创建"{section}"部分的设计文档内容。
                产品类型：{product_type}
                目标用户：{product_info.get("target_users", "未定义")}
                核心功能：{product_info.get("core_features", "未定义")}

                请提供详细、专业的内容，使用适当的子标题和项目符号。
                """

                content = self._get_llm_response(prompt)
                document["sections"][section] = content

        return {
            "doc_id": doc_id,
            "status": "文档已生成",
            "document": document
        }

    def refine_design_doc(self, doc_id, refinement_request):
        """根据修改请求优化设计文档"""
        if doc_id not in self.documents:
            return {"status": "错误", "message": "文档ID不存在"}

        document = self.documents[doc_id]

        # 记录修改历史
        old_version = document["version"]
        document["history"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": old_version,
            "request": refinement_request,
            "document_state": json.loads(json.dumps(document))  # 深拷贝
        })

        # 更新版本号
        major, minor = map(int, old_version.split('.'))
        document["version"] = f"{major}.{minor + 1}"

        # 处理修改请求
        for section, changes in refinement_request.items():
            if section in document["sections"]:
                prompt = f"""
                以下是产品"{document["product_info"].get("product_name", "未命名产品")}"的"{section}"部分：

                {document["sections"][section]}

                请根据以下修改请求进行优化：
                {changes}

                返回优化后的完整部分内容。
                """

                new_content = self._get_llm_response(prompt)
                document["sections"][section] = new_content

        return {
            "doc_id": doc_id,
            "status": "文档已更新",
            "new_version": document["version"],
            "document": document
        }

    def export_to_format(self, doc_id, format_type="markdown"):
        """将文档导出为指定格式"""
        if doc_id not in self.documents:
            return {"status": "错误", "message": "文档ID不存在"}

        document = self.documents[doc_id]

        if format_type == "markdown":
            # 生成Markdown格式
            md_content = f"# {document['product_info'].get('product_name', '产品设计文档')}\n\n"
            md_content += f"**版本**：{document['version']}\n\n"
            md_content += f"**创建时间**：{document['creation_time']}\n\n"

            for section, content in document["sections"].items():
                md_content += f"## {section}\n\n"
                md_content += f"{content}\n\n"

            return {
                "doc_id": doc_id,
                "format": format_type,
                "content": md_content
            }
        elif format_type == "json":
            # 生成JSON格式
            return {
                "doc_id": doc_id,
                "format": format_type,
                "content": json.dumps(document, indent=2, ensure_ascii=False)
            }
        else:
            return {"status": "错误", "message": f"不支持的格式: {format_type}"}

    def _get_llm_response(self, prompt):
        """获取LLM回复"""
        message = {"name": "user_proxy", "content": prompt}
        self.designer.receive(message, self.user_proxy)
        return self.designer.last_message()["content"]


# 示例使用
if __name__ == "__main__":
    agent = ProductDesignAgent()

    # 产品信息示例
    product_info = {
        "product_name": "健身伙伴",
        "product_type": "app",
        "product_positioning": "专注于家庭健身的社交化APP",
        "target_users": "18-35岁的健身爱好者，尤其是在家锻炼的人群",
        "core_value": "提供个性化健身计划，连接志同道合的健身伙伴",
        "core_features": "个性化训练计划、社交打卡、健身社区、饮食建议",
        "competitor_analysis": "相比Keep更注重社交互动，相比Fitbit更专注于家庭场景"
    }

    # 生成文档
    result = agent.generate_product_design_doc(product_info)
    doc_id = result["doc_id"]
    print(f"文档已生成，ID: {doc_id}")

    # 查看文档内容
    document = result["document"]
    for section, content in document["sections"].items():
        print(f"\n=== {section} ===")
        print(content[:200] + "...")  # 显示前200个字符

    # 优化文档
    refinement = {
        "功能模块": "增加线下课程预约功能的详细说明",
        "数据指标": "补充用户留存率和日活的计算方式"
    }

    update_result = agent.refine_design_doc(doc_id, refinement)
    print(f"\n文档已更新至版本: {update_result['new_version']}")

    # 导出为Markdown
    export_result = agent.export_to_format(doc_id, "markdown")
    with open(f"健身伙伴_产品设计文档_{document['version']}.md", "w", encoding="utf-8") as f:
        f.write(export_result["content"])
    print(f"文档已导出为Markdown格式")