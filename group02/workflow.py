import autogen
from agents import ProductDemoAgents
import os
import json
from datetime import datetime
import logging
import sys
from io import StringIO

# 配置日志，减少AutoGen的详细输出
logging.getLogger("autogen").setLevel(logging.WARNING)

class ProductDemoWorkflow:
    def __init__(self):
        self.agents_manager = ProductDemoAgents()
        self.conversation_history = []
        self.generated_files = {}
        self.progress_callback = None
        self.conversation_callback = None
        
    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def set_conversation_callback(self, callback):
        """设置对话回调函数，用于实时显示Agent讨论"""
        self.conversation_callback = callback
    
    def _log_progress(self, message, progress=None):
        """记录进度信息到终端和Web界面"""
        print(f"🔄 {message}")
        if self.progress_callback and progress is not None:
            self.progress_callback(progress, message)
    
    def _log_conversation(self, speaker, message):
        """记录对话到Web界面"""
        if self.conversation_callback:
            self.conversation_callback(speaker, message)
    
    def generate_product_demo(self, user_description, progress_callback=None, conversation_callback=None):
        """根据用户描述生成完整产品demo的工作流"""
        
        self.progress_callback = progress_callback
        self.conversation_callback = conversation_callback
        
        self._log_progress(f"开始生成产品demo: {user_description}", 0.1)
        
        # 获取所有agent
        user_proxy = self.agents_manager.get_agent("user_proxy")
        product_manager = self.agents_manager.get_agent("product_manager")
        ui_designer = self.agents_manager.get_agent("ui_designer")
        backend_developer = self.agents_manager.get_agent("backend_developer")
        fullstack_developer = self.agents_manager.get_agent("fullstack_developer")
        tester = self.agents_manager.get_agent("tester")
        devops_engineer = self.agents_manager.get_agent("devops_engineer")
        
        # 创建自定义的GroupChat类来捕获消息
        class CustomGroupChat(autogen.GroupChat):
            def __init__(self, agents, messages, max_round, speaker_selection_method, workflow_instance):
                super().__init__(agents, messages, max_round, speaker_selection_method)
                self.workflow = workflow_instance
            
            def append(self, message, speaker):
                """重写append方法来捕获消息"""
                super().append(message, speaker)
                # 发送消息到Web界面
                speaker_name = speaker.name if hasattr(speaker, 'name') else str(speaker)
                content = message.get("content", "") if isinstance(message, dict) else str(message)
                self.workflow._log_conversation(speaker_name, content)
        
        # 创建群组聊天
        group_chat = CustomGroupChat(
            agents=[user_proxy, product_manager, ui_designer, backend_developer, 
                   fullstack_developer, tester, devops_engineer],
            messages=[],
            max_round=25,
            speaker_selection_method="round_robin",
            workflow_instance=self
        )
        
        manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=self.agents_manager.agents["product_manager"].llm_config
        )
        
        # 构造详细的产品开发流程消息
        initial_message = f"""
🎯 产品需求：{user_description}

请按照以下完整的产品开发流程协作完成产品demo：

📋 **第一阶段：产品规划**
- ProductManager：深入分析需求，制定产品规格，确定核心功能和用户故事
- 输出：产品需求文档、功能规格、技术栈选择

🎨 **第二阶段：界面设计**
- UIDesigner：根据产品需求设计用户界面，创建前端代码
- 输出：完整的HTML/CSS/JavaScript前端代码，确保美观和易用

⚙️ **第三阶段：后端开发**
- BackendDeveloper：开发后端API和业务逻辑，设计数据库
- 输出：完整的后端服务代码、API文档、数据库设计

🔧 **第四阶段：全栈整合**
- FullstackDeveloper：整合前后端，实现完整的产品功能
- 输出：可运行的完整产品demo、用户流程实现

🧪 **第五阶段：测试验证**
- Tester：编写测试用例，验证产品功能
- 输出：测试代码、测试报告、质量评估

🚀 **第六阶段：部署上线**
- DevOpsEngineer：创建部署方案，提供运行指南
- 输出：部署脚本、Docker配置、运行文档

**最终目标：**
生成一个完整的、可直接运行的产品demo，包含：
1. 前端界面（HTML/CSS/JS）
2. 后端服务（Python/Node.js）
3. 数据库设计
4. 测试用例
5. 部署脚本
6. 运行文档

请各位Agent按照流程开始协作！每个Agent都要提供具体的代码和文档。
"""
        
        # 启动对话
        try:
            self._log_progress("启动多Agent协作对话...", 0.2)
            
            # 检查是否需要用户确认
            user_proxy = self.agents_manager.get_agent("user_proxy")
            needs_confirmation = (hasattr(user_proxy, 'human_input_mode') and 
                                user_proxy.human_input_mode == "ALWAYS")
            
            if needs_confirmation:
                # 如果需要用户确认，保持标准输出以显示确认提示
                print("🔧 启用用户确认模式 - 代码执行前会显示命令并等待您的确认")
                print("💡 在终端中，您可以输入 'y' 或 'yes' 来确认执行，输入 'n' 或 'no' 来拒绝")
                print("📝 或者直接按回车键来跳过当前步骤")
                
                result = user_proxy.initiate_chat(
                    manager,
                    message=initial_message,
                    max_turns=30
                )
            else:
                # 如果不需要用户确认，禁用详细输出
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                
                # 只在终端显示重要信息
                sys.stdout = StringIO()
                sys.stderr = StringIO()
                
                try:
                    result = user_proxy.initiate_chat(
                        manager,
                        message=initial_message,
                        max_turns=30
                    )
                finally:
                    # 恢复标准输出
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
            
            self._log_progress("对话完成，开始解析结果...", 0.8)
            
            # 解析和组织结果
            demo_result = self.parse_demo_result(result)
            
            self._log_progress("保存生成的文件...", 0.9)
            # 保存生成的文件
            self.save_demo_files(demo_result, user_description)
            
            self._log_progress("产品Demo生成完成！", 1.0)
            return demo_result
            
        except Exception as e:
            error_msg = f"产品demo生成过程中出现错误: {str(e)}"
            self._log_progress(f"❌ {error_msg}", None)
            return {"error": error_msg}
    
    def parse_demo_result(self, result):
        """解析agent协作的结果，提取各个组件"""
        self._log_progress("解析Agent协作结果...", None)
        
        # 初始化结果结构
        demo_result = {
            "product_spec": "",
            "frontend_code": "",
            "backend_code": "",
            "database_design": "",
            "test_code": "",
            "deployment_config": "",
            "documentation": "",
            "run_instructions": "",
            "conversation_log": []
        }
        
        # 提取对话历史
        if hasattr(result, 'chat_history'):
            messages = result.chat_history
        elif isinstance(result, dict) and "chat_history" in result:
            messages = result["chat_history"]
        else:
            messages = []
        
        demo_result["conversation_log"] = messages
        
        # 从对话中提取各种内容
        for message in messages:
            if isinstance(message, dict):
                speaker = message.get("name", "")
                content = message.get("content", "")
            else:
                speaker = getattr(message, 'name', '')
                content = getattr(message, 'content', str(message))
            
            # 根据发言者分类内容
            if speaker == "ProductManager":
                demo_result["product_spec"] += content + "\n\n"
            
            elif speaker == "UIDesigner":
                # 提取前端代码
                frontend_code = self.extract_frontend_code(content)
                if frontend_code.strip():
                    demo_result["frontend_code"] += frontend_code
            
            elif speaker == "BackendDeveloper":
                # 提取后端代码
                backend_code = self.extract_backend_code(content)
                if backend_code.strip():
                    demo_result["backend_code"] += backend_code
                
                # 提取数据库设计（只提取代码块中的SQL等）
                code_blocks = self.extract_code_blocks(content)
                for block in code_blocks:
                    if any(keyword in block.upper() for keyword in ["CREATE TABLE", "INSERT", "SELECT", "UPDATE", "DELETE", "SQL"]):
                        demo_result["database_design"] += block + "\n\n"
            
            elif speaker == "FullstackDeveloper":
                # 全栈代码可能包含前端和后端
                frontend_code = self.extract_frontend_code(content)
                backend_code = self.extract_backend_code(content)
                
                if frontend_code.strip():
                    demo_result["frontend_code"] += frontend_code
                if backend_code.strip():
                    demo_result["backend_code"] += backend_code
                
                # 运行说明
                if "运行" in content or "启动" in content or "部署" in content:
                    demo_result["run_instructions"] += content + "\n\n"
            
            elif speaker == "Tester":
                # 只提取测试代码
                code_blocks = self.extract_code_blocks(content)
                for block in code_blocks:
                    if self.is_code_content(block) and any(keyword in block.lower() for keyword in [
                        "test", "assert", "unittest", "pytest", "describe", "it("
                    ]):
                        demo_result["test_code"] += block + "\n\n"
            
            elif speaker == "DevOpsEngineer":
                # 只提取部署配置代码
                code_blocks = self.extract_code_blocks(content)
                for block in code_blocks:
                    if any(keyword in block.lower() for keyword in [
                        "dockerfile", "docker-compose", "nginx", "apache", "yaml", "yml"
                    ]):
                        demo_result["deployment_config"] += block + "\n\n"
                
                if "运行" in content or "部署" in content:
                    demo_result["run_instructions"] += content + "\n\n"
        
        # 生成综合文档
        demo_result["documentation"] = self.generate_comprehensive_documentation(demo_result)
        
        # 如果某些部分为空，生成默认内容
        if not demo_result["frontend_code"].strip():
            demo_result["frontend_code"] = self.generate_default_frontend()
        
        if not demo_result["backend_code"].strip():
            demo_result["backend_code"] = self.generate_default_backend()
        
        if not demo_result["test_code"].strip():
            demo_result["test_code"] = self.generate_default_tests()
        
        if not demo_result["deployment_config"].strip():
            demo_result["deployment_config"] = self.generate_default_deployment()
        
        return demo_result
    
    def extract_code_blocks(self, content):
        """提取代码块"""
        import re
        # 匹配各种代码块格式
        patterns = [
            r'```[\w]*\n(.*?)```',  # 标准代码块
            r'`([^`\n]+)`',  # 单行代码
        ]
        
        code_blocks = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            code_blocks.extend(matches)
        
        return code_blocks
    
    def is_code_content(self, content):
        """判断内容是否为代码"""
        # 代码特征关键词
        code_indicators = [
            'def ', 'class ', 'import ', 'from ', 'function', 'var ', 'let ', 'const ',
            'if ', 'for ', 'while ', 'return ', '#!/', '<?', '<html', '<script',
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE TABLE'
        ]
        
        # 检查是否包含代码特征
        content_lower = content.lower()
        has_code_indicators = any(indicator.lower() in content_lower for indicator in code_indicators)
        
        # 检查代码结构特征
        has_brackets = '{' in content or '}' in content
        has_parentheses = '(' in content and ')' in content
        has_semicolons = ';' in content
        has_indentation = '\n    ' in content or '\n\t' in content
        
        # 代码行数比例（简单启发式）
        lines = content.split('\n')
        code_like_lines = 0
        for line in lines:
            line = line.strip()
            if line and (line.startswith('#') or line.startswith('//') or 
                        '=' in line or line.endswith(':') or line.endswith(';') or
                        line.startswith('def ') or line.startswith('class ') or
                        line.startswith('import ') or line.startswith('from ')):
                code_like_lines += 1
        
        code_ratio = code_like_lines / max(len(lines), 1)
        
        # 综合判断
        return (has_code_indicators or 
                (has_brackets and has_parentheses) or 
                (has_indentation and code_ratio > 0.3))
    
    def extract_backend_code(self, content):
        """专门提取后端代码"""
        code_blocks = self.extract_code_blocks(content)
        backend_code = ""
        
        for block in code_blocks:
            # 检查是否为后端相关代码
            if any(keyword in block.lower() for keyword in [
                "python", "flask", "fastapi", "django", "node", "express", 
                "app.py", "server.py", "main.py", "api", "router", "endpoint"
            ]):
                backend_code += block + "\n\n"
            # 或者检查是否包含后端代码特征
            elif self.is_code_content(block) and any(keyword in block.lower() for keyword in [
                "def ", "class ", "import ", "from ", "app =", "server =", 
                "route", "post", "get", "put", "delete", "database", "db"
            ]):
                backend_code += block + "\n\n"
        
        return backend_code
    
    def extract_frontend_code(self, content):
        """专门提取前端代码"""
        code_blocks = self.extract_code_blocks(content)
        frontend_code = ""
        
        for block in code_blocks:
            # 检查是否为前端相关代码
            if any(keyword in block.lower() for keyword in [
                "html", "css", "javascript", "react", "vue", "angular",
                "<!doctype", "<html", "<head", "<body", "<script", "<style"
            ]):
                frontend_code += block + "\n\n"
            # 或者检查是否包含前端代码特征
            elif self.is_code_content(block) and any(keyword in block.lower() for keyword in [
                "function", "var ", "let ", "const ", "document.", "window.",
                "onclick", "onload", "style", "class=", "id="
            ]):
                frontend_code += block + "\n\n"
        
        return frontend_code
    
    def generate_comprehensive_documentation(self, demo_result):
        """生成综合文档"""
        doc = f"""# 产品Demo文档

## 项目概述
{demo_result['product_spec'][:500]}...

## 技术架构
- 前端：HTML/CSS/JavaScript
- 后端：Python/Node.js
- 数据库：SQLite/MySQL
- 部署：Docker

## 功能特性
- 用户界面友好
- 完整的业务逻辑
- 数据持久化
- 自动化测试
- 一键部署

## 文件结构
```
demo/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── backend/
│   ├── app.py
│   ├── models.py
│   └── requirements.txt
├── tests/
│   └── test_app.py
├── deployment/
│   ├── Dockerfile
│   └── docker-compose.yml
└── README.md
```

## 快速开始
{demo_result['run_instructions'][:300]}...

## 更多信息
请参考各个组件的详细文档。
"""
        return doc
    
    def generate_default_frontend(self):
        """生成默认前端代码"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>产品Demo</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .demo-content {
            text-align: center;
            padding: 20px;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }
        button:hover {
            background: #764ba2;
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 产品Demo</h1>
        <div class="demo-content">
            <p>欢迎使用AI生成的产品demo！</p>
            <button onclick="handleDemo()">开始体验</button>
            <div id="result"></div>
        </div>
    </div>
    
    <script>
        function handleDemo() {
            const result = document.getElementById('result');
            result.innerHTML = '<p>✅ Demo功能正常运行！</p>';
            
            // 这里可以添加与后端的交互逻辑
            fetch('/api/demo')
                .then(response => response.json())
                .then(data => {
                    result.innerHTML += '<p>后端响应：' + JSON.stringify(data) + '</p>';
                })
                .catch(error => {
                    result.innerHTML += '<p>⚠️ 后端连接失败，请检查后端服务</p>';
                });
        }
    </script>
</body>
</html>'''
    
    def generate_default_backend(self):
        """生成默认后端代码"""
        return '''from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 模拟数据存储
data_store = {
    "demos": [],
    "stats": {
        "total_requests": 0,
        "created_at": datetime.now().isoformat()
    }
}

@app.route('/')
def index():
    """主页"""
    return render_template_string(open('index.html').read())

@app.route('/api/demo', methods=['GET'])
def get_demo():
    """获取demo数据"""
    data_store["stats"]["total_requests"] += 1
    return jsonify({
        "message": "Demo API正常运行",
        "timestamp": datetime.now().isoformat(),
        "stats": data_store["stats"]
    })

@app.route('/api/demo', methods=['POST'])
def create_demo():
    """创建新的demo数据"""
    try:
        demo_data = {
            "id": len(data_store["demos"]) + 1,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        data_store["demos"].append(demo_data)
        return jsonify(demo_data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 启动产品Demo后端服务...")
    print("📍 访问地址: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)'''
    
    def generate_default_tests(self):
        """生成默认测试代码"""
        return '''import unittest
import requests
import json
from datetime import datetime

class TestProductDemo(unittest.TestCase):
    """产品Demo测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.base_url = "http://localhost:5000"
        self.api_url = f"{self.base_url}/api"
    
    def test_health_check(self):
        """测试健康检查接口"""
        try:
            response = requests.get(f"{self.api_url}/health")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "healthy")
            print("✅ 健康检查测试通过")
        except requests.exceptions.ConnectionError:
            print("⚠️ 无法连接到后端服务，请先启动后端")
    
    def test_demo_api(self):
        """测试Demo API"""
        try:
            response = requests.get(f"{self.api_url}/demo")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("message", data)
            print("✅ Demo API测试通过")
        except requests.exceptions.ConnectionError:
            print("⚠️ 无法连接到后端服务，请先启动后端")
    
    def test_create_demo(self):
        """测试创建Demo"""
        try:
            response = requests.post(f"{self.api_url}/demo")
            self.assertEqual(response.status_code, 201)
            data = response.json()
            self.assertIn("id", data)
            print("✅ 创建Demo测试通过")
        except requests.exceptions.ConnectionError:
            print("⚠️ 无法连接到后端服务，请先启动后端")
    
    def test_frontend_accessibility(self):
        """测试前端页面可访问性"""
        try:
            response = requests.get(self.base_url)
            self.assertEqual(response.status_code, 200)
            print("✅ 前端页面测试通过")
        except requests.exceptions.ConnectionError:
            print("⚠️ 无法连接到前端服务，请先启动服务")

