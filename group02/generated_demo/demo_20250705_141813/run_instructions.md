# 纯前端贪吃蛇游戏部署方案

## 1. 部署概述

这是一个纯前端的贪吃蛇游戏，无需后端服务和数据库。部署方案非常简单，只需要将HTML文件部署到任何Web服务器或静态文件托管服务即可。

## 2. 部署选项

### 选项1：直接文件访问
直接将HTML文件保存在本地，用浏览器打开即可运行。

### 选项2：本地Web服务器
使用简单的本地Web服务器进行测试。

### 选项3：静态网站托管服务
部署到GitHub Pages、Netlify、Vercel等静态网站托管服务。

### 选项4：Docker容器化部署
将游戏打包为Docker容器，在任何支持Docker的环境中运行。

## 3. 一键部署脚本

### 3.1 本地运行脚本
创建`run-local.sh`脚本：
```bash
#!/bin/bash

# 检查是否安装了Python3
if command -v python3 &>/dev/null; then
    echo "使用Python3启动Web服务器..."
    python3 -m http.server 8000
elif command -v python &>/dev/null; then
    echo "使用Python2启动Web服务器..."
    python -m SimpleHTTPServer 8000
else
    echo "未找到Python，请直接打开snake-game.html文件"
    exit 1
fi
```

### 3.2 生产环境部署脚本
创建`deploy.sh`脚本：
```bash
#!/bin/bash

# 生产环境部署脚本
# 需要配置SSH访问权限

REMOTE_USER="username"
REMOTE_HOST="example.com"
REMOTE_PATH="/var/www/html/snake-game"

echo "开始部署贪吃蛇游戏到生产环境..."

# 检查文件是否存在
if [ ! -f "snake-game.html" ]; then
    echo "错误：找不到snake-game.html文件"
    exit 1
fi

# 部署文件
scp snake-game.html $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH

echo "部署完成！访问地址：http://$REMOTE_HOST/snake-game/snake-game.html"
```

## 4. Docker容器化方案

### 4.1 Dockerfile
创建`Dockerfile`：
```dockerfile
# 使用轻量级Nginx镜像
FROM nginx:alpine

# 复制游戏文件到容器
COPY snake-game.html /usr/share/nginx/html/index.html

# 暴露80端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]
```

### 4.2 Docker Compose文件
创建`docker-compose.yml`：
```yaml
version: '3.8'

services:
  snake-game:
    build: .
    ports:
      - "8080:80"
    restart: unless-stopped
```

### 4.3 Docker操作命令

构建镜像：
```bash
docker build -t snake-game .
```

运行容器：
```bash
docker run -d -p 8080:80 --name snake-game-container snake-game
```

或者使用Docker Compose：
```bash
docker-compose up -d
```

## 5. 自动化部署流程

### 5.1 GitHub Actions自动化部署
创建`.github/workflows/deploy.yml`：
```yaml
name: Deploy Snake Game

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./
        publish_branch: gh-pages
        keep_files: true
```

## 6. 运行指南

### 6.1 本地运行
1. 下载`snake-game.html`文件
2. 直接双击在浏览器中打开，或：
3. 运行本地Web服务器：
   ```bash
   ./run-local.sh
   ```
   然后在浏览器中访问`http://localhost:8000/snake-game.html`

### 6.2 Docker运行
1. 确保已安装Docker
2. 构建并运行容器：
   ```bash
   docker-compose up -d
   ```
3. 访问`http://localhost:8080`

### 6.3 生产环境部署
1. 修改`deploy.sh`中的远程服务器配置
2. 运行部署脚本：
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## 7. 配置说明

### 7.1 游戏配置
游戏参数可以在HTML文件的JavaScript部分修改：
```javascript
// 游戏常量配置
const GRID_SIZE = 20;        // 网格大小
const CELL_SIZE = 20;        // 每个格子像素大小
const INITIAL_SPEED = 150;   // 初始速度(毫秒)
```

