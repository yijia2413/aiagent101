from typing import Dict, Any
import docker
from pathlib import Path

def test_docker_connection():
    try:
        client = docker.from_env()
        print("Docker 连接成功!")
        print(f"Docker 版本: {client.version()}")
        return True
    except Exception as e:
        print(f"Docker 连接失败: {str(e)}")
        return False

def deploy_project(test_report: Dict[str, Any], code_paths: Dict[str, str]) -> Dict[str, Any]:
    """部署通过测试的项目"""
    if test_report["status"] != "pass":
        return {
            "status": "fail",
            "message": "部署中止: 测试未通过",
            "details": test_report
        }
    
    try:
        # 构建Docker镜像
        build_result = build_docker_image(code_paths["dockerfile"])
        
        # 运行容器
        run_result = run_docker_container()
        
        return {
            "status": "success",
            "message": "部署成功",
            "container_id": run_result["container_id"],
            "access_url": "http://localhost:8080"
        }
        
    except Exception as e:
        return {
            "status": "fail",
            "message": f"部署失败: {str(e)}"
        }

def build_docker_image(dockerfile_path: str) -> Dict[str, Any]:
    """构建Docker镜像"""
    client = docker.from_env()
    
    # 获取Dockerfile所在目录
    docker_dir = str(Path(dockerfile_path).parent)
    
    # 构建镜像
    image, logs = client.images.build(
        path=docker_dir,
        tag="myapp:latest",
        rm=True
    )
    
    return {
        "image_id": image.id,
        "logs": [line for line in logs]
    }

def run_docker_container() -> Dict[str, Any]:
    """运行Docker容器"""
    client = docker.from_env()
    
    container = client.containers.run(
        "myapp:latest",
        ports={'80/tcp': 8080},
        detach=True
    )
    
    return {
        "container_id": container.id,
        "status": container.status
    }

if __name__ == "__main__":
    test_docker_connection()
