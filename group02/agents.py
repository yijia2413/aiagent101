import autogen
from config import OPENAI_CONFIG, AGENT_CONFIG

class ProductDemoAgents:
    def __init__(self):
        self.agents = {}
        self.setup_agents()
    
    def setup_agents(self):
        """设置所有的agent"""
        
        # 用户代理 - 负责接收用户需求并执行代码（需要用户确认）
        self.agents["user_proxy"] = autogen.UserProxyAgent(
            name="UserProxy",
            system_message="你是用户代理，负责接收用户的产品需求并协调其他代理完成完整的产品demo开发。你可以执行代码来验证和测试生成的内容，但每次执行前都会显示命令并等待用户确认。",
            code_execution_config={
                "work_dir": "generated_code",
                "use_docker": False,
                "timeout": 60,
                "last_n_messages": 3,
            },
            max_consecutive_auto_reply=AGENT_CONFIG.get("max_consecutive_auto_reply", 10),
            human_input_mode="ALWAYS",  # 总是需要人工确认
            is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", "").upper(),
        )
        
        # 产品经理代理 - 负责产品规划和需求分析
        self.agents["product_manager"] = autogen.AssistantAgent(
            name="ProductManager",
            system_message="""你是产品经理代理。你的职责是：
1. 深入分析用户的产品需求描述
2. 制定完整的产品功能规格和用户故事
3. 确定产品的核心功能和用户体验流程
4. 选择合适的技术栈和架构方案
5. 制定产品demo的开发计划和优先级
6. 确保产品具有良好的用户体验和商业价值

请用中文回复，提供详细的产品规划方案。""",
            llm_config=OPENAI_CONFIG,
        )
        
        # UI/UX设计师代理 - 负责界面设计和用户体验
        self.agents["ui_designer"] = autogen.AssistantAgent(
            name="UIDesigner",
            system_message="""你是UI/UX设计师代理。你的职责是：
1. 根据产品需求设计用户界面和交互流程
2. 创建现代化、美观的用户界面设计
3. 确保良好的用户体验和可用性
4. 提供具体的HTML/CSS/JavaScript前端代码
5. 使用现代前端框架（如React、Vue或原生HTML）
6. 确保响应式设计和移动端适配

请用中文回复，提供完整的前端界面代码。""",
            llm_config=OPENAI_CONFIG,
        )
        
        # 后端开发者代理 - 负责后端逻辑和API开发
        self.agents["backend_developer"] = autogen.AssistantAgent(
            name="BackendDeveloper",
            system_message="""你是后端开发者代理。你的职责是：
1. 根据产品需求开发后端API和业务逻辑
2. 设计数据库结构和数据模型
3. 实现用户认证、数据处理等核心功能
4. 提供RESTful API接口
5. 使用Python Flask/FastAPI或Node.js等技术栈
6. 确保代码的安全性和性能
7. 提供完整的后端服务代码

请用中文回复，提供完整的后端代码和API文档。""",
            llm_config=OPENAI_CONFIG,
        )
        
        # 全栈开发者代理 - 负责整合前后端和完整产品实现
        self.agents["fullstack_developer"] = autogen.AssistantAgent(
            name="FullstackDeveloper",
            system_message="""你是全栈开发者代理。你的职责是：
1. 整合前端和后端代码，确保完整的产品功能
2. 处理前后端数据交互和API集成
3. 实现完整的用户流程和业务逻辑
4. 优化性能和用户体验
5. 创建可直接运行的完整demo产品
6. 提供部署和运行说明
7. 确保产品的完整性和可用性

请用中文回复，提供完整的产品代码和部署方案。""",
            llm_config=OPENAI_CONFIG,
        )
        
        # 测试工程师代理 - 负责产品测试和质量保证
        self.agents["tester"] = autogen.AssistantAgent(
            name="Tester",
            system_message="""你是测试工程师代理。你的职责是：
1. 为产品demo编写完整的测试用例
2. 进行功能测试、用户体验测试和性能测试
3. 编写自动化测试脚本
4. 验证产品的各项功能是否正常工作
5. 提供测试报告和改进建议
6. 确保产品demo的质量和稳定性

请用中文回复，提供完整的测试方案和测试代码。""",
            llm_config=OPENAI_CONFIG,
        )
        
        # 部署工程师代理 - 负责产品部署和上线
        self.agents["devops_engineer"] = autogen.AssistantAgent(
            name="DevOpsEngineer",
            system_message="""你是部署工程师代理。你的职责是：
1. 创建产品demo的部署脚本和配置文件
2. 提供Docker容器化方案
3. 配置本地开发环境和生产环境
4. 创建自动化部署流程
5. 提供详细的部署文档和运行指南
6. 确保产品demo可以一键部署和运行

请用中文回复，提供完整的部署方案和运行指南。""",
            llm_config=OPENAI_CONFIG,
        )
    
    def get_agent(self, name):
        """获取指定的agent"""
        return self.agents.get(name)
    
    def get_all_agents(self):
        """获取所有agent"""
        return list(self.agents.values())
    
    def get_development_agents(self):
        """获取开发相关的agents"""
        return [
            self.agents["product_manager"],
            self.agents["ui_designer"], 
            self.agents["backend_developer"],
            self.agents["fullstack_developer"],
            self.agents["tester"],
            self.agents["devops_engineer"]
        ] 