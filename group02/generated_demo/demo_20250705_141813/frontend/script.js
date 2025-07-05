
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
    