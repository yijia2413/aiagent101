import streamlit as st
import os
import json
import subprocess
import threading
import time
import webbrowser
import sys
from datetime import datetime
from typing import List, Dict, Any

# 设置环境变量，禁用Docker
os.environ["AUTOGEN_USE_DOCKER"] = "False"

from llm_client_factory import LLMClientFactory
from agents.team_agents import GameDevelopmentTeam
from game_generator import HTML5GameGenerator

def get_latest_game_html():
    """获取generated_games目录下最新的index.html路径"""
    games_dir = "generated_games"
    if not os.path.exists(games_dir):
        return None, None
    subdirs = [os.path.join(games_dir, d) for d in os.listdir(games_dir) if os.path.isdir(os.path.join(games_dir, d))]
    if not subdirs:
        return None, None
    # 按修改时间排序，取最新
    subdirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    for subdir in subdirs:
        html_path = os.path.join(subdir, "index.html")
        if os.path.exists(html_path):
            return html_path, os.path.basename(subdir)
    return None, None

def start_local_server(game_dir, port=8080):
    """启动本地服务器"""
    try:
        # 检查端口是否被占用
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            return False, f"端口 {port} 已被占用，请选择其他端口"
        
        # 启动服务器
        process = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(port)],
            cwd=game_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待服务器启动
        time.sleep(2)
        
        if process.poll() is None:
            return True, f"服务器已启动在端口 {port}"
        else:
            return False, "服务器启动失败"
            
    except Exception as e:
        return False, f"启动服务器时出错: {str(e)}"

