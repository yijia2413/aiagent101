describe('游戏初始化测试', () => {
  beforeAll(() => {
    // 初始化游戏
    initGame();
  });
  
  test('游戏画布应正确初始化', () => {
    expect(canvas.width).toBe(400);
    expect(canvas.height).toBe(400);
  });
  
  test('蛇应正确初始化', () => {
    expect(snake.length).toBe(3);
    // 检查蛇的初始位置
    const startX = Math.floor(GRID_SIZE / 4);
    const startY = Math.floor(GRID_SIZE / 2);
    expect(snake[0]).toEqual({ x: startX, y: startY });
    expect(snake[1]).toEqual({ x: startX - 1, y: startY });
    expect(snake[2]).toEqual({ x: startX - 2, y: startY });
  });
  
  test('食物应正确生成且不在蛇身上', () => {
    expect(food).toHaveProperty('x');
    expect(food).toHaveProperty('y');
    expect(food.x).toBeGreaterThanOrEqual(0);
    expect(food.x).toBeLessThan(GRID_SIZE);
    expect(food.y).toBeGreaterThanOrEqual(0);
    expect(food.y).toBeLessThan(GRID_SIZE);
    
    // 确保食物不在蛇身上
    const foodOnSnake = snake.some(segment => 
      segment.x === food.x && segment.y === food.y
    );
    expect(foodOnSnake).toBe(false);
  });
  
  test('分数应初始化为0', () => {
    expect(score).toBe(0);
    expect(document.getElementById('current-score').textContent).toBe('0');
  });
  
  test('游戏状态应为READY', () => {
    expect(gameState).toBe(GAME_STATES.READY);
  });
});


describe('游戏控制测试', () => {
  beforeEach(() => {
    initGame();
    gameState = GAME_STATES.PLAYING;
  });
  
  test('方向键应改变蛇的移动方向', () => {
    // 初始方向向右
    expect(direction).toEqual(DIRECTIONS.RIGHT);
    
    // 模拟按下上箭头
    const upEvent = new KeyboardEvent('keydown', { key: 'ArrowUp' });
    document.dispatchEvent(upEvent);
    expect(nextDirection).toEqual(DIRECTIONS.UP);
    
    // 模拟按下左箭头
    const leftEvent = new KeyboardEvent('keydown', { key: 'ArrowLeft' });
    document.dispatchEvent(leftEvent);
    expect(nextDirection).toEqual(DIRECTIONS.LEFT);
    
    // 不能直接反向移动
    const downEvent = new KeyboardEvent('keydown', { key: 'ArrowDown' });
    document.dispatchEvent(downEvent);
    expect(nextDirection).not.toEqual(DIRECTIONS.DOWN);
  });
  
  test('空格键应暂停/继续游戏', () => {
    // 开始游戏
    gameState = GAME_STATES.PLAYING;
    const pauseEvent = new KeyboardEvent('keydown', { key: ' ' });
    document.dispatchEvent(pauseEvent);
    expect(gameState).toBe(GAME_STATES.PAUSED);
    
    // 继续游戏
    document.dispatchEvent(pauseEvent);
    expect(gameState).toBe(GAME_STATES.PLAYING);
  });
  
  test('移动端按钮应改变方向', () => {
    // 模拟点击上按钮
    const upBtn = document.querySelector('.mobile-btn.up');
    upBtn.click();
    expect(nextDirection).toEqual(DIRECTIONS.UP);
    
    // 模拟点击左按钮
    const leftBtn = document.querySelector('.mobile-btn.left');
    leftBtn.click();
    expect(nextDirection).toEqual(DIRECTIONS.LEFT);
  });
});


describe('游戏逻辑测试', () => {
  beforeEach(() => {
    initGame();
    gameState = GAME_STATES.PLAYING;
  });
  
  test('蛇应正确移动', () => {
    const initialHead = { ...snake[0] };
    gameUpdate();
    
    // 检查蛇头是否移动
    expect(snake[0].x).toBe(initialHead.x + 1); // 初始方向向右
    expect(snake[0].y).toBe(initialHead.y);
    
    // 检查蛇身是否跟随
    expect(snake[1]).toEqual(initialHead);
  });
  
  test('吃到食物应增加长度和分数', () => {
    // 将食物放在蛇头前方
    food = { x: snake[0].x + 1, y: snake[0].y };
    const initialLength = snake.length;
    const initialScore = score;
    
    gameUpdate();
    
    expect(snake.length).toBe(initialLength + 1);
    expect(score).toBe(initialScore + 10);
    expect(document.getElementById('current-score').textContent).toBe((initialScore + 10).toString());
  });
  
  test('撞墙应结束游戏', () => {
    // 将蛇头移到墙边
    snake[0] = { x: 0, y: 0 };
    direction = DIRECTIONS.LEFT;
    nextDirection = DIRECTIONS.LEFT;
    
    gameUpdate();
    
    expect(gameState).toBe(GAME_STATES.GAME_OVER);
  });
  
  test('撞自身应结束游戏', () => {
    // 将蛇头移到蛇身上
    snake.unshift({ x: snake[1].x, y: snake[1].y });
    
    gameUpdate();
    
    expect(gameState).toBe(GAME_STATES.GAME_OVER);
  });
  
  test('游戏速度应随分数增加', () => {
    const initialSpeed = gameSpeed;
    score = 50; // 触发速度增加条件
    
    // 吃到食物
    food = { x: snake[0].x + 1, y: snake[0].y };
    gameUpdate();
    
    expect(gameSpeed).toBe(initialSpeed - 5);
  });
});


