# 🚀 AI多Agent产品Demo生成器

基于AutoGen框架的智能产品开发系统，通过一句话描述即可生成完整的可运行产品Demo。

## ✨ 核心特性

- **🧠 智能产品规划**: 产品经理Agent深度分析需求，制定完整的产品规格
- **🎨 专业UI设计**: UI设计师Agent创建美观现代的用户界面
- **⚙️ 后端开发**: 后端开发Agent构建完整的API和业务逻辑
- **🔧 全栈整合**: 全栈Agent整合前后端，确保完整功能
- **🧪 自动化测试**: 测试Agent生成完整的测试用例和验证
- **🚀 一键部署**: 部署Agent提供Docker和部署解决方案

## 🔄 开发流程

```
用户需求 → 产品规划 → UI设计 → 后端开发 → 全栈整合 → 测试验证 → 部署上线 → 完整产品Demo
```

## 🏗️ 技术架构

### 多Agent协作系统

1. **ProductManager**: 产品经理Agent
   - 需求分析和产品规划
   - 功能规格制定
   - 技术栈选择

2. **UIDesigner**: UI/UX设计师Agent
   - 用户界面设计
   - 前端代码生成
   - 用户体验优化

3. **BackendDeveloper**: 后端开发Agent
   - API设计和开发
   - 数据库设计
   - 业务逻辑实现

4. **FullstackDeveloper**: 全栈开发Agent
   - 前后端整合
   - 完整功能实现
   - 性能优化

5. **Tester**: 测试工程师Agent
   - 测试用例设计
   - 功能验证
   - 质量保证

6. **DevOpsEngineer**: 部署工程师Agent
   - 部署方案设计
   - Docker配置
   - 运行指南

### 技术栈

- **框架**: AutoGen, Gradio
- **后端**: Python Flask
- **前端**: HTML/CSS/JavaScript
- **AI模型**: OpenAI GPT-4
- **部署**: Docker
- **测试**: Python unittest

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd agent_learn
```

### 2. 安装依赖

我们提供了多种安装方式，推荐使用清华镜像源加速安装：

#### 方式1：使用清华镜像源快速安装（推荐）

```bash
# 使用快速安装脚本（使用清华镜像源）
bash install_with_mirror.sh
```

#### 方式2：完整安装脚本

```bash
# 使用完整安装脚本（自动尝试多种方式）
bash install_dependencies.sh
```

#### 方式3：手动安装

```bash
# 使用清华镜像源手动安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 如果上面失败，尝试备用依赖文件
pip install -r requirements-alternative.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 方式4：常规安装

```bash
# 常规pip安装
pip install -r requirements.txt
```

### 3. 配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入您的OpenAI API密钥
# OPENAI_API_KEY=your_openai_api_key_here
```

### 4. 启动应用

```bash
python app.py
```

应用将在 http://localhost:7860 启动

## 📖 使用指南

### 基本使用

1. **访问界面**: 打开浏览器访问 http://localhost:7860
2. **输入需求**: 在文本框中描述您想要的产品功能
3. **生成Demo**: 点击"🚀 生成产品Demo"按钮
4. **查看结果**: 在不同标签页查看生成的前端、后端、测试等代码
5. **下载项目**: 点击"📦 下载完整产品Demo"获取完整项目

### 示例需求

- **待办事项管理**: "开发一个在线待办事项管理系统，用户可以添加、编辑、删除任务，支持分类和优先级设置"
- **在线聊天室**: "创建一个实时在线聊天室应用，支持多用户聊天、消息历史记录、用户状态显示"
- **数据可视化**: "构建一个数据可视化仪表板，可以上传CSV文件，自动生成各种图表"
- **电商平台**: "开发一个简单的电商平台，包含商品展示、购物车、用户注册登录、订单管理等功能"

## 📁 项目结构

```
agent_learn/
├── app.py                 # 主应用文件
├── agents.py              # Agent定义
├── workflow.py            # 工作流程
├── config.py              # 配置文件
├── requirements.txt       # 依赖包
├── .env.example          # 环境变量模板
├── README.md             # 项目说明
└── generated_demo/       # 生成的Demo项目
    └── demo_20240101_120000/
        ├── frontend/      # 前端文件
        ├── backend/       # 后端文件
        ├── tests/         # 测试文件
        ├── deployment/    # 部署配置
        └── README.md     # 项目文档
```

## 🔧 生成的Demo项目结构

每个生成的产品Demo包含：

```
demo_project/
├── frontend/
│   └── index.html        # 前端界面
├── backend/
│   ├── app.py           # 后端服务
│   └── requirements.txt # 依赖包
├── tests/
│   └── test_demo.py     # 测试用例
├── deployment/
│   └── README.md        # 部署说明
├── Dockerfile           # Docker配置
├── start.sh            # 启动脚本
└── README.md           # 项目文档
```

## 🏃‍♂️ 运行生成的Demo

### 本地运行

```bash
cd generated_demo/demo_xxxxxxxx_xxxxxx
./start.sh
```

### Docker运行

```bash
cd generated_demo/demo_xxxxxxxx_xxxxxx
docker build -t product-demo .
docker run -p 5000:5000 product-demo
```

## 🧪 测试

```bash
# 运行生成的测试
cd generated_demo/demo_xxxxxxxx_xxxxxx/tests
python test_demo.py
```

## 🔧 配置说明

### 环境变量

- `OPENAI_API_KEY`: OpenAI API密钥（必需）
- `OPENAI_API_BASE`: OpenAI API基础URL（可选）

### pip镜像源配置（可选但推荐）

为了提高包安装速度，建议配置pip使用清华大学镜像源：

#### 方式1：使用配置脚本（推荐）

```bash
# 自动配置pip镜像源
bash setup_pip_mirror.sh
```

#### 方式2：手动配置

**Linux/macOS:**
```bash
# 创建pip配置目录
mkdir -p ~/.config/pip  # Linux
# 或者
mkdir -p ~/Library/Application\ Support/pip  # macOS

# 创建配置文件
cat > ~/.config/pip/pip.conf << EOF  # Linux
# 或者 ~/Library/Application\ Support/pip/pip.conf  # macOS
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
```

**Windows:**
```cmd
# 创建pip配置目录
mkdir %APPDATA%\pip

# 创建配置文件 %APPDATA%\pip\pip.ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
```

#### 方式3：临时使用镜像源

```bash
# 单次安装时使用镜像源
pip install package_name -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Agent配置

可以在 `config.py` 中调整：

- 模型选择（GPT-4, GPT-3.5等）
- 温度参数
- 超时设置
- 最大对话轮数

## 🚀 部署

### 本地部署

```bash
python app.py
```

### Docker部署

```bash
docker build -t ai-product-demo-generator .
docker run -p 7860:7860 -e OPENAI_API_KEY=your_key ai-product-demo-generator
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [AutoGen](https://github.com/microsoft/autogen) - 多Agent协作框架
- [Gradio](https://gradio.app/) - 机器学习应用界面
- [OpenAI](https://openai.com/) - GPT模型支持

## 📞 联系我们

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 参与讨论

---

**让AI帮你一句话生成完整的产品Demo！** 🚀 