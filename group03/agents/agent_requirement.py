from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

def process_requirements(state: Dict[str, Any]) -> Dict[str, Any]:
    raw_input = state["requirements"]
    config = state.get("config", {})
    """将原始需求转换为结构化需求文档"""
    prompt = ChatPromptTemplate.from_template(
        "作为产品经理，请将以下用户需求转化为详细的需求文档(Markdown格式):\n\n{input}"
    )
    
    try:
        # Create configured LLM
        llm = ChatOpenAI(
            api_key=config.get("api_key"),
            base_url=config.get("base_url"),
            model="Pro/deepseek-ai/DeepSeek-V3"
        )
        
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"input": raw_input})
        requirements_md = str(result) if not isinstance(result, str) else result
        
        return {
            "requirements": requirements_md,
            "status": "success",
            "message": "需求分析完成"
        }
    except Exception as e:
        return {
            "requirements": f"需求分析失败: {str(e)}",
            "status": "fail",
            "message": str(e)
        }
