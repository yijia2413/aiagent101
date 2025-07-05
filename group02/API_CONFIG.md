# API配置说明

本项目支持多种AI API提供商，您可以根据需要选择合适的API服务。

## 支持的API提供商

### 1. 🚀 DeepSeek API (推荐)
- **优势**: 性价比高，中文支持好，API稳定
- **费用**: 相对便宜
- **获取方式**: [DeepSeek官网](https://platform.deepseek.com/)

### 2. 🤖 OpenAI API
- **优势**: 功能强大，生态完善
- **费用**: 相对较贵
- **获取方式**: [OpenAI官网](https://platform.openai.com/)

### 3. ☁️ Azure OpenAI
- **优势**: 企业级服务，稳定性好
- **费用**: 按使用量计费
- **获取方式**: [Azure门户](https://azure.microsoft.com/zh-cn/products/ai-services/openai-service)

### 4. 🌙 Moonshot API
- **优势**: 国产化，长文本支持
- **费用**: 合理定价
- **获取方式**: [Moonshot官网](https://platform.moonshot.cn/)

### 5. 🔥 通义千问 API
- **优势**: 阿里云服务，中文优化
- **费用**: 灵活计费
- **获取方式**: [阿里云控制台](https://dashscope.console.aliyun.com/)

## 配置步骤

### 第一步：复制配置文件
```bash
cp .env.example .env
```

### 第二步：编辑配置文件
```bash
nano .env  # 或使用其他编辑器
```

### 第三步：选择API提供商
在`.env`文件中设置：
```bash
API_PROVIDER=deepseek  # 可选值: openai, deepseek, azure, moonshot, qwen
```

### 第四步：配置对应的API密钥

#### 使用DeepSeek API
```bash
API_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-chat
```

#### 使用OpenAI API
```bash
API_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
```

#### 使用Azure OpenAI
```bash
API_PROVIDER=azure
AZURE_API_KEY=your_azure_api_key_here
AZURE_API_BASE=https://your-resource.openai.azure.com
AZURE_MODEL=gpt-4
```

#### 使用Moonshot API
```bash
API_PROVIDER=moonshot
MOONSHOT_API_KEY=your_moonshot_api_key_here
MOONSHOT_MODEL=moonshot-v1-8k
```

#### 使用通义千问API
```bash
API_PROVIDER=qwen
QWEN_API_KEY=your_qwen_api_key_here
QWEN_MODEL=qwen-turbo
```

## 高级配置

### 调整API参数
```bash
API_TEMPERATURE=0.7    # 控制输出的随机性 (0.0-1.0)
API_TIMEOUT=120        # 请求超时时间(秒)
```

### 模型选择建议

| 提供商 | 推荐模型 | 特点 |
|--------|----------|------|
| DeepSeek | deepseek-chat | 性价比高，中文友好 |
| OpenAI | gpt-4 | 功能最强，但费用高 |
| Azure | gpt-4 | 企业级稳定性 |
| Moonshot | moonshot-v1-8k | 长文本处理 |
| 通义千问 | qwen-turbo | 中文优化 |

## 费用对比

| 提供商 | 大致费用 | 备注 |
|--------|----------|------|
| DeepSeek | 💰 | 最便宜 |
| 通义千问 | 💰💰 | 较便宜 |
| Moonshot | 💰💰💰 | 中等 |
| OpenAI | 💰💰💰💰 | 较贵 |
| Azure | 💰💰💰💰💰 | 最贵但最稳定 |

## 故障排除

### 1. API密钥无效
- 检查密钥是否正确复制
- 确认API密钥是否已激活
- 检查账户余额是否充足

### 2. 网络连接问题
- 检查网络连接
- 尝试更换API_BASE地址
- 考虑使用代理

### 3. 模型不支持
- 检查模型名称是否正确
- 确认账户是否有权限使用该模型
- 尝试使用默认模型

### 4. 请求超时
- 增加API_TIMEOUT值
- 检查网络稳定性
- 尝试重新启动应用

## 推荐配置

### 开发测试环境
```bash
API_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_key_here
API_TEMPERATURE=0.7
API_TIMEOUT=120
```

### 生产环境
```bash
API_PROVIDER=azure
AZURE_API_KEY=your_key_here
AZURE_API_BASE=https://your-resource.openai.azure.com
API_TEMPERATURE=0.5
API_TIMEOUT=180
```

## 获取API密钥的详细步骤

### DeepSeek API
1. 访问 [DeepSeek官网](https://platform.deepseek.com/)
2. 注册账户并完成认证
3. 进入控制台，创建API密钥
4. 充值账户余额
5. 复制API密钥到.env文件

### OpenAI API
1. 访问 [OpenAI官网](https://platform.openai.com/)
2. 注册账户并绑定支付方式
3. 进入API Keys页面
4. 创建新的API密钥
5. 复制密钥到.env文件

### 其他API提供商
请参考各自官方文档获取API密钥。

## 安全建议

1. **不要将API密钥提交到版本控制系统**
2. **定期更换API密钥**
3. **设置合理的使用限制**
4. **监控API使用情况和费用**
5. **在生产环境中使用环境变量而非文件**

## 联系支持

如果在配置过程中遇到问题，请：
1. 检查本文档的故障排除部分
2. 查看各API提供商的官方文档
3. 在项目中提交Issue
4. 联系对应API提供商的技术支持 