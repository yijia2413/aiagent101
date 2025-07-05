from agents.agent_manager import run_workflow

def main():
    # 示例用户输入
    user_input = "构建一个任务管理系统"
    
    # API配置
    config = {
        "api_key": "sk-iezstwckxfihicztnjdvkghcjxtqtkuqdfbrhzojayxbccdp",  # 替换为你的API密钥
        "base_url": "https://api.siliconflow.cn/v1"  # 替换为你的API基础URL
    }
    
    # 执行完整工作流
    final_state = run_workflow(user_input, config)
    
    # 输出结果
    deployment_result = final_state.get("deployment_result", {})
    if deployment_result.get("status") == "success":
        print(f"部署成功! 访问地址: {deployment_result.get('access_url', '')}")
    else:
        print(f"部署失败: {deployment_result.get('message', '未知错误')}")

if __name__ == "__main__":
    main()
