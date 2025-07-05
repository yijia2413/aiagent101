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


FROM nginx:alpine
COPY snake-game.html /usr/share/nginx/html/index.html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]


