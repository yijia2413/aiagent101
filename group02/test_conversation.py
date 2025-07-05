#!/usr/bin/env python3
"""
测试Agent对话功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import ProductDemoApp
import time

def test_conversation_functionality():
    """测试对话功能"""
    print("🧪 测试Agent对话功能...")
    
    # 创建应用实例
    app = ProductDemoApp()
    
    # 模拟添加对话消息
    print("📝 添加测试对话消息...")
    app.add_conversation_message("ProductManager", "我正在分析用户需求：待办事项管理系统")
    app.add_conversation_message("UIDesigner", "我将设计一个现代化的用户界面")
    app.add_conversation_message("BackendDeveloper", "我负责开发后端API和数据库")
    app.add_conversation_message("FullstackDeveloper", "我将整合前后端功能")
    app.add_conversation_message("Tester", "我会生成完整的测试用例")
    app.add_conversation_message("DevOpsEngineer", "我将配置部署环境")
    
    # 获取对话显示
    print("💬 获取对话显示内容...")
    conversation_display = app.get_conversation_display()
    print("\n对话显示内容:")
    print("=" * 50)
    print(conversation_display)
    print("=" * 50)
    
    # 测试对话历史
    print(f"\n📊 当前对话历史数量: {len(app.current_conversation)}")
    
    # 测试线程安全
    print("🔒 测试线程安全...")
    import threading
    
    def add_messages():
        for i in range(5):
            app.add_conversation_message(f"Agent{i}", f"这是第{i+1}条测试消息")
            time.sleep(0.1)
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=add_messages)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"✅ 线程安全测试完成，总消息数: {len(app.current_conversation)}")
    
    # 最终对话显示
    final_display = app.get_conversation_display()
    print("\n最终对话显示:")
    print("=" * 50)
    print(final_display[-500:])  # 只显示最后500字符
    print("=" * 50)
    
    print("🎉 Agent对话功能测试完成！")

if __name__ == "__main__":
    test_conversation_functionality() 