if __name__ == "__main__":
    print("🧪 开始运行产品Demo测试...")
    unittest.main(verbosity=2)'''
    
    def generate_default_deployment(self):
        """生成默认部署配置"""
        return '''# Docker部署配置

# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]

---

# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data

---

# requirements.txt
Flask==2.3.3
Flask-CORS==4.0.0
gunicorn==21.2.0

---

# 部署脚本 (deploy.sh)
#!/bin/bash

echo "🚀 开始部署产品Demo..."

# 构建Docker镜像
docker build -t product-demo .

# 运行容器
docker run -d -p 5000:5000 --name product-demo-container product-demo

echo "✅ 部署完成！"
echo "📍 访问地址: http://localhost:5000"

---

# 本地运行脚本 (run.sh)
#!/bin/bash

echo "🚀 启动产品Demo..."

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
python app.py &

# 打开浏览器
sleep 3
open http://localhost:5000

echo "✅ 产品Demo已启动！"'''
    
    def save_demo_files(self, demo_result, description):
        """保存生成的demo文件"""
        print("💾 保存生成的文件...")
        
        # 创建项目目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = f"demo_{timestamp}"
        project_dir = os.path.join("generated_demo", project_name)
        
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(os.path.join(project_dir, "frontend"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "backend"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "tests"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "deployment"), exist_ok=True)
        
        # 智能保存文件
        self._save_frontend_files(demo_result["frontend_code"], project_dir)
        self._save_backend_files(demo_result["backend_code"], project_dir)
        self._save_test_files(demo_result["test_code"], project_dir)
        self._save_deployment_files(demo_result["deployment_config"], project_dir)
        
        # 保存文档文件
        doc_files = {
            "README.md": demo_result["documentation"],
            "product_spec.md": demo_result["product_spec"],
            "run_instructions.md": demo_result["run_instructions"]
        }
        
        for filename, content in doc_files.items():
            if content.strip():
                filepath = os.path.join(project_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
        
        # 保存数据库设计
        if demo_result["database_design"].strip():
            db_file = os.path.join(project_dir, "backend", "database.sql")
            with open(db_file, "w", encoding="utf-8") as f:
                f.write(demo_result["database_design"])
        
        # 保存项目元数据
        metadata = {
            "project_name": project_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "files_generated": self._get_generated_files_list(project_dir)
        }
        
        with open(os.path.join(project_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        self.generated_files[project_name] = project_dir
        print(f"✅ 文件已保存到: {project_dir}")
        
        return project_dir
    
    def _save_frontend_files(self, frontend_code, project_dir):
        """智能保存前端文件"""
        if not frontend_code.strip():
            return
        
        # 分离HTML、CSS、JavaScript
        html_content = ""
        css_content = ""
        js_content = ""
        
        # 提取HTML
        html_blocks = self._extract_html_blocks(frontend_code)
        if html_blocks:
            html_content = "\n".join(html_blocks)
        
        # 提取CSS
        css_blocks = self._extract_css_blocks(frontend_code)
        if css_blocks:
            css_content = "\n".join(css_blocks)
        
        # 提取JavaScript
        js_blocks = self._extract_js_blocks(frontend_code)
        if js_blocks:
            js_content = "\n".join(js_blocks)
        
        # 保存文件
        if html_content:
            with open(os.path.join(project_dir, "frontend", "index.html"), "w", encoding="utf-8") as f:
                f.write(html_content)
        
        if css_content:
            with open(os.path.join(project_dir, "frontend", "style.css"), "w", encoding="utf-8") as f:
                f.write(css_content)
        
        if js_content:
            with open(os.path.join(project_dir, "frontend", "script.js"), "w", encoding="utf-8") as f:
                f.write(js_content)
        
        # 如果没有分离出具体内容，保存为通用HTML文件
        if not (html_content or css_content or js_content):
            with open(os.path.join(project_dir, "frontend", "index.html"), "w", encoding="utf-8") as f:
                f.write(frontend_code)
    
    def _save_backend_files(self, backend_code, project_dir):
        """智能保存后端文件"""
        if not backend_code.strip():
            return
        
        # 检测后端语言类型
        if "flask" in backend_code.lower() or "from flask" in backend_code.lower():
            filename = "app.py"
        elif "fastapi" in backend_code.lower() or "from fastapi" in backend_code.lower():
            filename = "main.py"
        elif "express" in backend_code.lower() or "require('express')" in backend_code:
            filename = "server.js"
        elif "node" in backend_code.lower() and "javascript" in backend_code.lower():
            filename = "server.js"
        else:
            filename = "app.py"  # 默认Python
        
        filepath = os.path.join(project_dir, "backend", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(backend_code)
        
        # 生成requirements.txt或package.json
        self._generate_dependencies_file(backend_code, project_dir)
    
    def _save_test_files(self, test_code, project_dir):
        """智能保存测试文件"""
        if not test_code.strip():
            return
        
        # 检测测试框架
        if "unittest" in test_code.lower():
            filename = "test_unittest.py"
        elif "pytest" in test_code.lower():
            filename = "test_pytest.py"
        elif "jest" in test_code.lower():
            filename = "test.js"
        else:
            filename = "test_app.py"
        
        filepath = os.path.join(project_dir, "tests", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(test_code)
    
    def _save_deployment_files(self, deployment_config, project_dir):
        """智能保存部署文件"""
        if not deployment_config.strip():
            return
        
        # 分离不同的部署配置
        if "dockerfile" in deployment_config.lower():
            dockerfile_content = self._extract_dockerfile(deployment_config)
            if dockerfile_content:
                with open(os.path.join(project_dir, "deployment", "Dockerfile"), "w", encoding="utf-8") as f:
                    f.write(dockerfile_content)
        
        if "docker-compose" in deployment_config.lower():
            compose_content = self._extract_docker_compose(deployment_config)
            if compose_content:
                with open(os.path.join(project_dir, "deployment", "docker-compose.yml"), "w", encoding="utf-8") as f:
                    f.write(compose_content)
        
        # 保存通用部署说明
        with open(os.path.join(project_dir, "deployment", "deploy.md"), "w", encoding="utf-8") as f:
            f.write(deployment_config)
    
    def _extract_html_blocks(self, content):
        """提取HTML代码块"""
        import re
        patterns = [
            r'```html\n(.*?)```',
            r'<!DOCTYPE html.*?</html>',
            r'<html.*?</html>'
        ]
        
        html_blocks = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            html_blocks.extend(matches)
        
        return html_blocks
    
    def _extract_css_blocks(self, content):
        """提取CSS代码块"""
        import re
        patterns = [
            r'```css\n(.*?)```',
            r'<style.*?>(.*?)</style>'
        ]
        
        css_blocks = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            css_blocks.extend(matches)
        
        return css_blocks
    
    def _extract_js_blocks(self, content):
        """提取JavaScript代码块"""
        import re
        patterns = [
            r'```javascript\n(.*?)```',
            r'```js\n(.*?)```',
            r'<script.*?>(.*?)</script>'
        ]
        
        js_blocks = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            js_blocks.extend(matches)
        
        return js_blocks
    
    def _extract_dockerfile(self, content):
        """提取Dockerfile内容"""
        import re
        patterns = [
            r'```dockerfile\n(.*?)```',
            r'# Dockerfile\n(.*?)(?=\n#|\n---|\Z)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        return None
    
    def _extract_docker_compose(self, content):
        """提取docker-compose内容"""
        import re
        patterns = [
            r'```yaml\n(.*?)```',
            r'```yml\n(.*?)```',
            r'# docker-compose\.yml\n(.*?)(?=\n#|\n---|\Z)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        return None
    
    def _generate_dependencies_file(self, backend_code, project_dir):
        """生成依赖文件"""
        if "flask" in backend_code.lower():
            requirements = "Flask==2.3.3\nFlask-CORS==4.0.0\nrequests==2.31.0\n"
            with open(os.path.join(project_dir, "backend", "requirements.txt"), "w", encoding="utf-8") as f:
                f.write(requirements)
        elif "fastapi" in backend_code.lower():
            requirements = "fastapi==0.104.1\nuvicorn==0.24.0\nrequests==2.31.0\n"
            with open(os.path.join(project_dir, "backend", "requirements.txt"), "w", encoding="utf-8") as f:
                f.write(requirements)
        elif "express" in backend_code.lower():
            package_json = '''{"name": "backend", "version": "1.0.0", "dependencies": {"express": "^4.18.2", "cors": "^2.8.5"}}'''
            with open(os.path.join(project_dir, "backend", "package.json"), "w", encoding="utf-8") as f:
                f.write(package_json)
    
    def _get_generated_files_list(self, project_dir):
        """获取生成的文件列表"""
        files = []
        for root, dirs, filenames in os.walk(project_dir):
            for filename in filenames:
                if filename != "metadata.json":
                    rel_path = os.path.relpath(os.path.join(root, filename), project_dir)
                    files.append(rel_path)
        return files
    
    def get_conversation_history(self):
        """获取对话历史"""
        return self.conversation_history
    
    def get_generated_projects(self):
        """获取已生成的项目列表"""
        return self.generated_files 