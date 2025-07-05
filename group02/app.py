import gradio as gr
import os
import zipfile
import tempfile
from datetime import datetime
from workflow import ProductDemoWorkflow
import json
import threading
import time

class ProductDemoApp:
    def __init__(self):
        self.workflow = ProductDemoWorkflow()
        self.generation_history = []
        self.current_conversation = []
        self.conversation_lock = threading.Lock()
        
    def add_conversation_message(self, speaker, message):
        """添加对话消息"""
        with self.conversation_lock:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.current_conversation.append({
                "timestamp": timestamp,
                "speaker": speaker,
                "message": message
            })
    
    def get_conversation_display(self):
        """获取对话显示内容"""
        with self.conversation_lock:
            if not self.current_conversation:
                return "等待Agent开始对话..."
            
            display_text = ""
            for msg in self.current_conversation[-20:]:  # 只显示最近20条消息
                speaker_emoji = {
                    "UserProxy": "🤖",
                    "ProductManager": "📋",
                    "UIDesigner": "🎨",
                    "BackendDeveloper": "⚙️",
                    "FullstackDeveloper": "🔧",
                    "Tester": "🧪",
                    "DevOpsEngineer": "🚀"
                }.get(msg["speaker"], "💬")
                
                display_text += f"**[{msg['timestamp']}] {speaker_emoji} {msg['speaker']}:**\n"
                display_text += f"{msg['message'][:500]}{'...' if len(msg['message']) > 500 else ''}\n\n"
            
            return display_text
    
    def generate_demo_interface(self, user_description, progress=gr.Progress()):
        """Web界面的产品demo生成函数"""
        if not user_description.strip():
            return "请输入您的产品需求描述！", "", "", "", "", "", "请输入产品需求"
        
        # 清空当前对话
        with self.conversation_lock:
            self.current_conversation = []
        
        # 检查API密钥
        api_provider = os.getenv("API_PROVIDER", "openai").lower()
        api_key_found = False
        
        if api_provider == "deepseek":
            api_key_found = bool(os.getenv("DEEPSEEK_API_KEY"))
            if not api_key_found:
                return "请先设置DEEPSEEK_API_KEY环境变量！", "", "", "", "", "", "API密钥未配置"
        elif api_provider == "azure":
            api_key_found = bool(os.getenv("AZURE_API_KEY"))
            if not api_key_found:
                return "请先设置AZURE_API_KEY环境变量！", "", "", "", "", "", "API密钥未配置"
        elif api_provider == "moonshot":
            api_key_found = bool(os.getenv("MOONSHOT_API_KEY"))
            if not api_key_found:
                return "请先设置MOONSHOT_API_KEY环境变量！", "", "", "", "", "", "API密钥未配置"
        elif api_provider == "qwen":
            api_key_found = bool(os.getenv("QWEN_API_KEY"))
            if not api_key_found:
                return "请先设置QWEN_API_KEY环境变量！", "", "", "", "", "", "API密钥未配置"
        else:  # OpenAI
            api_key_found = bool(os.getenv("OPENAI_API_KEY"))
            if not api_key_found:
                return "请先设置OPENAI_API_KEY环境变量！", "", "", "", "", "", "API密钥未配置"
        
        progress(0.1, desc="正在分析产品需求...")
        
        try:
            # 设置回调函数
            def progress_callback(prog, desc):
                progress(prog, desc=desc)
            
            def conversation_callback(speaker, message):
                self.add_conversation_message(speaker, message)
            
            # 生成产品demo
            progress(0.2, desc="多Agent协作规划中...")
            result = self.workflow.generate_product_demo(
                user_description, 
                progress_callback=progress_callback,
                conversation_callback=conversation_callback
            )
            
            if "error" in result:
                return result["error"], "", "", "", "", result["error"], "生成失败"
            
            progress(0.8, desc="整理产品文件...")
            
            # 提取各个组件
            frontend_code = result.get("frontend_code", "")
            backend_code = result.get("backend_code", "")
            test_code = result.get("test_code", "")
            deployment_config = result.get("deployment_config", "")
            documentation = result.get("documentation", "")
            
            progress(0.9, desc="保存项目文件...")
            
            # 保存到历史记录
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.generation_history.append({
                "timestamp": timestamp,
                "description": user_description,
                "frontend": frontend_code,
                "backend": backend_code,
                "tests": test_code,
                "deployment": deployment_config,
                "docs": documentation
            })
            
            progress(1.0, desc="产品Demo生成完成！")
            
            return (
                frontend_code, 
                backend_code, 
                test_code, 
                deployment_config, 
                documentation, 
                f"✅ 产品Demo生成成功！ ({timestamp})",
                self.get_conversation_display()
            )
            
        except Exception as e:
            error_msg = f"❌ 生成失败: {str(e)}"
            return error_msg, "", "", "", "", error_msg, "生成过程中出现错误"
    
    def download_demo_project(self, frontend, backend, tests, deployment, docs):
        """打包下载完整的产品demo项目"""
        if not frontend.strip() and not backend.strip():
            return None
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建项目结构
            frontend_dir = os.path.join(temp_dir, "frontend")
            backend_dir = os.path.join(temp_dir, "backend")
            tests_dir = os.path.join(temp_dir, "tests")
            deployment_dir = os.path.join(temp_dir, "deployment")
            
            os.makedirs(frontend_dir, exist_ok=True)
            os.makedirs(backend_dir, exist_ok=True)
            os.makedirs(tests_dir, exist_ok=True)
            os.makedirs(deployment_dir, exist_ok=True)
            
            # 保存前端文件
            if frontend.strip():
                with open(os.path.join(frontend_dir, "index.html"), "w", encoding="utf-8") as f:
                    f.write(frontend)
            
            # 保存后端文件
            if backend.strip():
                with open(os.path.join(backend_dir, "app.py"), "w", encoding="utf-8") as f:
                    f.write(backend)
                
                # 创建requirements.txt
                with open(os.path.join(backend_dir, "requirements.txt"), "w", encoding="utf-8") as f:
                    f.write("Flask==2.3.3\nFlask-CORS==4.0.0\nrequests==2.31.0\n")
            
            # 保存测试文件
            if tests.strip():
                with open(os.path.join(tests_dir, "test_demo.py"), "w", encoding="utf-8") as f:
                    f.write(tests)
            
            # 保存部署配置
            if deployment.strip():
                with open(os.path.join(deployment_dir, "README.md"), "w", encoding="utf-8") as f:
                    f.write(deployment)
                
                # 创建Dockerfile
                dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
