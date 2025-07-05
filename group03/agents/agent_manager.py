from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from .agent_requirement import process_requirements
from .agent_design import create_design_document
from .agent_development import generate_code
from .agent_testing import create_test_plan
from .agent_deployment import deploy_project

class ProjectState(TypedDict):
    config: Dict[str, str]  # API配置
    requirements: str
    design: str
    code: Dict[str, str]  # 代码内容
    code_paths: Dict[str, str]  # 代码路径
    test_report: Dict[str, Any]
    deployment_result: Dict[str, Any]

def create_workflow():
    # 初始化工作流
    workflow = StateGraph(ProjectState)
    
    # 添加节点
    workflow.add_node("requirement", process_requirements)
    workflow.add_node("design", lambda state: create_design_document(state["requirements"]))
    workflow.add_node("development", lambda state: generate_code(state["design"]))
    workflow.add_node("testing", lambda state: {
        **state,  # 保留所有现有状态
        "test_report": create_test_plan(state["design"], state)
    })
    workflow.add_node("deployment", lambda state: deploy_project(state["test_report"], state["code"]))
    
    # 定义边
    workflow.add_edge("requirement", "design")
    workflow.add_edge("design", "development")
    workflow.add_edge("development", "testing")
    workflow.add_conditional_edges(
        "testing",
        lambda state: "deployment" if state["test_report"]["status"] == "pass" else "development",
    )
    workflow.add_edge("deployment", END)
    
    # 设置入口点
    workflow.set_entry_point("requirement")
    
    return workflow.compile()

def run_workflow(user_input: str, config: Dict[str, str]) -> ProjectState:
    workflow = create_workflow()
    initial_state = {
        "requirements": user_input,
        "config": config
    }
    return workflow.invoke(initial_state)
