from typing import Dict, Any
from utils.llm_client import LLMClient

def generate_code(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    编码节点：基于设计报告，生成完整的项目代码文件
    """
    try:
        print("💻 开始代码生成...")
        
        # 获取LLM客户端
        config = state.get("config", {})
        llm_client = LLMClient(config["api_key"], config["base_url"])
        
        design_report = state["design_report"]
        code_files = {}
        
        # 定义需要生成的文件类型
        file_types = [
            ("index.html", "HTML主页面"),
            ("style.css", "CSS样式文件"),
            ("script.js", "JavaScript交互脚本"),
            ("README.md", "项目说明文档")
        ]
        
        # 逐个生成代码文件
        for filename, file_description in file_types:
            print(f"  📝 生成 {filename}...")
            try:
                code_content = llm_client.generate_code(design_report, file_description)
                code_files[filename] = code_content
                print(f"  ✅ {filename} 生成完成")
            except Exception as e:
                print(f"  ❌ {filename} 生成失败: {str(e)}")
                # 继续生成其他文件
                continue
        
        if not code_files:
            raise Exception("没有成功生成任何代码文件")
        
        print(f"✅ 代码生成完成，共生成 {len(code_files)} 个文件")
        
        # 更新状态
        state["code_files"] = code_files
        state["current_step"] = "coding_completed"
        
        return state
        
    except Exception as e:
        error_msg = f"代码生成失败: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"].append(error_msg)
        state["current_step"] = "coding_failed"
        return state
