from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
import time
from typing import Dict, Any, Optional
import uuid
from maya_integration import maya_service

app = FastAPI(title="Maya AI Game Creation API", version="1.0.0")

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"],  # Vite and common React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store for conversation persistence
# In production, this should be Redis or a database
session_store: Dict[str, Dict[str, Any]] = {}

class GameRequest(BaseModel):
    prompt: str
    session_id: str = None

class ChatMessage(BaseModel):
    prompt: str
    session_id: str = None
    user_id: str = "default_user"

# Mock game templates for quick generation
GAME_TEMPLATES = {
    "breakout": {
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Breakout Game</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #0f172a, #1e293b);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Courier New', monospace;
        }
        canvas {
            border: 2px solid #00ffff;
            border-radius: 10px;
            box-shadow: 0 0 20px #00ffff;
        }
        .game-container {
            text-align: center;
        }
        .title {
            color: #00ffff;
            font-size: 2rem;
            margin-bottom: 20px;
            text-shadow: 0 0 10px #00ffff;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <h1 class="title">MAYA BREAKOUT</h1>
        <canvas id="gameCanvas" width="800" height="400"></canvas>
        <p style="color: #64748b; margin-top: 10px;">Move: ← → arrows | Start: Spacebar</p>
    </div>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        // Game variables
        const paddle = { x: 350, y: 370, width: 100, height: 10, speed: 8 };
        const ball = { x: 400, y: 200, radius: 8, dx: 4, dy: -4 };
        const bricks = [];
        
        // Create bricks
        for (let row = 0; row < 5; row++) {
            for (let col = 0; col < 10; col++) {
                bricks.push({
                    x: col * 80 + 10,
                    y: row * 30 + 30,
                    width: 70,
                    height: 20,
                    visible: true
                });
            }
        }

        // Game loop
        function gameLoop() {
            // Clear canvas
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw paddle
            ctx.fillStyle = '#00ffff';
            ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);

            // Draw ball
            ctx.beginPath();
            ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
            ctx.fillStyle = '#8b5cf6';
            ctx.fill();

            // Draw bricks
            bricks.forEach(brick => {
                if (brick.visible) {
                    ctx.fillStyle = '#10b981';
                    ctx.fillRect(brick.x, brick.y, brick.width, brick.height);
                }
            });

            // Ball movement
            ball.x += ball.dx;
            ball.y += ball.dy;

            // Ball collision with walls
            if (ball.x + ball.radius > canvas.width || ball.x - ball.radius < 0) {
                ball.dx = -ball.dx;
            }
            if (ball.y - ball.radius < 0) {
                ball.dy = -ball.dy;
            }

            // Ball collision with paddle
            if (ball.y + ball.radius > paddle.y && 
                ball.x > paddle.x && 
                ball.x < paddle.x + paddle.width) {
                ball.dy = -ball.dy;
            }

            // Ball collision with bricks
            bricks.forEach(brick => {
                if (brick.visible &&
                    ball.x > brick.x && ball.x < brick.x + brick.width &&
                    ball.y > brick.y && ball.y < brick.y + brick.height) {
                    brick.visible = false;
                    ball.dy = -ball.dy;
                }
            });

            // Reset if ball goes off bottom
            if (ball.y > canvas.height) {
                ball.x = 400;
                ball.y = 200;
                ball.dx = 4;
                ball.dy = -4;
            }

            requestAnimationFrame(gameLoop);
        }

        // Controls
        const keys = {};
        document.addEventListener('keydown', (e) => keys[e.key] = true);
        document.addEventListener('keyup', (e) => keys[e.key] = false);

        // Update paddle
        function updatePaddle() {
            if (keys['ArrowLeft'] && paddle.x > 0) paddle.x -= paddle.speed;
            if (keys['ArrowRight'] && paddle.x < canvas.width - paddle.width) paddle.x += paddle.speed;
            requestAnimationFrame(updatePaddle);
        }

        // Start game
        gameLoop();
        updatePaddle();
    </script>
</body>
</html>""",
        "description": "A classic breakout game with a cyberpunk aesthetic. Use arrow keys to move the paddle and destroy all the bricks!"
    },
    "memory": {
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Memory Game</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: #e2e8f0;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .title {
            font-size: 2.5rem;
            color: #00ffff;
            text-shadow: 0 0 20px #00ffff;
            margin-bottom: 20px;
        }
        .game-board {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 30px 0;
        }
        .card {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #1e293b, #334155);
            border: 2px solid #00ffff;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .card:hover {
            transform: scale(1.05);
            box-shadow: 0 0 15px #00ffff;
        }
        .card.flipped {
            background: linear-gradient(135deg, #8b5cf6, #a855f7);
            border-color: #8b5cf6;
        }
        .card.matched {
            background: linear-gradient(135deg, #10b981, #059669);
            border-color: #10b981;
        }
        .stats {
            display: flex;
            gap: 30px;
            margin: 20px 0;
        }
        .stat {
            text-align: center;
        }
        .stat-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #00ffff;
        }
        .stat-label {
            font-size: 0.9rem;
            color: #64748b;
        }
    </style>
</head>
<body>
    <h1 class="title">MEMORY MATRIX</h1>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-value" id="moves">0</div>
            <div class="stat-label">MOVES</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="matches">0</div>
            <div class="stat-label">MATCHES</div>
        </div>
    </div>
    
    <div class="game-board" id="gameBoard"></div>
    
    <script>
        const symbols = ['🎮', '🎯', '🎲', '🎪', '🎨', '🎭', '🎸', '🎬'];
        const cards = [...symbols, ...symbols];
        let flippedCards = [];
        let moves = 0;
        let matches = 0;
        
        function shuffle(array) {
            for (let i = array.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]];
            }
            return array;
        }
        
        function createBoard() {
            const gameBoard = document.getElementById('gameBoard');
            gameBoard.innerHTML = '';
            shuffle(cards);
            
            cards.forEach((symbol, index) => {
                const card = document.createElement('div');
                card.className = 'card';
                card.dataset.symbol = symbol;
                card.dataset.index = index;
                card.innerHTML = '?';
                card.addEventListener('click', flipCard);
                gameBoard.appendChild(card);
            });
        }
        
        function flipCard(e) {
            const card = e.target;
            if (card.classList.contains('flipped') || card.classList.contains('matched') || flippedCards.length === 2) {
                return;
            }
            
            card.classList.add('flipped');
            card.innerHTML = card.dataset.symbol;
            flippedCards.push(card);
            
            if (flippedCards.length === 2) {
                moves++;
                document.getElementById('moves').textContent = moves;
                checkMatch();
            }
        }
        
        function checkMatch() {
            const [card1, card2] = flippedCards;
            
            setTimeout(() => {
                if (card1.dataset.symbol === card2.dataset.symbol) {
                    card1.classList.add('matched');
                    card2.classList.add('matched');
                    matches++;
                    document.getElementById('matches').textContent = matches;
                    
                    if (matches === symbols.length) {
                        alert('🎉 Congratulations! You won!');
                    }
                } else {
                    card1.classList.remove('flipped');
                    card2.classList.remove('flipped');
                    card1.innerHTML = '?';
                    card2.innerHTML = '?';
                }
                flippedCards = [];
            }, 1000);
        }
        
        createBoard();
    </script>
</body>
</html>""",
        "description": "A classic memory card matching game with a cyberpunk twist. Flip cards to find matching pairs!"
    }
}

