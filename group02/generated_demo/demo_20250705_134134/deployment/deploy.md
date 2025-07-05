# 五子棋游戏部署方案

## 1. 部署概述
这是一个纯Python实现的命令行五子棋游戏，无需任何外部依赖，仅需Python 3.8环境即可运行。

## 2. 部署环境要求
- Python 3.8+
- 无需数据库
- 无需前端服务器
- 支持Windows/Linux/macOS系统

## 3. 部署方案

### 3.1 直接运行方案
```bash
# 1. 下载游戏文件
wget https://example.com/gomoku.py

# 2. 运行游戏
python gomoku.py
```

### 3.2 Docker容器化方案
```dockerfile
# Dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY gomoku.py .

ENTRYPOINT ["python", "gomoku.py"]
```

构建和运行命令：
```bash
# 构建镜像
docker build -t gomoku .

# 运行容器
docker run -it --rm gomoku
```

### 3.3 可执行文件打包方案
使用PyInstaller创建独立可执行文件：
```bash
pip install pyinstaller
pyinstaller --onefile gomoku.py

# 生成的执行文件在dist目录下
./dist/gomoku
```

## 4. 自动化部署脚本

### 4.1 Linux/macOS部署脚本
```bash
#!/bin/bash
# deploy_gomoku.sh

# 检查Python版本
python_version=$(python3 -c 'import sys; print(sys.version_info.major, sys.version_info.minor)')
if [ "$python_version" != "3 8" ]; then
    echo "需要Python 3.8，当前版本: $python_version"
    exit 1
fi

# 下载游戏文件
curl -o gomoku.py https://example.com/gomoku.py

# 设置执行权限
chmod +x gomoku.py

# 安装依赖（无）
echo "无需额外依赖"

# 启动游戏
echo "游戏已安装完成，使用以下命令启动："
echo "python gomoku.py"
```

### 4.2 Windows部署脚本
```powershell
# deploy_gomoku.ps1

# 检查Python版本
$pythonVersion = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ($pythonVersion -ne "3.8") {
    Write-Host "需要Python 3.8，当前版本: $pythonVersion"
    exit 1
}

# 下载游戏文件
Invoke-WebRequest -Uri "https://example.com/gomoku.py" -OutFile "gomoku.py"

Write-Host "游戏已安装完成，使用以下命令启动："
Write-Host "python gomoku.py"
```

## 5. 运行指南

### 5.1 基本使用
```bash
# 启动游戏
python gomoku.py

# 游戏控制命令
- 输入坐标格式：行,列 (如 7,7)
- 输入'restart'重新开始
- 输入'quit'退出游戏
```

### 5.2 游戏示例
```
  0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
 0 . . . . . . . . . . . . . . .
 1 . . . . . . . . . . . . . . .
 2 . . . . . . . . . . . . . . .
 3 . . . . . . . . . . . . . . .
 4 . . . . . . . . . . . . . . .
 5 . . . . . . . . . . . . . . .
 6 . . . . . . . . . . . . . . .
 7 . . . . . . . . . . . . . . .
 8 . . . . . . . . . . . . . . .
 9 . . . . . . . . . . . . . . .
10 . . . . . . . . . . . . . . .
11 . . . . . . . . . . . . . . .
12 . . . . . . . . . . . . . . .
13 . . . . . . . . . . . . . . .
14 . . . . . . . . . . . . . . .
当前玩家: X
请输入落子坐标: 7,7
```

## 6. 系统集成方案

### 6.1 作为模块导入
```python
from gomoku import Gomoku

game = Gomoku()
game.make_move(7, 7)
game.print_board()
```

### 6.2 自动化测试集成
```bash
# 运行单元测试
python -m unittest test_gomoku.py
```

## 7. 监控与维护

### 7.1 日志记录
游戏内置简单日志记录：
```python
import logging
logging.basicConfig(filename='gomoku.log', level=logging.INFO)
```

### 7.2 健康检查
```bash
# 检查游戏是否正常运行
python -c "from gomoku import Gomoku; game = Gomoku(); game.make_move(7,7); assert game.board[7][7] == 'X'"
```

## 8. 卸载方案

### 8.1 直接删除文件
```bash
rm gomoku.py
```

### 8.2 Docker容器清理
```bash
docker rmi gomoku
```

## 9. 常见问题解决

| 问题 | 解决方案 |
|------|----------|
| 无法识别Python命令 | 检查Python安装并确保在PATH中 |
| 坐标输入无效 | 使用"行,列"格式，如"7,7" |
| 游戏无响应 | 检查是否输入了正确命令 |
| 棋盘显示错乱 | 调整终端窗口大小或使用更大终端 |

## 10. 版本升级

```bash
# 下载最新版本
curl -o gomoku.py https://example.com/gomoku.py
```

## 11. 安全注意事项
- 游戏不涉及网络通信，无安全风险
- 不需要特殊权限
- 所有数据处理在内存中完成

## 12. 性能指标
- 启动时间：<100ms
- 内存占用：<10MB
- CPU使用率：可忽略不计

## 13. 部署验证

```bash
# 验证部署成功
python gomoku.py <<< "7,7" | grep "当前玩家: O"
```

这个部署方案提供了多种部署方式，从最简单的直接运行到容器化方案，满足不同场景需求。所有方案都保持了产品的核心优势：零依赖、单文件、即开即用。

