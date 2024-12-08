document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('glitchoutCanvas');
    const ctx = canvas.getContext('2d');

    let paddleX = canvas.width / 2 - 40;
    const paddleWidth = 80;
    const paddleHeight = 10;
    let paddleSpeed = 5;

    let ballX = canvas.width / 2;
    let ballY = canvas.height - 30;
    let ballSpeedX = 3;
    let ballSpeedY = -3;
    const ballRadius = 5;

    let bricks = [];
    const brickRowCount = 5;
    const brickColumnCount = 10;
    const brickWidth = 50;
    const brickHeight = 15;
    const brickPadding = 5;
    const brickOffsetTop = 30;
    const brickOffsetLeft = 30;

    let rightPressed = false;
    let leftPressed = false;
    let spacePressed = false;
    let started = false;

    let score = 0;
    let glitchChance = 0;

    function resetBricks() {
        bricks = [];
        for (let c = 0; c < brickColumnCount; c++) {
            bricks[c] = [];
            for (let r = 0; r < brickRowCount; r++) {
                bricks[c][r] = { x:0, y:0, status:1 };
            }
        }
    }
    resetBricks();

    function drawBall() {
        ctx.beginPath();
        ctx.arc(ballX, ballY, ballRadius, 0, Math.PI*2);
        ctx.fillStyle = "#ffffff";
        ctx.fill();
        ctx.closePath();
    }

    function drawPaddle() {
        ctx.beginPath();
        ctx.rect(paddleX, canvas.height - paddleHeight - 10, paddleWidth, paddleHeight);
        ctx.fillStyle = "#00ff00";
        ctx.fill();
        ctx.closePath();
    }

    function drawBricks() {
        for (let c=0; c<brickColumnCount; c++) {
            for (let r=0; r<brickRowCount; r++) {
                if (bricks[c][r].status == 1) {
                    const brickX = (c*(brickWidth+brickPadding))+brickOffsetLeft;
                    const brickY = (r*(brickHeight+brickPadding))+brickOffsetTop;
                    bricks[c][r].x = brickX;
                    bricks[c][r].y = brickY;
                    ctx.beginPath();
                    ctx.rect(brickX, brickY, brickWidth, brickHeight);
                    // Slight glitch effect: alternate colors randomly
                    ctx.fillStyle = Math.random()<0.1?'#ff00ff':'#00ff00';
                    ctx.fill();
                    ctx.closePath();
                }
            }
        }
    }

    function detectCollision() {
        for (let c=0; c<brickColumnCount; c++) {
            for (let r=0; r<brickRowCount; r++) {
                const b = bricks[c][r];
                if (b.status == 1) {
                    if (ballX > b.x && ballX < b.x+brickWidth && ballY > b.y && ballY < b.y+brickHeight) {
                        ballSpeedY = -ballSpeedY;
                        b.status = 0;
                        score++;
                        glitchChance = score * 2; 
                        if (Math.random()*100 < glitchChance) {
                            applyGlitch();
                        }
                        // Win condition
                        if (score == brickRowCount*brickColumnCount) {
                            // Reset
                            resetGame();
                        }
                    }
                }
            }
        }
    }

    function applyGlitch() {
        // Glitch: random paddle position or change ball speed
        const effect = Math.floor(Math.random()*3);
        if (effect === 0) {
            paddleX = Math.random()*(canvas.width - paddleWidth);
        } else if (effect === 1) {
            ballSpeedX *= (Math.random()<0.5)?1.5:0.5;
            ballSpeedY *= (Math.random()<0.5)?1.5:0.5;
        } else {
            // Random lines on screen
            for (let i=0; i<5; i++) {
                const gx = Math.random()*canvas.width;
                const gy = Math.random()*canvas.height;
                const gx2 = Math.random()*canvas.width;
                const gy2 = Math.random()*canvas.height;
                ctx.strokeStyle = i%2===0?'#ff00ff':'#00ff00';
                ctx.beginPath();
                ctx.moveTo(gx, gy);
                ctx.lineTo(gx2, gy2);
                ctx.stroke();
            }
        }
    }

    function drawScore() {
        ctx.font = '10px "Press Start 2P"';
        ctx.fillStyle = '#00ff00';
        ctx.fillText("Score: "+score, 10, 10);
    }

    function resetGame() {
        score = 0;
        glitchChance = 0;
        started = false;
        ballX = canvas.width/2;
        ballY = canvas.height-30;
        ballSpeedX = 3;
        ballSpeedY = -3;
        paddleX = (canvas.width - paddleWidth)/2;
        resetBricks();
    }

    function draw() {
        ctx.clearRect(0,0,canvas.width,canvas.height);

        drawBricks();
        drawBall();
        drawPaddle();
        drawScore();

        if (started) {
            ballX += ballSpeedX;
            ballY += ballSpeedY;

            // Wall collision
            if (ballX + ballSpeedX > canvas.width - ballRadius || ballX + ballSpeedX < ballRadius) {
                ballSpeedX = -ballSpeedX;
            }
            if (ballY + ballSpeedY < ballRadius) {
                ballSpeedY = -ballSpeedY;
            } else if (ballY + ballSpeedY > canvas.height - ballRadius - paddleHeight - 10) {
                if (ballX > paddleX && ballX < paddleX + paddleWidth) {
                    ballSpeedY = -ballSpeedY;
                } else if (ballY > canvas.height - ballRadius) {
                    resetGame();
                }
            }
            detectCollision();
        }

        if (rightPressed && paddleX < canvas.width - paddleWidth) {
            paddleX += paddleSpeed;
        }
        if (leftPressed && paddleX > 0) {
            paddleX -= paddleSpeed;
        }

        requestAnimationFrame(draw);
    }

    draw();

    document.addEventListener("keydown", keyDownHandler, false);
    document.addEventListener("keyup", keyUpHandler, false);

    function keyDownHandler(e) {
        if (['ArrowLeft','ArrowRight',' '].includes(e.key)) {
            e.preventDefault();
        }
        if(e.key === "ArrowRight") {
            rightPressed = true;
        } else if(e.key === "ArrowLeft") {
            leftPressed = true;
        } else if(e.key === " ") {
            if (!started) {
                started = true;
            }
        }
    }
    function keyUpHandler(e) {
        if(e.key === "ArrowRight") {
            rightPressed = false;
        } else if(e.key === "ArrowLeft") {
            leftPressed = false;
        }
    }
});
