#!/usr/bin/env python3
"""
测试用户确认功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflow import ProductDemoWorkflow

def test_user_confirmation():
    """测试用户确认功能"""
    print("🧪 测试用户确认功能...")
    
    # 创建工作流实例
    workflow = ProductDemoWorkflow()
    
    # 检查UserProxy配置
    user_proxy = workflow.agents_manager.get_agent("user_proxy")
    
    print(f"📋 UserProxy配置:")
    print(f"   - 名称: {user_proxy.name}")
    print(f"   - 人工输入模式: {user_proxy.human_input_mode}")
    print(f"   - 代码执行配置: {user_proxy.code_execution_config}")
    print(f"   - 工作目录: {user_proxy.code_execution_config.get('work_dir', 'N/A')}")
    print(f"   - 使用Docker: {user_proxy.code_execution_config.get('use_docker', 'N/A')}")
    print(f"   - 超时时间: {user_proxy.code_execution_config.get('timeout', 'N/A')}秒")
    
    # 检查工作目录
    work_dir = user_proxy.code_execution_config.get('work_dir', 'generated_code')
    if os.path.exists(work_dir):
        print(f"✅ 工作目录存在: {work_dir}")
    else:
        print(f"❌ 工作目录不存在: {work_dir}")
        print("   创建工作目录...")
        os.makedirs(work_dir, exist_ok=True)
        print(f"✅ 工作目录已创建: {work_dir}")
    
    # 验证配置是否正确
    if user_proxy.human_input_mode == "ALWAYS":
        print("✅ 用户确认模式已启用")
    else:
        print("❌ 用户确认模式未启用")
        print(f"   当前模式: {user_proxy.human_input_mode}")
    
    if user_proxy.code_execution_config:
        print("✅ 代码执行功能已启用")
    else:
        print("❌ 代码执行功能未启用")
    
    print("\n🎯 测试总结:")
    print("1. 启动应用: ./start_app.sh")
    print("2. 访问Web界面: http://localhost:7860")
    print("3. 输入产品需求并生成Demo")
    print("4. 在终端中监控确认提示")
    print("5. 根据提示输入 y/n 来确认或拒绝命令执行")
    
    print("\n💡 提示:")
    print("- 所有代码执行都会在终端中显示")
    print("- 您可以审查每个命令后再决定是否执行")
    print("- 代码会在 generated_code/ 目录中执行")
    print("- 生成的文件会保存在 generated_demo/ 目录中")

if __name__ == "__main__":
    test_user_confirmation() 