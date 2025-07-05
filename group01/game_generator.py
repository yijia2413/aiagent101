import os
import json
from typing import Dict, Any, List

class HTML5GameGenerator:
    def __init__(self):
        """初始化HTML5游戏生成器"""
        self.games_dir = "generated_games"
        self.ensure_games_directory()
        
    def ensure_games_directory(self):
        """确保游戏目录存在"""
        if not os.path.exists(self.games_dir):
            os.makedirs(self.games_dir)
            
    def generate_game_from_discussion(self, discussion_messages: List[Dict], game_name: str):
        """根据团队讨论生成HTML5游戏"""
        
        # 分析讨论内容，提取游戏信息
        game_info = self.extract_game_info(discussion_messages)
        
        # 生成游戏文件
        game_files = self.create_game_files(game_info, game_name)
        
        return game_files
        
    def extract_game_info(self, messages: List[Dict]) -> Dict[str, Any]:
        """从讨论中提取游戏信息"""
        game_info = {
            "name": "HTML5小游戏",
            "type": "simple_game",
            "description": "基于团队讨论生成的HTML5小游戏",
            "features": [],
            "target_audience": "所有用户",
            "platform": "Web浏览器"
        }
        
        # 分析消息内容，提取关键信息
        for message in messages:
            content = message.get("content", "")
            if "游戏类型" in content or "游戏玩法" in content:
                # 提取游戏类型信息
                pass
            if "功能" in content or "特性" in content:
                # 提取功能特性
                pass
                
        return game_info
        
    def create_game_files(self, game_info: Dict[str, Any], game_name: str) -> Dict[str, str]:
        """创建游戏文件"""
        
        # 生成HTML文件
        html_content = self.generate_html(game_info, game_name)
        
        # 生成CSS文件
        css_content = self.generate_css(game_info)
        
        # 生成JavaScript文件
        js_content = self.generate_javascript(game_info)
        
        # 保存文件
        game_dir = os.path.join(self.games_dir, game_name)
        if not os.path.exists(game_dir):
            os.makedirs(game_dir)
            
        files = {}
        
        # HTML文件
        html_file = os.path.join(game_dir, "index.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        files["html"] = html_file
        
        # CSS文件
        css_file = os.path.join(game_dir, "style.css")
        with open(css_file, "w", encoding="utf-8") as f:
            f.write(css_content)
        files["css"] = css_file
        
        # JavaScript文件
        js_file = os.path.join(game_dir, "game.js")
        with open(js_file, "w", encoding="utf-8") as f:
            f.write(js_content)
        files["js"] = js_file
        
        return files
        
    def generate_html(self, game_info: Dict[str, Any], game_name: str) -> str:
        """生成HTML文件"""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{game_name}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="game-container">
        <header class="game-header">
            <h1>{game_name}</h1>
            <div class="game-info">
                <span class="score">得分: <span id="score">0</span></span>
                <span class="level">等级: <span id="level">1</span></span>
            </div>
        </header>
        
        <main class="game-main">
            <canvas id="gameCanvas" width="800" height="600"></canvas>
            
            <div class="game-controls">
                <button id="startBtn" class="btn">开始游戏</button>
                <button id="pauseBtn" class="btn">暂停</button>
                <button id="resetBtn" class="btn">重新开始</button>
            </div>
            
            <div class="game-instructions">
                <h3>游戏说明</h3>
                <p>使用方向键或WASD控制角色移动</p>
                <p>收集道具获得分数</p>
                <p>避免障碍物</p>
            </div>
        </main>
        
        <footer class="game-footer">
            <p>由AutoGen多Agent团队开发</p>
        </footer>
    </div>
    
    <script src="game.js"></script>
</body>
</html>"""
        
    def generate_css(self, game_info: Dict[str, Any]) -> str:
        """生成CSS文件"""
        return """/* 游戏样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

.game-container {
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    overflow: hidden;
    max-width: 900px;
    width: 100%;
}

.game-header {
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
    color: white;
    padding: 20px;
    text-align: center;
}

.game-header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.game-info {
    display: flex;
    justify-content: space-around;
    font-size: 1.2em;
    font-weight: bold;
}

.game-main {
    padding: 20px;
    text-align: center;
}

#gameCanvas {
    border: 3px solid #333;
    border-radius: 10px;
    background: #f0f0f0;
    margin-bottom: 20px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.game-controls {
    margin-bottom: 20px;
}

.btn {
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    border: none;
    padding: 12px 24px;
    margin: 0 10px;
    border-radius: 25px;
    font-size: 1em;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.3);
}

.btn:active {
    transform: translateY(0);
}

.game-instructions {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    margin-top: 20px;
}

.game-instructions h3 {
    color: #333;
    margin-bottom: 10px;
}

.game-instructions p {
    color: #666;
    margin-bottom: 5px;
}

.game-footer {
    background: #333;
    color: white;
    text-align: center;
    padding: 15px;
    font-size: 0.9em;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .game-container {
        margin: 10px;
        border-radius: 15px;
    }
    
    .game-header h1 {
        font-size: 2em;
    }
    
    #gameCanvas {
        width: 100%;
        height: auto;
        max-width: 400px;
    }
    
    .btn {
        margin: 5px;
        padding: 10px 20px;
    }
}"""
        
    def generate_javascript(self, game_info: Dict[str, Any]) -> str:
        """生成JavaScript文件"""
        return """// HTML5游戏主逻辑
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
});""" 