COPY frontend/ ./static/

EXPOSE 5000

CMD ["python", "app.py"]"""
                
                with open(os.path.join(temp_dir, "Dockerfile"), "w", encoding="utf-8") as f:
                    f.write(dockerfile_content)
            
            # 保存项目文档
            readme_content = f"""# 产品Demo项目

{docs}

## 项目结构
```
demo/
├── frontend/           # 前端文件
│   └── index.html
├── backend/            # 后端文件
│   ├── app.py
│   └── requirements.txt
├── tests/              # 测试文件
│   └── test_demo.py
├── deployment/         # 部署配置
│   └── README.md
├── Dockerfile          # Docker配置
└── README.md          # 项目说明
```

## 快速开始

### 本地运行
1. 进入backend目录：`cd backend`
2. 安装依赖：`pip install -r requirements.txt`
3. 启动后端：`python app.py`
4. 在浏览器中打开frontend/index.html

### Docker运行
1. 构建镜像：`docker build -t product-demo .`
2. 运行容器：`docker run -p 5000:5000 product-demo`
3. 访问：http://localhost:5000

## 测试
```bash
cd tests
python test_demo.py
```

## 技术栈
- 前端：HTML/CSS/JavaScript
- 后端：Python Flask
- 测试：Python unittest
- 部署：Docker
"""
            
            with open(os.path.join(temp_dir, "README.md"), "w", encoding="utf-8") as f:
                f.write(readme_content)
            
            # 创建启动脚本
            start_script = """#!/bin/bash
echo "🚀 启动产品Demo..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 请先安装Python3"
    exit 1
fi

# 进入后端目录
cd backend

# 安装依赖
echo "📦 安装依赖包..."
pip install -r requirements.txt

# 启动后端服务
echo "🔧 启动后端服务..."
python app.py &

# 等待服务启动
sleep 3

# 打开浏览器
echo "🌐 打开浏览器..."
if command -v open &> /dev/null; then
    open http://localhost:5000
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5000
else
    echo "请手动打开浏览器访问: http://localhost:5000"
fi