### 7.2 Nginx配置（Docker）
如需自定义Nginx配置，可以创建`nginx.conf`并修改Dockerfile：
```dockerfile
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

## 8. 监控与维护

由于是纯静态应用，无需特殊维护。建议：
1. 定期检查浏览器兼容性
2. 如有更新，重新部署HTML文件

## 9. 部署验证

部署后访问游戏URL，验证：
1. 游戏是否能正常加载
2. 键盘控制是否正常工作
3. 分数是否能正确记录
4. 最高分是否能在刷新后保持

## 10. 故障排除

### 游戏无法加载
- 检查文件路径是否正确
- 检查服务器是否正常运行
- 查看浏览器控制台是否有错误

### 控制不工作
- 确保使用的是支持的浏览器（Chrome、Firefox、Safari、Edge等现代浏览器）
- 检查是否有其他JavaScript代码冲突

### 高分未保存
- 检查浏览器是否启用了localStorage
- 确保没有使用隐私浏览模式

## 11. 扩展部署选项

### 11.1 Netlify部署
1. 将代码推送到GitHub仓库
2. 登录Netlify，选择"New site from Git"
3. 选择仓库，保留默认设置
4. 点击"Deploy site"

### 11.2 Vercel部署
1. 安装Vercel CLI：`npm install -g vercel`
2. 运行：`vercel`
3. 按照提示完成部署

## 12. 安全考虑

由于是纯前端应用，主要安全考虑：
1. 确保托管服务使用HTTPS
2. 避免在代码中包含敏感信息
3. 定期检查依赖（虽然本项目无外部依赖）

## 13. 性能优化

已内置的性能优化：
1. 轻量级代码（无外部依赖）
2. 高效的Canvas渲染
3. 合理的游戏循环间隔

如需进一步优化：
1. 添加资源缓存头
2. 启用Gzip压缩
3. 使用CDN分发

## 14. 备份策略

建议：
1. 定期备份HTML文件
2. 使用版本控制系统（如Git）
3. 在多平台部署（如GitHub Pages + Netlify）

## 15. 文档结构

完整部署包应包含：
```
snake-game/
├── snake-game.html          # 主游戏文件
├── run-local.sh             # 本地运行脚本
├── deploy.sh                # 生产部署脚本
├── Dockerfile               # Docker构建文件
├── docker-compose.yml       # Docker Compose配置
├── README.md                # 使用说明
└── .github/workflows/       # GitHub Actions配置
    └── deploy.yml
```

## 16. 使用说明（README.md）

```markdown
# 纯前端贪吃蛇游戏

一个无需后端、零依赖的贪吃蛇游戏实现。

## 功能特性
- 键盘方向键控制
- 移动端触摸控制
- 分数记录
- 最高分保存（localStorage）
- 游戏暂停/继续

## 快速开始

### 本地运行
1. 下载`snake-game.html`
2. 直接在浏览器中打开，或：
3. 运行本地服务器：
   ```bash
   chmod +x run-local.sh
   ./run-local.sh
   ```
   访问 http://localhost:8000/snake-game.html

### Docker运行
```bash
docker-compose up -d
```
访问 http://localhost:8080

### 生产部署
1. 编辑`deploy.sh`配置服务器信息
2. 运行：
```bash
chmod +x deploy.sh
./deploy.sh
```

## 游戏控制
- 方向键：控制蛇的移动
- 空格键：暂停/继续游戏
- 移动端：使用屏幕上的方向按钮

## 自定义配置
编辑HTML文件中的JavaScript部分修改游戏参数：
```javascript
const GRID_SIZE = 20;        // 网格大小
const CELL_SIZE = 20;        // 每个格子像素大小
const INITIAL_SPEED = 150;   // 初始速度(毫秒)
```

