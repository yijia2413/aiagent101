#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML5游戏开发团队 - AutoGen多Agent系统
主程序入口
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import main

if __name__ == "__main__":
    print("🎮 启动HTML5游戏开发团队系统...")
    print("📝 使用说明：")
    print("1. 确保已安装所有依赖包")
    print("2. 配置config/config.yaml中的API密钥")
    print("3. 运行: streamlit run streamlit_app.py")
    print("\n🚀 正在启动Streamlit应用...")
    
    # 启动Streamlit应用
    main() 