echo "✅ 产品Demo已启动！"
"""
            
            with open(os.path.join(temp_dir, "start.sh"), "w", encoding="utf-8") as f:
                f.write(start_script)
            
            # 设置执行权限
            os.chmod(os.path.join(temp_dir, "start.sh"), 0o755)
            
            # 打包成zip文件
            zip_path = os.path.join(temp_dir, "product_demo.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file != "product_demo.zip":
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)
            
            return zip_path
    
    def get_history_display(self):
        """获取历史记录显示"""
        if not self.generation_history:
            return "暂无生成历史"
        
        history_text = "## 产品Demo生成历史\n\n"
        for i, item in enumerate(reversed(self.generation_history[-10:])):  # 只显示最近10条
            history_text += f"**{i+1}. {item['timestamp']}**\n"
            history_text += f"产品需求: {item['description'][:100]}...\n"
            history_text += f"前端代码: {len(item['frontend'])} 字符\n"
            history_text += f"后端代码: {len(item['backend'])} 字符\n\n"
        
        return history_text
    
    def create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(
            title="AI多Agent产品Demo生成器",
            theme=gr.themes.Soft(),
            css="""
            .main-header {
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin-bottom: 2rem;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }
            .feature-box {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 1.5rem;
                border-radius: 12px;
                margin: 0.5rem 0;
                border-left: 4px solid #667eea;
                transition: transform 0.3s ease;
            }
            .feature-box:hover {
                transform: translateY(-2px);
            }
            .demo-flow {
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
                border: 1px solid #dee2e6;
            }
            """
        ) as interface:
            
            # 标题和介绍
            gr.HTML("""
            <div class="main-header">
                <h1>🚀 AI多Agent产品Demo生成器</h1>
                <p>基于AutoGen框架的智能产品开发系统</p>
                <p>产品经理 + UI设计师 + 后端开发 + 全栈整合 + 测试工程师 + 部署工程师</p>
                <p><strong>一句话描述 → 完整可运行的产品Demo</strong></p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("## 📝 描述您的产品需求")
                    
                    # 输入区域
                    user_input = gr.Textbox(
                        label="产品需求描述",
                        placeholder="例如：开发一个在线待办事项管理系统，用户可以添加、编辑、删除任务，支持分类和优先级设置...",
                        lines=5,
                        max_lines=15
                    )
                    
                    # 示例需求
                    gr.Markdown("### 💡 示例需求")
                    with gr.Row():
                        example_btn1 = gr.Button("📋 待办事项管理", size="sm")
                        example_btn2 = gr.Button("💬 在线聊天室", size="sm")
                        example_btn3 = gr.Button("📊 数据可视化", size="sm")
                        example_btn4 = gr.Button("🛒 电商平台", size="sm")
                    
                    generate_btn = gr.Button("🚀 生成产品Demo", variant="primary", size="lg")
                    
                    # 状态显示
                    status_display = gr.Textbox(label="生成状态", interactive=False)
                
                with gr.Column(scale=1):
                    gr.Markdown("## 🔧 系统特性")
                    gr.HTML("""
                    <div class="feature-box">
                        <h4>🧠 智能产品规划</h4>
                        <p>产品经理Agent深度分析需求，制定完整的产品规格</p>
                    </div>
                    <div class="feature-box">
                        <h4>🎨 专业UI设计</h4>
                        <p>UI设计师Agent创建美观现代的用户界面</p>
                    </div>
                    <div class="feature-box">
                        <h4>⚙️ 后端开发</h4>
                        <p>后端开发Agent构建完整的API和业务逻辑</p>
                    </div>
                    <div class="feature-box">
                        <h4>🔧 全栈整合</h4>
                        <p>全栈Agent整合前后端，确保完整功能</p>
                    </div>
                    <div class="feature-box">
                        <h4>🧪 自动化测试</h4>
                        <p>测试Agent生成完整的测试用例和验证</p>
                    </div>
                    <div class="feature-box">
                        <h4>🚀 一键部署</h4>
                        <p>部署Agent提供Docker和部署解决方案</p>
                    </div>
                    """)
                    
                    gr.HTML("""
                    <div class="demo-flow">
                        <h4>🔄 开发流程</h4>
                        <p>需求分析 → UI设计 → 后端开发 → 全栈整合 → 测试验证 → 部署上线</p>
                    </div>
                    """)
            
            # 输出区域
            gr.Markdown("## 📤 生成的产品Demo")
            
            with gr.Tabs():
                with gr.TabItem("💬 Agent对话"):
                    conversation_display = gr.Markdown(
                        label="Agent协作对话",
                        value="等待Agent开始对话...",
                        height=400
                    )
                    
                    # 自动刷新对话的按钮
                    refresh_conversation_btn = gr.Button("🔄 刷新对话", size="sm")
                
                with gr.TabItem("🎨 前端界面"):
                    frontend_code = gr.Code(
                        label="前端代码 (HTML/CSS/JavaScript)",
                        language="html",
                        lines=20,
                        interactive=False
                    )
                
                with gr.TabItem("⚙️ 后端服务"):
                    backend_code = gr.Code(
                        label="后端代码 (Python Flask)",
                        language="python",
                        lines=20,
                        interactive=False
                    )
                
                with gr.TabItem("🧪 测试代码"):
                    test_code = gr.Code(
                        label="测试代码",
                        language="python",
                        lines=15,
                        interactive=False
                    )
                
                with gr.TabItem("🚀 部署配置"):
                    deployment_config = gr.Code(
                        label="部署配置和说明",
                        language="markdown",
                        lines=15,
                        interactive=False
                    )
                
                with gr.TabItem("📚 项目文档"):
                    documentation = gr.Markdown(label="项目文档")
                
                with gr.TabItem("📋 历史记录"):
                    history_display = gr.Markdown(label="生成历史")
            
            # 下载按钮
            with gr.Row():
                download_btn = gr.Button("📦 下载完整产品Demo", variant="secondary", size="lg")
                download_file = gr.File(label="产品Demo项目文件", visible=False)
            
            # 事件绑定
            generate_btn.click(
                fn=self.generate_demo_interface,
                inputs=[user_input],
                outputs=[frontend_code, backend_code, test_code, deployment_config, documentation, status_display, conversation_display]
            )
            
            # 示例按钮事件
            example_btn1.click(
                lambda: "开发一个在线待办事项管理系统，用户可以添加、编辑、删除任务，支持分类和优先级设置，有美观的界面和实时更新功能",
                outputs=[user_input]
            )
            
            example_btn2.click(
                lambda: "创建一个实时在线聊天室应用，支持多用户聊天、消息历史记录、用户状态显示，具有现代化的聊天界面",
                outputs=[user_input]
            )
            
            example_btn3.click(
                lambda: "构建一个数据可视化仪表板，可以上传CSV文件，自动生成各种图表（柱状图、饼图、折线图），支持数据筛选和导出",
                outputs=[user_input]
            )
            
            example_btn4.click(
                lambda: "开发一个简单的电商平台，包含商品展示、购物车、用户注册登录、订单管理等基本功能，界面美观易用",
                outputs=[user_input]
            )
            
            # 对话刷新事件
            refresh_conversation_btn.click(
                fn=self.get_conversation_display,
                outputs=[conversation_display]
            )
            
            # 下载事件
            download_btn.click(
                fn=self.download_demo_project,
                inputs=[frontend_code, backend_code, test_code, deployment_config, documentation],
                outputs=[download_file]
            )
            
            # 定期更新历史记录
            interface.load(
                fn=self.get_history_display,
                outputs=[history_display]
            )
        
        return interface

