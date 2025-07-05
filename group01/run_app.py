#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML5游戏开发团队系统启动脚本
"""

import subprocess
import sys
import os

def main():
    """启动Streamlit应用"""
    print("🎮 HTML5游戏开发团队 - AutoGen多Agent系统")
    print("=" * 50)
    
    # 设置环境变量，禁用Docker
    os.environ["AUTOGEN_USE_DOCKER"] = "False"
    print("✅ 已禁用Docker代码执行")
    
    # 检查依赖
    try:
        import streamlit
        import autogen
        import yaml
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return
    
    # 检查配置文件
    if not os.path.exists("config/config.yaml"):
        print("❌ 配置文件不存在: config/config.yaml")
        print("请检查配置文件")
        return
    
    print("🚀 启动Streamlit应用...")
    print("📱 应用将在浏览器中打开")
    print("🔗 地址: http://localhost:8501")
    print("\n按 Ctrl+C 停止应用")
    print("-" * 50)
    
    try:
        # 启动Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py", 
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main() 