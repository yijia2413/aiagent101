from typing import Dict, Any
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def generate_code(design_doc: str) -> Dict[str, Any]:
    """根据设计文档生成并写入项目代码和部署文件"""
    # 生成并写入后端代码
    backend_prompt = ChatPromptTemplate.from_template(
        "作为Python开发者，请根据以下设计文档实现后端代码:\n\n"
        "设计文档:\n{design}\n\n"
        "要求:\n"
        "1. 使用Python 3.10+\n"
        "2. 包含完整的FastAPI实现\n"
        "3. 包含数据库模型定义\n"
        "4. 返回完整可运行的代码"
    )
    backend_chain = backend_prompt | StrOutputParser()
    try:
        backend_result = backend_chain.invoke({"design": design_doc})
        backend_code = str(backend_result) if not isinstance(backend_result, str) else backend_result
    except Exception as e:
        return {
            "code": {},
            "status": "fail", 
            "message": f"后端代码生成失败: {str(e)}"
        }
    
    backend_dir = "group03/project_code/backend"
    with open(f"{backend_dir}/main.py", "w") as f:
        f.write(backend_code)
    with open(f"{backend_dir}/requirements.txt", "w") as f:
        f.write("fastapi\nuvicorn\nsqlalchemy")

    # 生成并写入前端代码
    frontend_prompt = ChatPromptTemplate.from_template(
        "作为TypeScript开发者，请根据以下设计文档实现前端代码:\n\n"
        "设计文档:\n{design}\n\n"
        "要求:\n"
        "1. 使用React 18+\n"
        "2. 包含完整的页面组件\n"
        "3. 包含API调用逻辑\n"
        "4. 返回完整可运行的代码"
    )
    frontend_chain = frontend_prompt | StrOutputParser()
    try:
        frontend_result = frontend_chain.invoke({"design": design_doc})
        frontend_code = str(frontend_result) if not isinstance(frontend_result, str) else frontend_result
    except Exception as e:
        return {
            "code": {},
            "status": "fail",
            "message": f"前端代码生成失败: {str(e)}"
        }
    
    frontend_dir = "group03/project_code/frontend"
    os.makedirs(f"{frontend_dir}/src", exist_ok=True)
    with open(f"{frontend_dir}/src/App.tsx", "w") as f:
        f.write(frontend_code)
    with open(f"{frontend_dir}/package.json", "w") as f:
        f.write("""{
  "name": "frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.2"
  }
}""")

    # 生成并写入Dockerfile
    dockerfile_content = """# 后端构建阶段
FROM python:3.10-slim as backend
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# 前端构建阶段
FROM node:18 as frontend
WORKDIR /app
COPY frontend/package.json .
RUN npm install
COPY frontend/ .
RUN npm run build

# 生产阶段
FROM nginx:alpine
COPY --from=frontend /app/build /usr/share/nginx/html
COPY --from=backend /app /usr/share/nginx/api
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
"""
    with open("group03/project_code/Dockerfile", "w") as f:
        f.write(dockerfile_content)

    # 生成并写入README
    readme_content = """# 项目部署指南

## 构建Docker镜像
```bash
docker build -t myapp .
```

## 运行容器
```bash
docker run -p 8080:80 myapp
```

## 访问应用
- 前端: http://localhost:8080
- API: http://localhost:8080/api
"""
    with open("group03/project_code/README.md", "w") as f:
        f.write(readme_content)

    # 读取所有生成的文件内容
    backend_code = open(f"{backend_dir}/main.py").read()
    frontend_code = open(f"{frontend_dir}/src/App.tsx").read()
    dockerfile = open("group03/project_code/Dockerfile").read()
    readme = open("group03/project_code/README.md").read()
    
    return {
        "code": {
            "backend": backend_code,
            "frontend": frontend_code,
            "dockerfile": dockerfile,
            "readme": readme
        },
        "code_paths": {
            "backend": f"{backend_dir}/main.py",
            "frontend": f"{frontend_dir}/src/App.tsx",
            "dockerfile": "group03/project_code/Dockerfile",
            "readme": "group03/project_code/README.md"
        },
        "status": "success",
        "message": "项目代码和部署文件已生成"
    }
