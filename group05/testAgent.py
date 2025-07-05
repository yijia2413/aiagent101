import autogen
import os

# 设置 SiliconFlow 的 API_KEY 和 BASE_URL
API_KEY = "sk-kwuppasyxonyhpzocxuaiqfcfsfwngcyufckuhznfwttzmco"  # 替换为你的 SiliconFlow API Key
BASE_URL = "https://api.siliconflow.cn/v1 "

# 使用 openai 兼容接口配置 LLM
config_list = [
    {
        "model": "Qwen/Qwen3-8B",  # 可换成 glm-4 等模型
        "api_key": API_KEY,
        "base_url": BASE_URL
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.3
}

# 自动保存代码到 C:\test 的函数
def save_code_to_file(content, filename="malware_detector.py"):
    output_dir = r"C:\test"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_path = os.path.join(output_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[INFO] 已将代码保存至：{file_path}")

# 用户代理（负责执行代码、保存文件）
user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",  # 改为 NEVER 避免卡住
    max_consecutive_auto_reply=0,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": r"C:\test",  # 明确指定工作目录为 C:\test
        "use_docker": False,
        "execute_code": False   # 禁止自动执行代码
    },
)

# 回调函数：当开发者发送消息时，自动提取代码并保存
def reply_save_code(recipient, messages, sender, config):
    for msg in messages:
        content = msg.get("content", "")
        if content and ("```python" in content or ".py" in content):  # 判断是否是代码
            start = content.find("```python") + len("```python\n")
            end = content.find("```", start)
            code_content = content[start:end].strip()
            if code_content:
                save_code_to_file(code_content)
    return False, None  # 返回 (None, None) 表示继续正常流程

# 注册回调函数到 UserProxy，监听 DeveloperAgent 的回复
user_proxy.register_reply(autogen.AssistantAgent, reply_save_code)

# 项目经理
project_manager = autogen.AssistantAgent(
    name="ProjectManager",
    llm_config=llm_config,
    system_message="""
        你是项目负责人，负责统筹整个开发流程。
        你需要协调各角色完成需求分析、设计、开发、测试和部署。
    """
)

# 需求分析师
requirements_agent = autogen.AssistantAgent(
    name="RequirementsAgent",
    llm_config=llm_config,
    system_message="""
        你是需求分析师，负责明确用户需求和技术约束。
        当前任务：设计 Windows 启动项恶意检测工具的需求文档。
    """
)

# 设计师
design_agent = autogen.AssistantAgent(
    name="DesignAgent",
    llm_config=llm_config,
    system_message="""
        你是架构设计师，负责输出技术设计方案。
        包括数据结构、模块划分、调用逻辑等。这个项目只使用Python进行开发。
    """
)

# 开发者
developer_agent = autogen.AssistantAgent(
    name="DeveloperAgent",
    llm_config=llm_config,
    system_message="""
        你是核心开发者，负责根据设计文档编写代码。
        输出可运行的 Python 脚本，并说明使用方法。
		请给用户展示你的代码。
    """
)

# 测试工程师
qa_engineer_agent = autogen.AssistantAgent(
    name="QAEngineer",
    llm_config=llm_config,
    system_message="""
        你是测试工程师，负责制定测试用例并验证功能是否符合预期。
        可提出改进建议。
    """
)

# 启动对话
chat_result = user_proxy.initiate_chat(
    project_manager,
    message="""
        我们要开发一个 Windows 启动项恶意检测工具。
        目标是识别潜在恶意启动项，并提示用户进行处理。
        
        请按以下流程推进：
        1. 需求分析
        2. 技术设计
        3. 编码实现
        4. 测试验证
        5. 最终交付物，最终交付物都保存在 C:\\test 文件夹下。
        
        每个阶段完成后请通知我。
    """
)

# 进入持续交互模式
print("\n进入交互模式，请输入指令继续对话（输入 'exit' 退出）")
try:
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit"]:
            print("结束对话。")
            break
        user_proxy.send(user_input, project_manager)
except KeyboardInterrupt:
    print("\n用户中断，程序退出。")