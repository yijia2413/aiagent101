from typing import Dict, Any
from utils.llm_client import LLMClient

def create_design(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    设计节点：基于需求分析报告，生成详细的技术设计方案
    """
    try:
        print("🎨 开始系统设计...")
        
        # 获取LLM客户端
        config = state.get("config", {})
        llm_client = LLMClient(config["api_key"], config["base_url"])
        
        # 生成设计报告
        requirements_report = state["requirements_report"]
        design_report = llm_client.generate_design_report(requirements_report)
        
        print("✅ 系统设计完成")
        print(f"设计报告预览：\n{design_report[:200]}...")
        
        # 更新状态
        state["design_report"] = design_report
        state["current_step"] = "design_completed"
        
        return state
        
    except Exception as e:
        error_msg = f"系统设计失败: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"].append(error_msg)
        state["current_step"] = "design_failed"
        return state
