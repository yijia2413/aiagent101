from typing import Dict, Any
import os
import subprocess
import json
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def create_test_plan(design_doc: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """根据设计文档和状态数据创建端到端测试方案"""
    # 创建测试目录结构
    test_dir = "group03/project_code/tests"
    
    # 获取代码内容和路径
    backend_code = state["code"]["backend"]
    backend_path = state["code_paths"]["backend"]
    frontend_code = state["code"]["frontend"]
    frontend_path = state["code_paths"]["frontend"]
    
    # 写入后端代码
    os.makedirs(os.path.dirname(backend_path), exist_ok=True)
    with open(backend_path, "w") as f:
        f.write(backend_code)
    
    # 写入前端代码
    os.makedirs(os.path.dirname(frontend_path), exist_ok=True)
    with open(frontend_path, "w") as f:
        f.write(frontend_code)
    os.makedirs(f"{test_dir}/frontend/cypress/integration", exist_ok=True)
    
    # 生成测试计划文档
    test_plan_prompt = ChatPromptTemplate.from_template(
        "作为QA工程师，请根据以下设计文档创建端到端测试计划:\n\n"
        "设计文档:\n{design}\n\n"
        "要求:\n"
        "1. 包含API测试用例\n"
        "2. 包含前端功能测试用例\n"
        "3. 包含集成测试流程\n"
        "4. 使用Markdown格式输出"
    )
    test_plan_chain = test_plan_prompt | StrOutputParser()
    test_plan_md = test_plan_chain.invoke({"design": design_doc})
    
    with open(f"{test_dir}/TEST_PLAN.md", "w") as f:
        f.write(test_plan_md)

    # 生成API测试脚本
    api_test_prompt = ChatPromptTemplate.from_template(
        "根据以下设计文档创建API测试脚本(Python):\n\n"
        "设计文档:\n{design}\n\n"
        "要求:\n"
        "1. 使用pytest\n"
        "2. 覆盖所有API端点\n"
        "3. 包含断言\n"
        "4. 返回完整可运行的代码"
    )
    api_test_chain = api_test_prompt | StrOutputParser()
    api_test_code = api_test_chain.invoke({"design": design_doc})
    
    with open(f"{test_dir}/test_api.py", "w") as f:
        f.write(api_test_code)

    # 生成前端测试脚本
    frontend_test_prompt = ChatPromptTemplate.from_template(
        "根据以下设计文档创建前端测试脚本(JavaScript):\n\n"
        "设计文档:\n{design}\n\n"
        "要求:\n"
        "1. 使用Cypress\n"
        "2. 覆盖主要用户流程\n"
        "3. 包含断言\n"
        "4. 返回完整可运行的代码"
    )
    frontend_test_chain = frontend_test_prompt | StrOutputParser()
    frontend_test_code = frontend_test_chain.invoke({"design": design_doc})
    
    with open(f"{test_dir}/frontend/cypress/integration/spec.js", "w") as f:
        f.write(frontend_test_code)

    # 安装测试依赖
    install_test_dependencies(test_dir)

    # 执行测试并获取结果
    test_result = execute_tests(test_dir)
    
    return {
        "test_plan": f"{test_dir}/TEST_PLAN.md",
        "api_tests": f"{test_dir}/test_api.py",
        "frontend_tests": f"{test_dir}/frontend/cypress/integration/spec.js",
        "status": test_result["status"],
        "report": test_result
    }

def install_test_dependencies(test_dir: str):
    """安装测试所需的依赖"""
    # 安装Python测试依赖
    with open(f"{test_dir}/requirements-test.txt", "w") as f:
        f.write("pytest\nrequests")
    subprocess.run(["pip", "install", "-r", f"{test_dir}/requirements-test.txt"], check=True)
    
    # 安装前端测试依赖
    with open(f"{test_dir}/frontend/package.json", "w") as f:
        f.write("""{
  "name": "frontend-tests",
  "dependencies": {
    "cypress": "^12.0.0"
  }
}""")
    subprocess.run(["npm", "install"], cwd=f"{test_dir}/frontend", check=True)

def execute_tests(test_dir: str) -> Dict[str, Any]:
    """执行测试并返回动态结果"""
    test_result = {
        "status": "pass",
        "api_tests": {"passed": 0, "failed": 0},
        "frontend_tests": {"passed": 0, "failed": 0},
        "details": []
    }
    
    try:
        # 执行API测试
        api_result = subprocess.run(
            ["pytest", f"{test_dir}/test_api.py", "--json-report"],
            capture_output=True, text=True
        )
        
        # 解析API测试结果
        if api_result.returncode == 0:
            test_result["api_tests"]["passed"] = len(api_result.stdout.split("\n")) - 1
        else:
            test_result["api_tests"]["failed"] = 1
            test_result["status"] = "fail"
            test_result["details"].append("API测试失败")
        
        # 执行前端测试
        frontend_result = subprocess.run(
            ["npx", "cypress", "run"],
            cwd=f"{test_dir}/frontend",
            capture_output=True, text=True
        )
        
        # 解析前端测试结果
        if "All specs passed" in frontend_result.stdout:
            test_result["frontend_tests"]["passed"] = 1
        else:
            test_result["frontend_tests"]["failed"] = 1
            test_result["status"] = "fail"
            test_result["details"].append("前端测试失败")
            
    except subprocess.CalledProcessError as e:
        test_result["status"] = "fail"
        test_result["details"].append(f"测试执行错误: {str(e)}")
    
    return test_result
