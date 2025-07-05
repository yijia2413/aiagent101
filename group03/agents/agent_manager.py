from typing import Dict, Any, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from agents.requirements_analyzer import analyze_requirements
from agents.design_agent import create_design
from agents.coding_agent import generate_code
from agents.testing_agent import run_tests
from agents.deployment_agent import deploy_project

class ProductDevelopmentState(TypedDict):
    """产品开发工作流状态定义"""
    user_input: str
    config: Dict[str, Any]
    requirements_report: str
    design_report: str
    code_files: Dict[str, str]
    test_results: str
    deployment_result: Dict[str, Any]
    current_step: str
    errors: List[str]

def should_continue_to_design(state: ProductDevelopmentState) -> str:
    """判断是否继续到设计阶段"""
    if state["current_step"] == "requirements_analysis_completed":
        return "design"
    else:
        return END

def should_continue_to_coding(state: ProductDevelopmentState) -> str:
    """判断是否继续到编码阶段"""
    if state["current_step"] == "design_completed":
        return "coding"
    else:
        return END

def should_continue_to_testing(state: ProductDevelopmentState) -> str:
    """判断是否继续到测试阶段"""
    if state["current_step"] == "coding_completed":
        return "testing"
    else:
        return END

def should_continue_to_deployment(state: ProductDevelopmentState) -> str:
    """判断是否继续到部署阶段"""
    if state["current_step"] == "testing_completed":
        return "deployment"
    else:
        return END

def create_workflow() -> StateGraph:
    """创建产品开发工作流"""
    
    # 创建状态图
    workflow = StateGraph(ProductDevelopmentState)
    
    # 添加节点
    workflow.add_node("requirements_analysis", analyze_requirements)
    workflow.add_node("design", create_design)
    workflow.add_node("coding", generate_code)
    workflow.add_node("testing", run_tests)
    workflow.add_node("deployment", deploy_project)
    
    # 设置入口点
    workflow.set_entry_point("requirements_analysis")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "requirements_analysis",
        should_continue_to_design,
        {
            "design": "design",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "design",
        should_continue_to_coding,
        {
            "coding": "coding",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "coding",
        should_continue_to_testing,
        {
            "testing": "testing",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "testing",
        should_continue_to_deployment,
        {
            "deployment": "deployment",
            END: END
        }
    )
    
    # 部署完成后结束
    workflow.add_edge("deployment", END)
    
    return workflow

def run_workflow(user_input: str, config: Dict[str, Any]) -> ProductDevelopmentState:
    """运行完整的产品开发工作流"""
    
    print("🚀 启动产品开发 Agent 工作流")
    print(f"📝 用户需求: {user_input}")
    print("=" * 50)
    
    # 初始化状态
    initial_state = ProductDevelopmentState(
        user_input=user_input,
        config=config,
        requirements_report="",
        design_report="",
        code_files={},
        test_results="",
        deployment_result={},
        current_step="started",
        errors=[]
    )
    
    try:
        # 创建并编译工作流
        workflow = create_workflow()
        app = workflow.compile()
        
        # 执行工作流
        final_state = app.invoke(initial_state)
        
        print("=" * 50)
        print("🎉 产品开发工作流执行完成!")
        
        # 输出执行摘要
        if final_state["errors"]:
            print("⚠️  执行过程中出现的错误:")
            for error in final_state["errors"]:
                print(f"  - {error}")
        
        print(f"📊 最终状态: {final_state['current_step']}")
        
        return final_state
        
    except Exception as e:
        error_msg = f"工作流执行失败: {str(e)}"
        print(f"❌ {error_msg}")
        
        # 返回错误状态
        initial_state["errors"].append(error_msg)
        initial_state["current_step"] = "workflow_failed"
        initial_state["deployment_result"] = {
            "status": "failed",
            "message": error_msg,
            "project_path": "",
            "access_url": "",
            "main_file": ""
        }
        
        return initial_state

if __name__ == "__main__":
    # 测试工作流
    test_config = {
        "api_key": "test_key",
        "base_url": "test_url"
    }
    
    result = run_workflow("构建一个简单的待办事项管理系统", test_config)
    print(f"测试结果: {result['current_step']}")
