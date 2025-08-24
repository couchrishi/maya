import json
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Add this to your existing FastAPI app
mock_router = APIRouter()

class MockRequest(BaseModel):
    prompt: str
    session_id: str = "mock_session"
    user_id: str = "mock_user"

async def mock_game_stream():
    """Stream mock events to test frontend event routing."""
    
    # Mock events with proper classification
    events = [
        {"type": "status", "payload": "thinking"},
        {"type": "chunk", "payload": "Let me create an amazing game for you! Analyzing your request..."},
        {"type": "status", "payload": "generating"},
        {"type": "chunk", "payload": "\n\n## Building Your Game\nI'm crafting a sleek Snake game with smooth animations and modern styling."},
        {"type": "chunk", "payload": "\n\n```html\n"},  # This should go to chat
        {"type": "code_chunk", "payload": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>"},
        {"type": "code_chunk", "payload": "\n    <meta charset=\"UTF-8\">"},
        {"type": "code_chunk", "payload": "\n    <style>\n        body { margin: 0; background: #000; }"},
        {"type": "code_chunk", "payload": "\n        canvas { border: 2px solid #fff; display: block; margin: 20px auto; }"},
        {"type": "code_chunk", "payload": "\n    </style>\n</head>\n<body>"},
        {"type": "code_chunk", "payload": "\n    <canvas id=\"gameCanvas\" width=\"400\" height=\"400\"></canvas>"},
        {"type": "code_chunk", "payload": "\n    <script>\n        const canvas = document.getElementById('gameCanvas');"},
        {"type": "code_chunk", "payload": "\n        const ctx = canvas.getContext('2d');"},
        {"type": "code_chunk", "payload": "\n        // Simple snake game logic here"},
        {"type": "code_chunk", "payload": "\n        ctx.fillStyle = '#0f0';"},
        {"type": "code_chunk", "payload": "\n        ctx.fillRect(50, 50, 20, 20); // Snake head"},
        {"type": "code_chunk", "payload": "\n    </script>\n</body>\n</html>"},
        {"type": "chunk", "payload": "\n```\n\n## Game Features\n* Classic Snake gameplay\n* Smooth canvas animations\n* Keyboard controls (arrow keys)\n* Score tracking"},
        {"type": "command", "payload": "<parseResponse>Extracting game code...</parseResponse>"},
        {"type": "command", "payload": "<validateCode>Validating HTML structure...</validateCode>"},
        {"type": "code", "payload": {
            "html": "<!DOCTYPE html><html><head><style>body{margin:0;background:#000}canvas{border:2px solid #fff;display:block;margin:20px auto}</style></head><body><canvas id=\"gameCanvas\" width=\"400\" height=\"400\"></canvas><script>const canvas=document.getElementById('gameCanvas');const ctx=canvas.getContext('2d');ctx.fillStyle='#0f0';ctx.fillRect(50,50,20,20);</script></body></html>",
            "css": "",
            "js": ""
        }},
        {"type": "chunk", "payload": "\n\n🎉 Game generated successfully! Your Snake game is ready to play. What would you like to modify?"}
    ]
    
    # Stream each event with delay
    for i, event in enumerate(events):
        print(f"MOCK: Sending event {i+1}/{len(events)}: {event['type']}")
        yield f"data: {json.dumps(event)}\n\n"
        await asyncio.sleep(0.3)  # Simulate streaming delay
    
    # End stream
    yield "data: [DONE]\n\n"

@mock_router.post("/mock-generate-game")
async def mock_generate_game(request: MockRequest):
    """Mock endpoint that streams properly classified events."""
    return StreamingResponse(
        mock_game_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        }
    )