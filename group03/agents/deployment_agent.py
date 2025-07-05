import os
import webbrowser
from typing import Dict, Any
from utils.file_manager import FileManager

def deploy_project(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    部署节点：创建项目文件结构并运行项目
    """
    try:
        print("🚀 开始项目部署...")
        
        code_files = state["code_files"]
        
        # 创建文件管理器
        file_manager = FileManager("generated_project")
        
        # 创建项目文件结构
        print("  📁 创建项目文件...")
        creation_result = file_manager.create_project_structure(code_files)
        print(f"  {creation_result}")
        
        # 保存报告文件
        if "requirements_report" in state:
            file_manager.save_report("requirements", state["requirements_report"])
            print("  📄 需求分析报告已保存")
        
        if "design_report" in state:
            file_manager.save_report("design", state["design_report"])
            print("  📄 设计报告已保存")
        
        if "test_results" in state:
            file_manager.save_report("test", state["test_results"])
            print("  📄 测试报告已保存")
        
        # 获取主HTML文件路径
        main_html_path = file_manager.get_main_html_file()
        
        if main_html_path:
            # 构建访问URL
            access_url = f"file://{main_html_path}"
            
            print(f"✅ 项目部署成功!")
            print(f"📂 项目目录: {os.path.abspath('generated_project')}")
            print(f"🌐 访问地址: {access_url}")
            
            # 更新状态
            state["deployment_result"] = {
                "status": "success",
                "message": "项目部署成功",
                "project_path": os.path.abspath("generated_project"),
                "access_url": access_url,
                "main_file": main_html_path
            }
            state["current_step"] = "deployment_completed"
            
        else:
            raise Exception("未找到可访问的HTML文件")
        
        return state
        
    except Exception as e:
        error_msg = f"项目部署失败: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"].append(error_msg)
        state["deployment_result"] = {
            "status": "failed",
            "message": error_msg,
            "project_path": "",
            "access_url": "",
            "main_file": ""
        }
        state["current_step"] = "deployment_failed"
        return state

def open_project(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    可选的项目打开节点：在浏览器中打开生成的项目
    """
    try:
        deployment_result = state.get("deployment_result", {})
        
        if deployment_result.get("status") == "success":
            access_url = deployment_result.get("access_url", "")
            if access_url:
                print(f"🌐 正在浏览器中打开项目: {access_url}")
                webbrowser.open(access_url)
                print("✅ 项目已在浏览器中打开")
            else:
                print("❌ 无法获取项目访问地址")
        else:
            print("❌ 项目部署未成功，无法打开")
        
        return state
        
    except Exception as e:
        error_msg = f"打开项目失败: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"].append(error_msg)
        return state
