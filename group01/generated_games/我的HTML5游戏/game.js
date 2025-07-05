// HTML5游戏主逻辑
class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.score = 0;
        this.level = 1;
        this.gameRunning = false;
        this.gamePaused = false;
        
        // 游戏对象
        this.player = {
            x: this.canvas.width / 2,
            y: this.canvas.height - 50,
            width: 30,
            height: 30,
            speed: 5,
            color: '#4ecdc4'
        };
        
        this.collectibles = [];
        this.obstacles = [];
        this.keys = {};
        
        this.init();
    }
    
    init() {
        // 事件监听
        this.setupEventListeners();
        
        // 初始化游戏对象
        this.spawnCollectibles();
        this.spawnObstacles();
        
        // 开始游戏循环
        this.gameLoop();
    }
    
    setupEventListeners() {
        // 键盘事件
        document.addEventListener('keydown', (e) => {
            this.keys[e.key] = true;
        });
        
        document.addEventListener('keyup', (e) => {
            this.keys[e.key] = false;
        });
        
        // 按钮事件
        document.getElementById('startBtn').addEventListener('click', () => {
            this.startGame();
        });
        
        document.getElementById('pauseBtn').addEventListener('click', () => {
            this.togglePause();
        });
        
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.resetGame();
        });
    }
    
    startGame() {
        this.gameRunning = true;
        this.gamePaused = false;
        document.getElementById('startBtn').textContent = '游戏进行中';
        document.getElementById('startBtn').disabled = true;
    }
    
    togglePause() {
        this.gamePaused = !this.gamePaused;
        document.getElementById('pauseBtn').textContent = this.gamePaused ? '继续' : '暂停';
    }
    
    resetGame() {
        this.score = 0;
        this.level = 1;
        this.gameRunning = false;
        this.gamePaused = false;
        this.player.x = this.canvas.width / 2;
        this.player.y = this.canvas.height - 50;
        this.collectibles = [];
        this.obstacles = [];
        
        this.spawnCollectibles();
        this.spawnObstacles();
        
        document.getElementById('startBtn').textContent = '开始游戏';
        document.getElementById('startBtn').disabled = false;
        document.getElementById('pauseBtn').textContent = '暂停';
        
        this.updateUI();
    }
    
    spawnCollectibles() {
        for (let i = 0; i < 5; i++) {
            this.collectibles.push({
                x: Math.random() * (this.canvas.width - 20),
                y: Math.random() * (this.canvas.height - 100),
                width: 20,
                height: 20,
                color: '#ffd93d',
                collected: false
            });
        }
    }
    
    spawnObstacles() {
        for (let i = 0; i < 3; i++) {
            this.obstacles.push({
                x: Math.random() * (this.canvas.width - 30),
                y: Math.random() * (this.canvas.height - 100),
                width: 30,
                height: 30,
                color: '#ff6b6b',
                speedX: (Math.random() - 0.5) * 4,
                speedY: (Math.random() - 0.5) * 4
            });
        }
    }
    
    update() {
        if (!this.gameRunning || this.gamePaused) return;
        
        // 更新玩家位置
        this.updatePlayer();
        
        // 更新障碍物
        this.updateObstacles();
        
        // 检测碰撞
        this.checkCollisions();
        
        // 更新UI
        this.updateUI();
    }
    
    updatePlayer() {
        // 移动玩家
        if (this.keys['ArrowLeft'] || this.keys['a'] || this.keys['A']) {
            this.player.x -= this.player.speed;
        }
        if (this.keys['ArrowRight'] || this.keys['d'] || this.keys['D']) {
            this.player.x += this.player.speed;
        }
        if (this.keys['ArrowUp'] || this.keys['w'] || this.keys['W']) {
            this.player.y -= this.player.speed;
        }
        if (this.keys['ArrowDown'] || this.keys['s'] || this.keys['S']) {
            this.player.y += this.player.speed;
        }
        
        // 边界检测
        this.player.x = Math.max(0, Math.min(this.canvas.width - this.player.width, this.player.x));
        this.player.y = Math.max(0, Math.min(this.canvas.height - this.player.height, this.player.y));
    }
    
    updateObstacles() {
        this.obstacles.forEach(obstacle => {
            obstacle.x += obstacle.speedX;
            obstacle.y += obstacle.speedY;
            
            // 边界反弹
            if (obstacle.x <= 0 || obstacle.x >= this.canvas.width - obstacle.width) {
                obstacle.speedX *= -1;
            }
            if (obstacle.y <= 0 || obstacle.y >= this.canvas.height - obstacle.height) {
                obstacle.speedY *= -1;
            }
        });
    }
    
    checkCollisions() {
        // 检测收集道具
        this.collectibles.forEach(collectible => {
            if (!collectible.collected && this.isColliding(this.player, collectible)) {
                collectible.collected = true;
                this.score += 10;
                this.level = Math.floor(this.score / 50) + 1;
            }
        });
        
        // 检测障碍物碰撞
        this.obstacles.forEach(obstacle => {
            if (this.isColliding(this.player, obstacle)) {
                this.gameOver();
            }
        });
    }
    
    isColliding(rect1, rect2) {
        return rect1.x < rect2.x + rect2.width &&
               rect1.x + rect1.width > rect2.x &&
               rect1.y < rect2.y + rect2.height &&
               rect1.y + rect1.height > rect2.y;
    }
    
    gameOver() {
        this.gameRunning = false;
        alert(`游戏结束！最终得分：${this.score}`);
        this.resetGame();
    }
    
    updateUI() {
        document.getElementById('score').textContent = this.score;
        document.getElementById('level').textContent = this.level;
    }
    
    draw() {
        // 清空画布
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制玩家
        this.ctx.fillStyle = this.player.color;
        this.ctx.fillRect(this.player.x, this.player.y, this.player.width, this.player.height);
        
        // 绘制收集道具
        this.collectibles.forEach(collectible => {
            if (!collectible.collected) {
                this.ctx.fillStyle = collectible.color;
                this.ctx.fillRect(collectible.x, collectible.y, collectible.width, collectible.height);
            }
        });
        
        // 绘制障碍物
        this.obstacles.forEach(obstacle => {
            this.ctx.fillStyle = obstacle.color;
            this.ctx.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);
        });
        
        // 绘制游戏状态
        if (!this.gameRunning) {
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.fillStyle = 'white';
            this.ctx.font = '48px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('点击开始游戏', this.canvas.width / 2, this.canvas.height / 2);
        }
        
        if (this.gamePaused) {
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.fillStyle = 'white';
            this.ctx.font = '36px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('游戏暂停', this.canvas.width / 2, this.canvas.height / 2);
        }
    }
    
    gameLoop() {
        this.update();
        this.draw();
        requestAnimationFrame(() => this.gameLoop());
    }
}

// 初始化游戏
document.addEventListener('DOMContentLoaded', () => {
    new Game();
});