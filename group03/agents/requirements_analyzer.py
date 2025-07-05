from typing import Dict, Any
from utils.llm_client import LLMClient

def analyze_requirements(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    需求分析节点：分析用户输入的需求，生成详细的需求分析报告
    """
    try:
        print("🔍 开始需求分析...")
        
        # 获取LLM客户端
        config = state.get("config", {})
        llm_client = LLMClient(config["api_key"], config["base_url"])
        
        # 生成需求分析报告
        user_input = state["user_input"]
        requirements_report = llm_client.generate_requirements_analysis(user_input)
        
        print("✅ 需求分析完成")
        print(f"需求分析报告预览：\n{requirements_report[:200]}...")
        
        # 更新状态
        state["requirements_report"] = requirements_report
        state["current_step"] = "requirements_analysis_completed"
        
        return state
        
    except Exception as e:
        error_msg = f"需求分析失败: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"].append(error_msg)
        state["current_step"] = "requirements_analysis_failed"
        return state