async def generate_mock_sse_stream(prompt: str, session_id: str):
    """Generate mock Server-Sent Events stream matching the frontend PRD contract."""
    
    # Determine which game template to use based on prompt
    template_key = "breakout" if "breakout" in prompt.lower() else "memory"
    game_template = GAME_TEMPLATES[template_key]
    
    # Phase 1: Status - Thinking
    yield f"data: {json.dumps({'type': 'status', 'payload': 'thinking'})}\n\n"
    await asyncio.sleep(0.5)
    
    # Phase 2: AI thinking chunks
    thinking_chunks = [
        "I'll help you create an awesome game! Let me analyze your request...",
        f"\n\nGreat idea! I'm planning a {template_key} game with:",
        "\n• Cyberpunk visual theme",
        "\n• Smooth animations", 
        "\n• Engaging gameplay mechanics",
        "\n\nNow let me start building the code..."
    ]
    
    for chunk in thinking_chunks:
        yield f"data: {json.dumps({'type': 'chunk', 'payload': chunk})}\n\n"
        await asyncio.sleep(0.3)
    
    await asyncio.sleep(1)
    
    # Phase 3: Status - Generating
    yield f"data: {json.dumps({'type': 'status', 'payload': 'generating'})}\n\n"
    await asyncio.sleep(0.5)
    
    # Phase 4: Code generation commands
    commands = [
        "<createFile name='index.html'>Setting up game structure...</createFile>",
        "<generateCSS>Adding cyberpunk styling...</generateCSS>", 
        "<implementJS>Creating game logic...</implementJS>",
        "<optimizeCode>Polishing and optimizing...</optimizeCode>"
    ]
    
    for command in commands:
        yield f"data: {json.dumps({'type': 'command', 'payload': command})}\n\n"
        await asyncio.sleep(0.8)
    
    # Phase 5: Final code delivery
    code_payload = {
        "html": game_template["html"],
        "css": "", # CSS is embedded in HTML for simplicity
        "js": ""   # JS is embedded in HTML for simplicity
    }
    
    yield f"data: {json.dumps({'type': 'code', 'payload': code_payload})}\n\n"
    await asyncio.sleep(0.5)
    
    # Phase 6: Completion message
    completion_message = f"\n\n🎉 Your {template_key} game is ready! {game_template['description']}\n\nWhat would you like to add or modify next?"
    yield f"data: {json.dumps({'type': 'chunk', 'payload': completion_message})}\n\n"
    
    # End stream
    yield "data: [DONE]\n\n"

@app.get("/")
async def root():
    return {"message": "Maya AI Game Creation API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/generate-game")
async def generate_game_stream(request: ChatMessage):
    """Generate a game using Server-Sent Events streaming."""
    
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    async def event_stream():
        try:
            async for event in generate_mock_sse_stream(request.prompt, session_id):
                yield event
        except Exception as e:
            # Send error event if something goes wrong
            error_payload = f"Sorry, I encountered an error while generating your game: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'payload': error_payload})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

@app.post("/generate-game-real")
async def generate_game_real_stream(request: ChatMessage):
    """Generate a game using the real Maya agent with SSE streaming."""
    
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    async def event_stream():
        async for event in maya_service.generate_game_stream(
            prompt=request.prompt,
            session_id=session_id,
            user_id=request.user_id,
            session_store=session_store
        ):
            yield event
    
    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

@app.post("/chat")
async def chat_stream(request: ChatMessage):
    """Chat endpoint that also supports game generation."""
    # For now, redirect to generate-game
    return await generate_game_stream(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)