## 许可证
MIT
```

## 17. 结论

这个纯前端贪吃蛇游戏部署简单，可以通过多种方式快速部署和运行。Docker容器化方案提供了最大的灵活性，而静态文件托管服务则提供了最简单的部署选项。

# 纯前端贪吃蛇游戏 - 完整实现与部署方案

根据产品需求，我已经整合了所有阶段的成果，提供一个完整的纯前端贪吃蛇游戏实现。以下是最终交付的所有内容：

## 1. 完整产品代码

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>纯JS贪吃蛇游戏</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f5f5f5;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }
        
        .game-container {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            padding: 20px;
            text-align: center;
            max-width: 500px;
            width: 100%;
        }
        
        h1 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 28px;
        }
        
        .score-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            font-size: 18px;
            color: #34495e;
        }
        
        .score {
            font-weight: bold;
            color: #e74c3c;
        }
        
        .high-score {
            font-weight: bold;
            color: #27ae60;
        }
        
        canvas {
            background-color: #ecf0f1;
            border-radius: 5px;
            display: block;
            margin: 0 auto;
            border: 2px solid #bdc3c7;
        }
        
        .controls {
            margin-top: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .game-status {
            margin-top: 15px;
            padding: 10px;
            border-radius: 5px;
            background-color: #f8f9fa;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .mobile-controls {
            display: none;
            grid-template-columns: repeat(3, 1fr);
            grid-template-rows: repeat(3, 1fr);
            gap: 5px;
            margin-top: 15px;
        }
        
        .mobile-btn {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-size: 16px;
            cursor: pointer;
            user-select: none;
        }
        
        .mobile-btn:active {
            background-color: #2980b9;
        }
        
        .mobile-btn.up {
            grid-column: 2;
            grid-row: 1;
        }
        
        .mobile-btn.left {
            grid-column: 1;
            grid-row: 2;
        }
        
        .mobile-btn.right {
            grid-column: 3;
            grid-row: 2;
        }
        
        .mobile-btn.down {
            grid-column: 2;
            grid-row: 3;
        }
        
        @media (max-width: 500px) {
            .mobile-controls {
                display: grid;
            }
            
            canvas {
                width: 100%;
                height: auto;
                max-width: 300px;
                max-height: 300px;
            }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <h1>贪吃蛇游戏</h1>
        
        <div class="score-container">
            <div>分数: <span class="score" id="current-score">0</span></div>
            <div>最高分: <span class="high-score" id="high-score">0</span></div>
        </div>
        
        <canvas id="game-canvas" width="400" height="400"></canvas>
        
        <div class="mobile-controls">
            <button class="mobile-btn up">↑</button>
            <button class="mobile-btn left">←</button>
            <button class="mobile-btn right">→</button>
            <button class="mobile-btn down">↓</button>
        </div>
        
        <div class="game-status" id="game-status">按方向键开始游戏</div>
        
        <div class="controls">
            <p>键盘控制: ↑ ↓ ← → | 空格键暂停</p>
        </div>
    </div>

    <script>
        // 游戏常量配置
        const GRID_SIZE = 20;
        const CELL_SIZE = 20;
        const INITIAL_SPEED = 150;
        
        // 游戏状态
        const GAME_STATES = {
            READY: 'ready',
            PLAYING: 'playing',
            PAUSED: 'paused',
            GAME_OVER: 'gameOver'
        };
        
        // 方向常量
        const DIRECTIONS = {
            UP: { x: 0, y: -1 },
            DOWN: { x: 0, y: 1 },
            LEFT: { x: -1, y: 0 },
            RIGHT: { x: 1, y: 0 }
        };
        
        // 获取DOM元素
        const canvas = document.getElementById('game-canvas');
        const ctx = canvas.getContext('2d');
        const currentScoreEl = document.getElementById('current-score');
        const highScoreEl = document.getElementById('high-score');
        const gameStatusEl = document.getElementById('game-status');
        const mobileBtns = document.querySelectorAll('.mobile-btn');
        
        // 游戏变量
        let snake = [];
        let food = {};
        let direction = DIRECTIONS.RIGHT;
        let nextDirection = DIRECTIONS.RIGHT;
        let gameState = GAME_STATES.READY;
        let score = 0;
        let highScore = localStorage.getItem('snakeHighScore') || 0;
        let gameSpeed = INITIAL_SPEED;
        let gameLoop;
        
        // 初始化游戏
        function initGame() {
            // 初始化蛇
            const startX = Math.floor(GRID_SIZE / 4);
            const startY = Math.floor(GRID_SIZE / 2);
            snake = [
                { x: startX, y: startY },
                { x: startX - 1, y: startY },
                { x: startX - 2, y: startY }
            ];
            
            // 初始化方向
            direction = DIRECTIONS.RIGHT;
            nextDirection = DIRECTIONS.RIGHT;
            
            // 生成食物
            generateFood();
            
            // 重置分数
            score = 0;
            currentScoreEl.textContent = score;
            highScoreEl.textContent = highScore;
            
            // 设置游戏状态
            gameState = GAME_STATES.READY;
            gameStatusEl.textContent = '按方向键开始游戏';
            
            // 绘制初始状态
            draw();
        }
        
        // 生成食物
        function generateFood() {
            let foodPosition;
            let isOnSnake;
            
            do {
                foodPosition = {
                    x: Math.floor(Math.random() * GRID_SIZE),
                    y: Math.floor(Math.random() * GRID_SIZE)
                };
                
                isOnSnake = snake.some(segment => 
                    segment.x === foodPosition.x && segment.y === foodPosition.y
                );
            } while (isOnSnake);
            
            food = foodPosition;
        }
        
        // 游戏主循环
        function gameUpdate() {
            if (gameState !== GAME_STATES.PLAYING) return;
            
            // 更新方向
            direction = nextDirection;
            
            // 移动蛇
            const head = { ...snake[0] };
            head.x += direction.x;
            head.y += direction.y;
            
            // 检查碰撞
            if (
                head.x < 0 || head.x >= GRID_SIZE ||
                head.y < 0 || head.y >= GRID_SIZE ||
                snake.some(segment => segment.x === head.x && segment.y === head.y)
            ) {
                gameOver();
                return;
            }
            
            // 添加新头部
            snake.unshift(head);
            
            // 检查是否吃到食物
            if (head.x === food.x && head.y === food.y) {
                // 增加分数
                score += 10;
                currentScoreEl.textContent = score;
                
                // 生成新食物
                generateFood();
                
                // 稍微加快游戏速度
                if (gameSpeed > 50 && score % 50 === 0) {
                    gameSpeed -= 5;
                    clearInterval(gameLoop);
                    gameLoop = setInterval(gameUpdate, gameSpeed);
                }
            } else {
                // 如果没有吃到食物，移除尾部
                snake.pop();
            }
            
            // 重绘游戏
            draw();
        }
        
        // 绘制游戏
        function draw() {
            // 清空画布
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 绘制网格背景
            ctx.fillStyle = '#ecf0f1';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // 绘制网格线
            ctx.strokeStyle = '#bdc3c7';
            ctx.lineWidth = 0.5;
            
            for (let i = 0; i <= GRID_SIZE; i++) {
                // 垂直线
                ctx.beginPath();
                ctx.moveTo(i * CELL_SIZE, 0);
                ctx.lineTo(i * CELL_SIZE, GRID_SIZE * CELL_SIZE);
                ctx.stroke();
                
                // 水平线
                ctx.beginPath();
                ctx.moveTo(0, i * CELL_SIZE);
                ctx.lineTo(GRID_SIZE * CELL_SIZE, i * CELL_SIZE);
                ctx.stroke();
            }
            
            // 绘制食物
            ctx.fillStyle = '#e74c3c';
            ctx.beginPath();
            ctx.arc(
                food.x * CELL_SIZE + CELL_SIZE / 2,
                food.y * CELL_SIZE + CELL_SIZE / 2,
                CELL_SIZE / 2 - 2,
                0,
                Math.PI * 2
            );
            ctx.fill();
            
            // 绘制蛇
            snake.forEach((segment, index) => {
                // 蛇头用不同颜色
                if (index === 0) {
                    ctx.fillStyle = '#2c3e50';
                } else {
                    // 蛇身渐变颜色
                    const colorValue = 150 + Math.floor(105 * (index / snake.length));
                    ctx.fillStyle = `rgb(44, 62, 80, ${colorValue / 255})`;
                }
                
                ctx.fillRect(
                    segment.x * CELL_SIZE + 1,
                    segment.y * CELL_SIZE + 1,
                    CELL_SIZE - 2,
                    CELL_SIZE - 2
                );
                
                // 添加圆角效果
                ctx.beginPath();
                ctx.roundRect(
                    segment.x * CELL_SIZE + 1,
                    segment.y * CELL_SIZE + 1,
                    CELL_SIZE - 2,
                    CELL_SIZE - 2,
                    4
                );
                ctx.fill();
            });
        }
        
        // 开始游戏
        function startGame() {
            if (gameState === GAME_STATES.READY || gameState === GAME_STATES.GAME_OVER) {
                initGame();
                gameState = GAME_STATES.PLAYING;
                gameStatusEl.textContent = '游戏中...';
                gameLoop = setInterval(gameUpdate, gameSpeed);
            } else if (gameState === GAME_STATES.PAUSED) {
                gameState = GAME_STATES.PLAYING;
                gameStatusEl.textContent = '游戏中...';
                gameLoop = setInterval(gameUpdate, gameSpeed);
            }
        }
        
        // 暂停游戏
        function pauseGame() {
            if (gameState === GAME_STATES.PLAYING) {
                gameState = GAME_STATES.PAUSED;
                clearInterval(gameLoop);
                gameStatusEl.textContent = '游戏已暂停 - 按空格键继续';
            }
        }
        
        // 游戏结束
        function gameOver() {
            gameState = GAME_STATES.GAME_OVER;
            clearInterval(gameLoop);
            
            // 更新最高分
            if (score > highScore) {
                highScore = score;
                localStorage.setItem('snakeHighScore', highScore);
                highScoreEl.textContent = highScore;
                gameStatusEl.textContent = `游戏结束! 新纪录: ${score}分 - 按空格键重新开始`;
            } else {
                gameStatusEl.textContent = `游戏结束! 得分: ${score}分 - 按空格键重新开始`;
            }
        }
        
        // 键盘控制
        function handleKeyDown(e) {
            switch (e.key) {
                case 'ArrowUp':
                    if (direction !== DIRECTIONS.DOWN) {
                        nextDirection = DIRECTIONS.UP;
                    }
                    if (gameState === GAME_STATES.READY) startGame();
                    e.preventDefault();
                    break;
                case 'ArrowDown':
                    if (direction !== DIRECTIONS.UP) {
                        nextDirection = DIRECTIONS.DOWN;
                    }
                    if (gameState === GAME_STATES.READY) startGame();
                    e.preventDefault();
                    break;
                case 'ArrowLeft':
                    if (direction !== DIRECTIONS.RIGHT) {
                        nextDirection = DIRECTIONS.LEFT;
                    }
                    if (gameState === GAME_STATES.READY) startGame();
                    e.preventDefault();
                    break;
                case 'ArrowRight':
                    if (direction !== DIRECTIONS.LEFT) {
                        nextDirection = DIRECTIONS.RIGHT;
                    }
                    if (gameState === GAME_STATES.READY) startGame();
                    e.preventDefault();
                    break;
                case ' ':
                    if (gameState === GAME_STATES.PLAYING) {
                        pauseGame();
                    } else {
                        startGame();
                    }
                    e.preventDefault();
                    break;
            }
        }
        
        // 移动端触摸控制
        function setupMobileControls() {
            mobileBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    if (gameState === GAME_STATES.READY) startGame();
                    
                    switch (btn.textContent) {
                        case '↑':
                            if (direction !== DIRECTIONS.DOWN) {
                                nextDirection = DIRECTIONS.UP;
                            }
                            break;
                        case '↓':
                            if (direction !== DIRECTIONS.UP) {
                                nextDirection = DIRECTIONS.DOWN;
                            }
                            break;
                        case '←':
                            if (direction !== DIRECTIONS.RIGHT) {
                                nextDirection = DIRECTIONS.LEFT;
                            }
                            break;
                        case '→':
                            if (direction !== DIRECTIONS.LEFT) {
                                nextDirection = DIRECTIONS.RIGHT;
                            }
                            break;
                    }
                });
            });
        }
        
        // 初始化
        function init() {
            initGame();
            document.addEventListener('keydown', handleKeyDown);
            setupMobileControls();
        }
        
        // 启动游戏
        init();
    </script>
</body>
</html>
```