def main():
    """启动应用"""
    print("🚀 启动AI多Agent产品Demo生成器...")
    
    # 导入配置并显示API信息
    from config import print_api_info
    print_api_info()
    
    # 检查API密钥
    api_provider = os.getenv("API_PROVIDER", "openai").lower()
    
    api_key_found = False
    if api_provider == "deepseek":
        api_key_found = bool(os.getenv("DEEPSEEK_API_KEY"))
        if not api_key_found:
            print("⚠️ 请设置DEEPSEEK_API_KEY环境变量")
            print("💡 可以复制.env.example为.env文件并填入您的DeepSeek API密钥")
    elif api_provider == "azure":
        api_key_found = bool(os.getenv("AZURE_API_KEY"))
        if not api_key_found:
            print("⚠️ 请设置AZURE_API_KEY环境变量")
            print("💡 可以复制.env.example为.env文件并填入您的Azure API密钥")
    elif api_provider == "moonshot":
        api_key_found = bool(os.getenv("MOONSHOT_API_KEY"))
        if not api_key_found:
            print("⚠️ 请设置MOONSHOT_API_KEY环境变量")
            print("💡 可以复制.env.example为.env文件并填入您的Moonshot API密钥")
    elif api_provider == "qwen":
        api_key_found = bool(os.getenv("QWEN_API_KEY"))
        if not api_key_found:
            print("⚠️ 请设置QWEN_API_KEY环境变量")
            print("💡 可以复制.env.example为.env文件并填入您的通义千问API密钥")
    else:  # OpenAI
        api_key_found = bool(os.getenv("OPENAI_API_KEY"))
        if not api_key_found:
            print("⚠️ 请设置OPENAI_API_KEY环境变量")
            print("💡 可以复制.env.example为.env文件并填入您的OpenAI API密钥")
    
    if api_key_found:
        print(f"✅ {api_provider.upper()} API密钥已配置")
    else:
        print("❌ 未找到有效的API密钥，请先配置后再启动")
        return
    
    app = ProductDemoApp()
    interface = app.create_interface()
    
    # 启动界面
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True,
        inbrowser=True
    )

if __name__ == "__main__":
    main() 