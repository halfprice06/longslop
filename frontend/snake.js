document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('snakeCanvas');
    const ctx = canvas.getContext('2d');

    const gridSize = 20;       // Size of each cell
    const tileCount = 30;      // 30x30 grid on 600x600 canvas
    let xVelocity = 0;
    let yVelocity = 0;

    let snakeX = 15; 
    let snakeY = 15;
    const snakeTrail = [];
    let snakeLength = 5;

    let appleX = 20;
    let appleY = 20;

    let paused = false;
    let score = 0;
    let glitchLevel = 0;
    let moveInterval = 100; // ms
    let baseMoveInterval = 100;

    // Sloppiness variables
    let invertedControls = false;
    let invertDuration = 0;
    let obstacles = [];
    let glitchCountdown = 0;
    let powerUpX = -1;
    let powerUpY = -1;
    let powerUpActive = false;
    let powerUpEndTime = 0;

    function maybeAddObstacles() {
        const obstacleCount = Math.min(glitchLevel, 5);
        obstacles = [];
        for (let i = 0; i < obstacleCount; i++) {
            const ox = Math.floor(Math.random() * tileCount);
            const oy = Math.floor(Math.random() * tileCount);
            if ((ox === snakeX && oy === snakeY) || (ox === appleX && oy === appleY)) {
                i--;
                continue;
            }
            obstacles.push({x: ox, y: oy});
        }
    }

    function placePowerUp() {
        // 10% chance after eating apple if glitch level > 1
        if (glitchLevel > 1 && Math.random() < 0.1) {
            powerUpX = Math.floor(Math.random() * tileCount);
            powerUpY = Math.floor(Math.random() * tileCount);
        }
    }

    function updateGame() {
        if (!paused) {
            if (invertDuration > 0) {
                invertDuration--;
                if (invertDuration === 0) {
                    invertedControls = false;
                }
            }

            // Handle power-up effect
            if (powerUpActive && Date.now() > powerUpEndTime) {
                // End power-up
                powerUpActive = false;
                moveInterval = baseMoveInterval;
                clearInterval(gameLoop);
                gameLoop = setInterval(updateGame, moveInterval);
            }

            snakeX += xVelocity;
            snakeY += yVelocity;

            if (snakeX < 0) snakeX = tileCount - 1;
            if (snakeX > tileCount - 1) snakeX = 0;
            if (snakeY < 0) snakeY = tileCount - 1;
            if (snakeY > tileCount - 1) snakeY = 0;

            snakeTrail.push({x: snakeX, y: snakeY});
            while (snakeTrail.length > snakeLength) {
                snakeTrail.shift();
            }

            // Self-collision
            for (let i = 0; i < snakeTrail.length - 1; i++) {
                if (snakeTrail[i].x === snakeX && snakeTrail[i].y === snakeY) {
                    resetGame();
                }
            }

            // Obstacle collision
            for (const obs of obstacles) {
                if (obs.x === snakeX && obs.y === snakeY) {
                    resetGame();
                }
            }

            // Apple collision
            if (appleX === snakeX && appleY === snakeY) {
                snakeLength++;
                score++;
                glitchLevel++;
                appleX = Math.floor(Math.random() * tileCount);
                appleY = Math.floor(Math.random() * tileCount);

                if (glitchLevel > 2) {
                    maybeAddObstacles();
                }

                const glitchChance = Math.min(glitchLevel * 5, 50);
                if (Math.random() * 100 < glitchChance) {
                    applyRandomGlitch();
                }

                // Place power-up
                placePowerUp();
            }

            // Power-up collision
            if (powerUpX === snakeX && powerUpY === snakeY && powerUpX !== -1) {
                score += 5;
                powerUpActive = true;
                powerUpX = -1;
                powerUpY = -1;
                // Speed up snake temporarily
                moveInterval = 50;
                clearInterval(gameLoop);
                gameLoop = setInterval(updateGame, moveInterval);
                powerUpEndTime = Date.now() + 5000; // 5 seconds
            }
        }

        drawGame();
    }

    function applyRandomGlitch() {
        const effect = Math.floor(Math.random() * 3);
        if (effect === 0) {
            invertedControls = true;
            invertDuration = 50;
        } else if (effect === 1) {
            snakeX = Math.floor(Math.random() * tileCount);
            snakeY = Math.floor(Math.random() * tileCount);
            snakeTrail.length = 0;
            for (let i = 0; i < snakeLength; i++) {
                snakeTrail.push({x: snakeX, y: snakeY});
            }
        } else {
            glitchCountdown = 10;
        }
    }

    function resetGame() {
        snakeLength = 5;
        xVelocity = 0;
        yVelocity = 0;
        score = 0;
        glitchLevel = 0;
        obstacles = [];
        invertedControls = false;
        invertDuration = 0;
        powerUpX = -1;
        powerUpY = -1;
        powerUpActive = false;
        moveInterval = baseMoveInterval;
        clearInterval(gameLoop);
        gameLoop = setInterval(updateGame, moveInterval);

        snakeX = 15;
        snakeY = 15;
        snakeTrail.length = 0;
        for (let i = 0; i < snakeLength; i++) {
            snakeTrail.push({x: snakeX, y: snakeY});
        }
    }

    function drawGame() {
        ctx.fillStyle = 'black';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Glitch visuals
        if (glitchCountdown > 0) {
            glitchCountdown--;
            for (let i = 0; i < 5; i++) {
                const gx = Math.random() * canvas.width;
                const gy = Math.random() * canvas.height;
                const gx2 = Math.random() * canvas.width;
                const gy2 = Math.random() * canvas.height;
                ctx.strokeStyle = i % 2 === 0 ? '#00ff00' : '#ff00ff';
                ctx.beginPath();
                ctx.moveTo(gx, gy);
                ctx.lineTo(gx2, gy2);
                ctx.stroke();
            }
        }

        // Apple
        ctx.fillStyle = '#00ff00';
        ctx.fillRect(appleX * gridSize, appleY * gridSize, gridSize - 2, gridSize - 2);

        // Power-up (yellow)
        if (powerUpX !== -1 && powerUpY !== -1) {
            ctx.fillStyle = '#ffff00';
            ctx.fillRect(powerUpX * gridSize, powerUpY * gridSize, gridSize - 2, gridSize - 2);
        }

        // Obstacles
        ctx.fillStyle = '#ff0000';
        for (const obs of obstacles) {
            ctx.fillRect(obs.x * gridSize, obs.y * gridSize, gridSize - 2, gridSize - 2);
        }

        // Snake
        ctx.fillStyle = '#ffffff';
        for (let i = 0; i < snakeTrail.length; i++) {
            ctx.fillRect(snakeTrail[i].x * gridSize, snakeTrail[i].y * gridSize, gridSize - 2, gridSize - 2);
        }

        // Score and glitch
        ctx.fillStyle = '#00ff00';
        ctx.font = '10px "Press Start 2P"';
        ctx.fillText('Score: ' + score, 10, 10);
        ctx.fillText('Glitch: ' + glitchLevel, 10, 20);
        if (invertedControls) {
            ctx.fillText('INVERTED!', 10, 30);
        }
        if (powerUpActive) {
            ctx.fillText('POWER-UP!', 10, 40);
        }
    }

    let gameLoop = setInterval(updateGame, moveInterval);

    document.addEventListener('keydown', (e) => {
        if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(e.key)) {
            e.preventDefault();
        }
        let key = e.key;
        if (invertedControls) {
            if (key === 'ArrowUp') key = 'ArrowDown';
            else if (key === 'ArrowDown') key = 'ArrowUp';
            else if (key === 'ArrowLeft') key = 'ArrowRight';
            else if (key === 'ArrowRight') key = 'ArrowLeft';
        }

        switch(key) {
            case 'ArrowLeft':
                if (xVelocity !== 1) {xVelocity = -1; yVelocity = 0;}
                break;
            case 'ArrowUp':
                if (yVelocity !== 1) {yVelocity = -1; xVelocity = 0;}
                break;
            case 'ArrowRight':
                if (xVelocity !== -1) {xVelocity = 1; yVelocity = 0;}
                break;
            case 'ArrowDown':
                if (yVelocity !== -1) {yVelocity = 1; xVelocity = 0;}
                break;
            case ' ':
                paused = !paused;
                break;
        }
    });
});
