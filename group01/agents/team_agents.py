import autogen
from typing import Dict, Any, List
import json
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_client_factory import LLMClientFactory

class GameDevelopmentTeam:
    def __init__(self, llm_key: str = "default_llm", model_key: str = "default_model"):
        """初始化游戏开发团队"""
        self.llm_key = llm_key
        self.model_key = model_key
        self.config = LLMClientFactory.get_client_by_name(llm_key, model_key)
        self.agents = {}
        self.group_chat = None
        self.messages: List[Dict[str, Any]] = []  # 记录所有消息
        self.init_agents()
        
    def init_agents(self):
        """初始化所有Agent角色"""
        
        # 产品经理Agent
        self.product_manager = autogen.AssistantAgent(
            name="产品经理",
            system_message="你是一位经验丰富的产品经理，专门负责HTML5小游戏的产品设计。请先分析市场需求，提出关键问题和产品设计建议。",
            llm_config=self.config
        )
        
        # 项目经理Agent
        self.project_manager = autogen.AssistantAgent(
            name="项目经理",
            system_message="你是一位资深的项目经理，专门负责HTML5小游戏项目的管理。请根据产品经理的分析，分配任务、制定项目计划。",
            llm_config=self.config
        )
        
        # 开发工程师Agent
        self.developer = autogen.AssistantAgent(
            name="开发工程师",
            system_message="你是一位全栈开发工程师，专门负责HTML5小游戏的开发。请根据项目经理的分配，进行开发并汇报开发进度。",
            llm_config=self.config
        )
        
        # 测试工程师Agent
        self.tester = autogen.AssistantAgent(
            name="测试工程师",
            system_message="你是一位专业的测试工程师，专门负责HTML5小游戏的测试。请根据开发工程师的开发结果，进行测试并反馈测试情况。",
            llm_config=self.config
        )
        
        # 市场端用户代理 - 禁用代码执行
        self.market_user = autogen.UserProxyAgent(
            name="市场端",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            system_message="你是市场端的代表，负责提出游戏开发需求。请清晰表达需求。",
            llm_config=self.config,
            code_execution_config={"use_docker": False}  # 禁用Docker
        )

    def _append_message(self, name: str, content: str, stage: str):
        """添加消息到消息列表"""
        self.messages.append({
            "name": name,
            "content": content,
            "stage": stage,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def _get_agent_reply(self, agent, message: str) -> str:
        """获取Agent的回复"""
        try:
            # 创建临时用户代理来与Agent对话
            temp_user = autogen.UserProxyAgent(
                name="临时用户",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=1,
                llm_config=self.config,
                code_execution_config={"use_docker": False}
            )
            
            # 启动对话并捕获回复
            chat_result = temp_user.initiate_chat(
                agent,
                message=message
            )
            
            # 尝试多种方式获取回复
            if chat_result:
                # 如果直接返回了结果
                if isinstance(chat_result, str):
                    return chat_result
                elif isinstance(chat_result, dict):
                    return chat_result.get('content', str(chat_result))
                else:
                    return str(chat_result)
            
            # 尝试从chat_messages获取
            if hasattr(temp_user, 'chat_messages') and temp_user.chat_messages:
                # 获取最后一条消息
                last_message = temp_user.chat_messages[-1]
                if isinstance(last_message, dict):
                    return last_message.get('content', str(last_message))
                elif isinstance(last_message, str):
                    return last_message
                else:
                    return str(last_message)
            
            # 尝试从agent的chat_messages获取
            if hasattr(agent, 'chat_messages') and agent.chat_messages:
                last_message = agent.chat_messages[-1]
                if isinstance(last_message, dict):
                    return last_message.get('content', str(last_message))
                elif isinstance(last_message, str):
                    return last_message
                else:
                    return str(last_message)
            
            # 如果都获取不到，返回默认回复
            return f"{agent.name}已收到消息并正在处理..."
                
        except Exception as e:
            return f"获取{agent.name}回复时出错: {str(e)}"

    def start_development_process(self, market_requirement: str) -> List[Dict[str, Any]]:
        """顺序推进多角色协作，每个角色依次输出反馈"""
        try:
            # 1. 市场端输入需求
            self._append_message("市场端", market_requirement, "需求输入")

            # 2. 产品经理分析需求
            pm_input = f"市场端需求：{market_requirement}\n\n请分析需求，提出关键问题和产品设计建议。"
            pm_reply = self._get_agent_reply(self.product_manager, pm_input)
            self._append_message("产品经理", pm_reply, "需求分析")

            # 3. 项目经理分配任务
            proj_input = f"产品经理分析结果：{pm_reply}\n\n请根据分析分配任务，制定项目计划。"
            proj_reply = self._get_agent_reply(self.project_manager, proj_input)
            self._append_message("项目经理", proj_reply, "任务分配")

            # 4. 开发工程师开发
            dev_input = f"项目经理任务分配：{proj_reply}\n\n请根据分配进行开发并汇报开发进度。"
            dev_reply = self._get_agent_reply(self.developer, dev_input)
            self._append_message("开发工程师", dev_reply, "开发进度")

            # 5. 测试工程师测试
            test_input = f"开发工程师开发进度：{dev_reply}\n\n请根据开发结果进行测试并反馈测试情况。"
            test_reply = self._get_agent_reply(self.tester, test_input)
            self._append_message("测试工程师", test_reply, "测试反馈")

            return self.messages
            
        except Exception as e:
            # 如果出错，添加错误消息
            self._append_message("系统", f"开发过程中出现错误: {str(e)}", "错误")
            raise e 