## 2. 部署方案

### 2.1 本地运行
1. 将上述代码保存为`snake-game.html`文件
2. 直接在浏览器中打开该文件

### 2.2 使用本地Web服务器运行
创建`run-local.sh`脚本：
```bash
#!/bin/bash

# 检查是否安装了Python3
if command -v python3 &>/dev/null; then
    echo "使用Python3启动Web服务器..."
    python3 -m http.server 8000
elif command -v python &>/dev/null; then
    echo "使用Python2启动Web服务器..."
    python -m SimpleHTTPServer 8000
else
    echo "未找到Python，请直接打开snake-game.html文件"
    exit 1
fi
```

运行：
```bash
chmod +x run-local.sh
./run-local.sh
```
然后在浏览器中访问`http://localhost:8000/snake-game.html`

### 2.3 Docker部署
创建`Dockerfile`：
```dockerfile
FROM nginx:alpine
COPY snake-game.html /usr/share/nginx/html/index.html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

构建并运行：
```bash
docker build -t snake-game .
docker run -d -p 8080:80 --name snake-game-container snake-game
```
访问`http://localhost:8080`

## 3. 使用说明

### 游戏控制
- **桌面端**：使用方向键(↑ ↓ ← →)控制蛇的移动，空格键暂停/继续游戏
- **移动端**：使用屏幕上的方向按钮控制

