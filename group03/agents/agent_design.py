from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def create_design_document(requirements: str) -> Dict[str, Any]:
    """根据需求文档生成设计文档"""
    prompt = ChatPromptTemplate.from_template(
        "作为系统架构师，请根据以下需求文档设计系统方案(Markdown格式):\n\n"
        "需求文档:\n{requirements}\n\n"
        "设计需包含:\n"
        "1. 系统架构图描述\n"
        "2. 前后端技术选型\n"
        "3. 数据库设计\n"
        "4. API接口规范"
    )
    
    try:
        chain = prompt | StrOutputParser()
        result = chain.invoke({"requirements": requirements})
        design_md = str(result) if not isinstance(result, str) else result
        
        return {
            "design": design_md,
            "status": "success",
            "message": "设计文档生成完成"
        }
    except Exception as e:
        return {
            "design": f"设计文档生成失败: {str(e)}",
            "status": "fail",
            "message": str(e)
        }
