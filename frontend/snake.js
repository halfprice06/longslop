// Simple Snake Game
// Controls: Arrow keys
// Eat the green food, grow in length, don't hit walls or yourself.

(function() {
    let canvas, ctx;
    let snake = [];
    let direction = 'right';
    let food = null;
    let gameInterval = null;
    let gameRunning = false;
    let snakeStatusEl = null;
  
    const tileSize = 16;
    const tileCount = 20; // 320x320 with 16px tiles
  
    function initSnakeGame() {
      canvas = document.getElementById('snakeCanvas');
      ctx = canvas.getContext('2d');
      snakeStatusEl = document.getElementById('snakeStatus');
  
      resetGame();
  
      document.addEventListener('keydown', keyDown);
    }
  
    function resetGame() {
      snake = [
        {x: 2, y: 10},
        {x: 1, y: 10},
        {x: 0, y: 10}
      ];
      direction = 'right';
      placeFood();
      snakeStatusEl.textContent = "Game started. Good luck!";
      if (gameInterval) clearInterval(gameInterval);
      gameInterval = setInterval(gameLoop, 100);
      gameRunning = true;
    }
  
    function placeFood() {
      food = {
        x: Math.floor(Math.random()*tileCount),
        y: Math.floor(Math.random()*tileCount)
      };
      // Make sure food isn't placed on the snake
      while (snake.some(s => s.x === food.x && s.y === food.y)) {
        food.x = Math.floor(Math.random()*tileCount);
        food.y = Math.floor(Math.random()*tileCount);
      }
    }
  
    function gameLoop() {
      update();
      draw();
    }
  
    function update() {
      // Move snake head
      const head = { ...snake[0] };
      switch(direction) {
        case 'left': head.x -= 1; break;
        case 'up': head.y -= 1; break;
        case 'right': head.x += 1; break;
        case 'down': head.y += 1; break;
      }
  
      // Check wall collisions
      if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
        gameOver();
        return;
      }
  
      // Check self collisions
      if (snake.some(segment => segment.x === head.x && segment.y === head.y)) {
        gameOver();
        return;
      }
  
      snake.unshift(head);
  
      // Check food
      if (head.x === food.x && head.y === food.y) {
        placeFood();
        // Grow the snake by not removing the tail this turn
      } else {
        snake.pop(); // Remove tail if no food eaten
      }
    }
  
    function draw() {
      // Clear
      ctx.fillStyle = '#000000';
      ctx.fillRect(0,0,canvas.width, canvas.height);
  
      // Draw snake
      ctx.fillStyle = '#ffffff';
      snake.forEach(segment => {
        ctx.fillRect(segment.x*tileSize, segment.y*tileSize, tileSize, tileSize);
      });
  
      // Draw food
      ctx.fillStyle = '#00ff00';
      ctx.fillRect(food.x*tileSize, food.y*tileSize, tileSize, tileSize);
    }
  
    function keyDown(e) {
      if (!gameRunning) return;
      switch(e.key) {
        case 'ArrowLeft':
          if (direction !== 'right') direction = 'left';
          break;
        case 'ArrowUp':
          if (direction !== 'down') direction = 'up';
          break;
        case 'ArrowRight':
          if (direction !== 'left') direction = 'right';
          break;
        case 'ArrowDown':
          if (direction !== 'up') direction = 'down';
          break;
      }
    }
  
    function gameOver() {
      clearInterval(gameInterval);
      gameInterval = null;
      gameRunning = false;
      snakeStatusEl.textContent = "Game over! Press 'Start Snake' to play again.";
    }
  
    // Public API
    window.startSnakeGame = function() {
      if (!gameRunning) {
        resetGame();
      }
    }
  
    // Initialize on load
    document.addEventListener('DOMContentLoaded', initSnakeGame);
  })();
  