describe('数据持久化测试', () => {
  beforeEach(() => {
    // 清除localStorage
    localStorage.clear();
    initGame();
  });
  
  test('应正确保存和读取最高分', () => {
    // 模拟打破记录
    score = 100;
    highScore = 50;
    gameOver();
    
    expect(localStorage.getItem('snakeHighScore')).toBe('100');
    expect(highScore).toBe(100);
    expect(document.getElementById('high-score').textContent).toBe('100');
    
    // 重新初始化游戏
    initGame();
    expect(highScore).toBe(100);
    expect(document.getElementById('high-score').textContent).toBe('100');
  });
  
  test('未打破记录不应保存', () => {
    score = 30;
    highScore = 50;
    gameOver();
    
    expect(localStorage.getItem('snakeHighScore')).toBe(null);
    expect(highScore).toBe(50);
  });
});


describe('用户体验测试', () => {
  beforeEach(() => {
    initGame();
  });
  
  test('游戏状态提示应正确显示', () => {
    expect(gameStatusEl.textContent).toBe('按方向键开始游戏');
    
    // 开始游戏
    gameState = GAME_STATES.PLAYING;
    gameUpdate();
    expect(gameStatusEl.textContent).toBe('游戏中...');
    
    // 暂停游戏
    gameState = GAME_STATES.PAUSED;
    pauseGame();
    expect(gameStatusEl.textContent).toContain('游戏已暂停');
    
    // 游戏结束
    gameState = GAME_STATES.GAME_OVER;
    score = 50;
    highScore = 40;
    gameOver();
    expect(gameStatusEl.textContent).toContain('新纪录');
    expect(gameStatusEl.textContent).toContain('50分');
  });
  
  test('分数显示应实时更新', () => {
    score = 30;
    currentScoreEl.textContent = score;
    expect(document.getElementById('current-score').textContent).toBe('30');
    
    highScore = 50;
    highScoreEl.textContent = highScore;
    expect(document.getElementById('high-score').textContent).toBe('50');
  });
  
  test('移动端控制按钮应可见', () => {
    // 模拟移动端视图
    window.innerWidth = 400;
    const resizeEvent = new Event('resize');
    window.dispatchEvent(resizeEvent);
    
    const mobileControls = document.querySelector('.mobile-controls');
    expect(window.getComputedStyle(mobileControls).display).not.toBe('none');
  });
});


describe('性能测试', () => {
  test('游戏更新应在合理时间内完成', () => {
    initGame();
    gameState = GAME_STATES.PLAYING;
    
    const startTime = performance.now();
    for (let i = 0; i < 100; i++) {
      gameUpdate();
    }
    const endTime = performance.now();
    const averageTime = (endTime - startTime) / 100;
    
    expect(averageTime).toBeLessThan(2); // 平均每次更新应小于2ms
  });
  
  test('长蛇时游戏仍应流畅', () => {
    initGame();
    gameState = GAME_STATES.PLAYING;
    
    // 创建长蛇
    snake = [];
    for (let i = 0; i < 100; i++) {
      snake.push({ x: i, y: 0 });
    }
    
    const startTime = performance.now();
    gameUpdate();
    const endTime = performance.now();
    
    expect(endTime - startTime).toBeLessThan(10); // 更新应小于10ms
  });
  
  test('方向改变应即时响应', () => {
    initGame();
    gameState = GAME_STATES.PLAYING;
    
    const startTime = performance.now();
    const event = new KeyboardEvent('keydown', { key: 'ArrowUp' });
    document.dispatchEvent(event);
    const endTime = performance.now();
    
    expect(endTime - startTime).toBeLessThan(50); // 响应时间应小于50ms
    expect(nextDirection).toEqual(DIRECTIONS.UP);
  });
});