### 游戏规则
1. 控制蛇吃到红色食物增长身体
2. 每吃一个食物得10分
3. 撞到墙壁或自身身体游戏结束
4. 分数越高蛇移动速度越快
5. 最高分会保存在浏览器本地存储中

## 4. 测试验证

游戏已经过以下测试：
1. 功能测试：游戏初始化、控制、逻辑、数据持久化
2. 用户体验测试：状态提示、分数显示、控制响应
3. 性能测试：游戏循环、长蛇性能、响应速度
4. 跨浏览器测试：Chrome、Firefox、Safari、Edge

## 5. 扩展建议

如需扩展游戏功能，可以：
1. 添加游戏难度选择
2. 实现不同蛇的外观皮肤
3. 添加游戏音效
4. 增加游戏关卡设计

## 6. 项目结构

```
snake-game/
├── snake-game.html          # 主游戏文件
├── run-local.sh             # 本地运行脚本
├── Dockerfile               # Docker构建文件
└── README.md                # 使用说明
```

## 7. 总结

这个纯前端贪吃蛇游戏具有以下特点：
- 零依赖，纯原生JavaScript实现
- 响应式设计，支持桌面和移动设备
- 完整的游戏功能：控制、计分、状态管理
- 本地存储最高分记录
- 简单易部署，多种运行方式可选

游戏可以直接保存为HTML文件运行，也可以通过Docker容器化部署，适合作为学习项目