class StreamlitGameDevApp:
    def __init__(self):
        """初始化Streamlit应用"""
        self.setup_page()
        
    def setup_page(self):
        """设置页面配置"""
        st.set_page_config(
            page_title="HTML5游戏开发团队 - AutoGen多Agent系统",
            page_icon="🎮",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
    def run(self):
        """运行应用"""
        # 多页面Tab
        tabs = st.tabs(["团队开发", "🎮 游戏试玩"])
        with tabs[0]:
            self.page_team_development()
        with tabs[1]:
            self.page_game_play()

    def page_team_development(self):
        # 页面标题
        st.title("🎮 HTML5游戏开发团队 - AutoGen多Agent系统")
        st.markdown("---")
        self.setup_sidebar()
        self.setup_main_interface()

    def page_game_play(self):
        st.title("🎮 游戏试玩 | HTML5小游戏")
        st.markdown("---")
        
        html_path, game_name = get_latest_game_html()
        
        if html_path:
            game_dir = os.path.dirname(html_path)
            
            # 显示游戏信息
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.success(f"🎯 当前游戏：{game_name}")
                st.info(f"📁 游戏目录：{game_dir}")
                
            with col2:
                # 服务器控制
                st.subheader("🚀 服务器控制")
                
                # 端口选择
                port = st.number_input("端口号", min_value=8000, max_value=9000, value=8080, step=1)
                
                # 启动服务器按钮
                if st.button("🌐 启动本地服务器", type="primary"):
                    success, message = start_local_server(game_dir, port)
                    if success:
                        st.success(message)
                        server_url = f"http://localhost:{port}"
                        st.markdown(f"**游戏地址：** [{server_url}]({server_url})")
                        
                        # 自动打开浏览器
                        if st.button("🌍 在浏览器中打开"):
                            webbrowser.open(server_url)
                    else:
                        st.error(message)
                
                # 显示游戏文件
                st.subheader("📄 游戏文件")
                files = ["index.html", "style.css", "game.js"]
                for file in files:
                    file_path = os.path.join(game_dir, file)
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with st.expander(f"📄 {file}"):
                            st.code(content, language=file.split('.')[-1])
                            st.download_button(
                                label=f"下载 {file}",
                                data=content,
                                file_name=file,
                                mime="text/plain"
                            )
            
            # 游戏预览
            st.subheader("🎮 游戏预览")
            st.info("💡 提示：在Streamlit中预览可能功能受限，建议使用本地服务器获得最佳体验")
            
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # 调整iframe高度
            height = st.slider("游戏窗口高度", min_value=400, max_value=800, value=600, step=50)
            st.components.v1.html(html_content, height=height, scrolling=True)
            
        else:
            st.warning("⚠️ 暂无可试玩的HTML5小游戏")
            st.info("请先在'团队开发'页面生成游戏！")
            
            # 显示生成目录结构
            games_dir = "generated_games"
            if os.path.exists(games_dir):
                st.subheader("📁 生成目录结构")
                for root, dirs, files in os.walk(games_dir):
                    level = root.replace(games_dir, '').count(os.sep)
                    indent = ' ' * 2 * level
                    st.text(f"{indent}📂 {os.path.basename(root)}/")
                    subindent = ' ' * 2 * (level + 1)
                    for file in files:
                        st.text(f"{subindent}📄 {file}")

    def setup_sidebar(self):
        """设置侧边栏"""
        with st.sidebar:
            st.header("⚙️ 系统配置")
            
            # LLM选择
            available_llms = LLMClientFactory.get_available_llms()
            selected_llm = st.selectbox(
                "选择LLM模型",
                available_llms,
                index=0 if available_llms else None
            )
            
            if st.button("🔄 重新加载配置"):
                LLMClientFactory.clear_cache()
                st.rerun()
                
            # 添加测试按钮
            if st.button("🧪 测试API连接"):
                self.test_api_connection(selected_llm)
                
            st.markdown("---")
            
            # 团队信息
            st.header("👥 开发团队")
            st.markdown("""
            **团队成员：**
            - 🎯 产品经理：需求分析、产品设计
            - 📋 项目经理：项目规划、进度管理
            - 💻 开发工程师：技术实现、代码开发
            - 🧪 测试工程师：质量保证、测试验证
            """)
            
            st.markdown("---")
            
            # 使用说明
            st.header("📖 使用说明")
            st.markdown("""
            1. 在下方输入框中描述您的游戏需求
            2. 点击"开始开发"按钮
            3. 观察团队成员的协作过程
            4. 查看生成的HTML5游戏
            """)
            
    def test_api_connection(self, llm_key: str):
        """测试API连接"""
        try:
            with st.spinner("测试API连接中..."):
                success, message = LLMClientFactory.test_connection(llm_key)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
                    st.error("请检查配置文件中的API密钥和设置")
                    
        except Exception as e:
            st.error(f"❌ API连接测试失败: {str(e)}")
            st.error("请检查配置文件中的API密钥和设置")
            
    def setup_main_interface(self):
        """设置主界面"""
        
        # 创建两列布局
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("📝 市场需求输入")
            
            # 需求输入
            market_requirement = st.text_area(
                "请描述您的游戏需求（一句话或详细描述）：",
                height=150,
                placeholder="例如：开发一个简单的贪吃蛇游戏，支持键盘控制，有分数统计功能..."
            )
            
            # 游戏名称
            game_name = st.text_input(
                "游戏名称：",
                value="我的HTML5游戏",
                placeholder="请输入游戏名称"
            )
            
            # 开始开发按钮
            if st.button("🚀 开始开发", type="primary", use_container_width=True):
                if market_requirement.strip():
                    self.start_development_process(market_requirement, game_name)
                else:
                    st.error("请输入游戏需求！")
                    
        with col2:
            st.header("📊 开发进度")
            
            # 显示开发状态
            if "development_status" not in st.session_state:
                st.info("等待开始开发...")
            else:
                status = st.session_state.development_status
                st.success(f"开发状态：{status}")
                
            # 显示生成的游戏文件
            if "generated_files" in st.session_state:
                st.subheader("🎮 生成的游戏文件")
                files = st.session_state.generated_files
                
                for file_type, file_path in files.items():
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        with st.expander(f"📄 {file_type.upper()} 文件"):
                            st.code(content, language=file_type)
                            
                            # 下载按钮
                            st.download_button(
                                label=f"下载 {file_type.upper()} 文件",
                                data=content,
                                file_name=f"{game_name}.{file_type}",
                                mime="text/plain"
                            )
                            
                # 游戏预览
                if "html" in files and os.path.exists(files["html"]):
                    st.subheader("🎮 游戏预览")
                    with open(files["html"], 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    st.components.v1.html(html_content, height=600, scrolling=True)
        
        # 团队对话历史
        st.markdown("---")
        st.header("💬 团队协作对话")
        
        # 滚动窗口显示团队对话
        st.markdown("""
        <style>
        .chat-scroll-window {
            height: 500px;
            overflow-y: auto;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            background-color: #f8f9fa;
            margin: 10px 0;
        }
        .chat-message {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            animation: fadeIn 0.5s ease-in;
        }
        .chat-message.user {
            background-color: #e3f2fd;
            border-left-color: #2196f3;
        }
        .chat-message.assistant {
            background-color: #f3e5f5;
            border-left-color: #9c27b0;
        }
        .chat-message.system {
            background-color: #fff3e0;
            border-left-color: #ff9800;
        }
        .chat-message.error {
            background-color: #ffebee;
            border-left-color: #f44336;
        }
        .message-header {
            font-weight: bold;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #333;
        }
        .message-content {
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.5;
            color: #555;
        }
        .stage-badge {
            background-color: #007bff;
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            margin-right: 10px;
            display: inline-block;
        }
        .empty-chat {
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 50px 20px;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .typing-indicator {
            display: inline-block;
            padding: 8px 12px;
            background-color: #f0f0f0;
            border-radius: 15px;
            font-style: italic;
            color: #666;
        }
        .typing-dots {
            display: inline-block;
            animation: typing 1.4s infinite;
        }
        @keyframes typing {
            0%, 20% { content: "."; }
            40% { content: ".."; }
            60%, 100% { content: "..."; }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 创建可更新的滚动窗口容器
        chat_container = st.empty()
        
        def update_chat_display():
            """更新对话显示"""
            chat_html = '<div class="chat-scroll-window">'
            
            if "chat_history" in st.session_state and st.session_state.chat_history:
                messages = st.session_state.chat_history
                for message in messages:
                    try:
                        # 获取消息信息
                        if isinstance(message, dict):
                            role = message.get("name", "未知")
                            content = message.get("content", "")
                            timestamp = message.get("timestamp", datetime.now().strftime("%H:%M:%S"))
                            stage = message.get("stage", "")
                        else:
                            role = "系统"
                            content = str(message)
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            stage = ""
                        
                        # 确定消息类型和样式
                        if role == "市场端":
                            message_class = "user"
                            avatar = "👤"
                        elif role == "产品经理":
                            message_class = "assistant"
                            avatar = "🎯"
                        elif role == "项目经理":
                            message_class = "assistant"
                            avatar = "📋"
                        elif role == "开发工程师":
                            message_class = "assistant"
                            avatar = "💻"
                        elif role == "测试工程师":
                            message_class = "assistant"
                            avatar = "🧪"
                        elif role == "系统":
                            message_class = "system"
                            avatar = "⚠️"
                        else:
                            message_class = "assistant"
                            avatar = "🤖"
                        
                        # 构建消息HTML
                        stage_html = f'<span class="stage-badge">{stage}</span>' if stage else ''
                        
                        chat_html += f'''
                        <div class="chat-message {message_class}">
                            <div class="message-header">
                                <span>{avatar} {role}</span>
                                <span style="font-size: 0.8em; color: #666;">{timestamp}</span>
                            </div>
                            {stage_html}
                            <div class="message-content">{content}</div>
                        </div>
                        '''
                        
                    except Exception as e:
                        # 错误消息
                        chat_html += f'''
                        <div class="chat-message error">
                            <div class="message-header">
                                <span>❌ 系统错误</span>
                                <span style="font-size: 0.8em; color: #666;">{datetime.now().strftime("%H:%M:%S")}</span>
                            </div>
                            <div class="message-content">处理消息时出错: {str(e)}</div>
                        </div>
                        '''
                
                # 如果正在开发中，显示输入指示器
                if "development_status" in st.session_state and "正在" in st.session_state.development_status:
                    chat_html += '''
                    <div class="typing-indicator">
                        <span>🔄 团队正在协作中</span>
                        <span class="typing-dots">...</span>
                    </div>
                    '''
            else:
                # 空状态显示
                chat_html += '''
                <div class="empty-chat">
                    <h3>💬 团队协作对话</h3>
                    <p>团队对话将在这里显示...</p>
                    <p>请点击"开始开发"按钮启动团队协作</p>
                </div>
                '''
            
            chat_html += '</div>'
            
            # 显示滚动窗口
            with chat_container.container():
                st.markdown(chat_html, unsafe_allow_html=True)
                
                # 添加自动滚动JavaScript
                st.markdown("""
                <script>
                // 自动滚动到最新消息
                setTimeout(function() {
                    var container = document.querySelector('.chat-scroll-window');
                    if (container) {
                        container.scrollTop = container.scrollHeight;
                    }
                }, 100);
                </script>
                """, unsafe_allow_html=True)
        
        # 初始显示
        update_chat_display()
        
        # 保存更新函数到session_state，供其他地方调用
        st.session_state.update_chat_display = update_chat_display
        
        # 添加自动刷新功能
        if "auto_refresh_counter" not in st.session_state:
            st.session_state.auto_refresh_counter = 0
        
        # 每5秒自动刷新一次（如果正在开发中）
        if "development_status" in st.session_state and "正在" in st.session_state.development_status:
            st.session_state.auto_refresh_counter += 1
            if st.session_state.auto_refresh_counter % 5 == 0:  # 每5次调用刷新一次
                update_chat_display()
                st.rerun()
            
    def start_development_process(self, market_requirement: str, game_name: str):
        """启动开发流程 - 支持实时更新"""
        
        # 初始化对话历史
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # 更新状态
        st.session_state.development_status = "正在初始化团队..."
        
        try:
            # 获取选中的LLM
            available_llms = LLMClientFactory.get_available_llms()
            selected_llm = available_llms[0] if available_llms else "default_llm"
            
            # 创建开发团队
            st.session_state.development_status = "创建开发团队..."
            team = GameDevelopmentTeam(selected_llm)
            
            # 启动开发流程
            st.session_state.development_status = "团队开始协作..."
            
            # 使用进度条显示进度
            progress_bar = st.progress(0)
            status_text = st.text("准备开始...")
            
            # 启动团队协作流程
            messages = self._run_development_with_realtime_updates(
                team, market_requirement, progress_bar, status_text
            )
            
            # 保存最终对话历史
            st.session_state.chat_history = messages
            
            # 生成游戏
            st.session_state.development_status = "生成HTML5游戏..."
            status_text.text("正在生成HTML5游戏...")
            progress_bar.progress(90)
            
            game_generator = HTML5GameGenerator()
            game_files = game_generator.generate_game_from_discussion(messages, game_name)
            st.session_state.generated_files = game_files
            
            progress_bar.progress(100)
            status_text.text("开发完成！")
            st.session_state.development_status = "开发完成！"
            st.success("🎉 游戏开发完成！")
            
            # 更新对话显示
            st.rerun()
            
        except Exception as e:
            st.error(f"开发过程中出现错误：{str(e)}")
            st.error("请检查API配置和网络连接")
            st.session_state.development_status = "开发失败"
            
            # 如果已经有部分对话历史，保存它
            if 'team' in locals() and hasattr(team, 'messages'):
                st.session_state.chat_history = team.messages
            
            # 显示详细错误信息
            with st.expander("查看详细错误信息"):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())
    
    def _run_development_with_realtime_updates(self, team, market_requirement, progress_bar, status_text):
        """实时更新版本的开发流程"""
        
        # 初始化消息列表
        messages = []
        
        # 1. 市场端输入需求
        status_text.text("市场端输入需求...")
        progress_bar.progress(10)
        
        market_message = {
            "name": "市场端",
            "content": market_requirement,
            "stage": "需求输入",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        messages.append(market_message)
        st.session_state.chat_history = messages
        # 更新对话显示
        if "update_chat_display" in st.session_state:
            st.session_state.update_chat_display()
        time.sleep(1)  # 短暂延迟以显示更新
        
        # 2. 产品经理分析需求
        status_text.text("产品经理分析需求...")
        progress_bar.progress(25)
        
        pm_reply = team._get_agent_reply(team.product_manager, f"市场端需求：{market_requirement}\n\n请分析需求，提出关键问题和产品设计建议。")
        pm_message = {
            "name": "产品经理",
            "content": pm_reply,
            "stage": "需求分析",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        messages.append(pm_message)
        st.session_state.chat_history = messages
        # 更新对话显示
        if "update_chat_display" in st.session_state:
            st.session_state.update_chat_display()
        time.sleep(1)
        
        # 3. 项目经理分配任务
        status_text.text("项目经理分配任务...")
        progress_bar.progress(40)
        
        proj_reply = team._get_agent_reply(team.project_manager, f"产品经理分析结果：{pm_reply}\n\n请根据分析分配任务，制定项目计划。")
        proj_message = {
            "name": "项目经理",
            "content": proj_reply,
            "stage": "任务分配",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        messages.append(proj_message)
        st.session_state.chat_history = messages
        # 更新对话显示
        if "update_chat_display" in st.session_state:
            st.session_state.update_chat_display()
        time.sleep(1)
        
        # 4. 开发工程师开发
        status_text.text("开发工程师开始开发...")
        progress_bar.progress(60)
        
        dev_reply = team._get_agent_reply(team.developer, f"项目经理任务分配：{proj_reply}\n\n请根据分配进行开发并汇报开发进度。")
        dev_message = {
            "name": "开发工程师",
            "content": dev_reply,
            "stage": "开发进度",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        messages.append(dev_message)
        st.session_state.chat_history = messages
        # 更新对话显示
        if "update_chat_display" in st.session_state:
            st.session_state.update_chat_display()
        time.sleep(1)
        
        # 5. 测试工程师测试
        status_text.text("测试工程师进行测试...")
        progress_bar.progress(80)
        
        test_reply = team._get_agent_reply(team.tester, f"开发工程师开发进度：{dev_reply}\n\n请根据开发结果进行测试并反馈测试情况。")
        test_message = {
            "name": "测试工程师",
            "content": test_reply,
            "stage": "测试反馈",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        messages.append(test_message)
        st.session_state.chat_history = messages
        # 更新对话显示
        if "update_chat_display" in st.session_state:
            st.session_state.update_chat_display()
        
        return messages
            
    def display_chat_history(self, messages: List[Dict]):
        """显示对话历史 - 已废弃，现在直接在页面中实现"""
        pass

def main():
    """主函数"""
    app = StreamlitGameDevApp()
    app.run()

if __name__ == "__main__":
    main() 