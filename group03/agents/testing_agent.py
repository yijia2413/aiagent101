from typing import Dict, Any
from utils.llm_client import LLMClient
from utils.file_manager import FileManager

def run_tests(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    测试节点：对生成的代码进行测试，确保功能正常
    """
    try:
        print("🧪 开始代码测试...")
        
        # 获取LLM客户端
        config = state.get("config", {})
        llm_client = LLMClient(config["api_key"], config["base_url"])
        
        code_files = state["code_files"]
        
        # 生成测试计划
        print("  📋 生成测试计划...")
        test_plan = llm_client.generate_test_plan(code_files)
        
        # 执行基本的代码检查
        test_results = []
        test_results.append("=== 代码测试报告 ===\n")
        test_results.append(f"测试时间: {state.get('current_step', 'unknown')}\n")
        test_results.append(f"测试文件数量: {len(code_files)}\n\n")
        
        # 检查必要文件是否存在
        required_files = ["index.html"]
        missing_files = []
        for file in required_files:
            if file not in code_files:
                missing_files.append(file)
        
        if missing_files:
            test_results.append(f"❌ 缺少必要文件: {', '.join(missing_files)}\n")
        else:
            test_results.append("✅ 所有必要文件都已生成\n")
        
        # 检查HTML文件结构
        if "index.html" in code_files:
            html_content = code_files["index.html"]
            html_checks = []
            
            if "<!DOCTYPE html>" in html_content or "<html" in html_content:
                html_checks.append("✅ HTML文档结构正确")
            else:
                html_checks.append("❌ HTML文档结构不完整")
            
            if "<head>" in html_content and "</head>" in html_content:
                html_checks.append("✅ HTML头部结构正确")
            else:
                html_checks.append("❌ HTML头部结构缺失")
            
            if "<body>" in html_content and "</body>" in html_content:
                html_checks.append("✅ HTML主体结构正确")
            else:
                html_checks.append("❌ HTML主体结构缺失")
            
            test_results.append("HTML结构检查:\n")
            test_results.extend([f"  {check}\n" for check in html_checks])
        
        # 检查CSS文件
        if "style.css" in code_files:
            css_content = code_files["style.css"]
            if len(css_content.strip()) > 0:
                test_results.append("✅ CSS样式文件已生成且包含内容\n")
            else:
                test_results.append("❌ CSS样式文件为空\n")
        
        # 检查JavaScript文件
        if "script.js" in code_files:
            js_content = code_files["script.js"]
            if len(js_content.strip()) > 0:
                test_results.append("✅ JavaScript脚本文件已生成且包含内容\n")
            else:
                test_results.append("❌ JavaScript脚本文件为空\n")
        
        # 添加测试计划到结果中
        test_results.append("\n=== 详细测试计划 ===\n")
        test_results.append(test_plan)
        
        final_test_results = "".join(test_results)
        
        print("✅ 代码测试完成")
        print("测试结果预览:")
        print(final_test_results[:300] + "...")
        
        # 更新状态
        state["test_results"] = final_test_results
        state["current_step"] = "testing_completed"
        
        return state
        
    except Exception as e:
        error_msg = f"代码测试失败: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"].append(error_msg)
        state["current_step"] = "testing_failed"
        return state
