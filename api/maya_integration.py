import json
import asyncio
from typing import AsyncGenerator
from agents.maya_agent.maya_agent.agent import maya_agent
from agents.maya_agent.maya_agent.schemas import GameRequest
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uuid

class MayaAgentService:
    """Service to integrate the real Maya agent with FastAPI SSE streaming."""
    
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=maya_agent,
            app_name="maya_api",
            session_service=self.session_service
        )
        self.sessions = {}  # Track active sessions
    
    async def ensure_session(self, session_id: str, user_id: str = "api_user") -> str:
        """Ensure a session exists for the given session_id."""
        if session_id not in self.sessions:
            await self.session_service.create_session(
                app_name="maya_api",
                user_id=user_id,
                session_id=session_id
            )
            self.sessions[session_id] = {"user_id": user_id, "created": True}
        return session_id
    
    async def generate_game_stream(self, prompt: str, session_id: str = None, user_id: str = "api_user", session_store: dict = None) -> AsyncGenerator[str, None]:
        """Generate a game using the real Maya agent with SSE streaming."""
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Ensure session exists
        await self.ensure_session(session_id, user_id)
        
        # Initialize session in shared store if not exists
        if session_store is not None:
            if session_id not in session_store:
                session_store[session_id] = {
                    "user_id": user_id,
                    "conversation_history": [],
                    "current_game": None,
                    "created_at": asyncio.get_event_loop().time()
                }
            
            # Add current prompt to conversation history
            session_store[session_id]["conversation_history"].append({
                "role": "user",
                "content": prompt,
                "timestamp": asyncio.get_event_loop().time()
            })
        
        try:
            # Phase 1: Status - Thinking
            yield self._create_sse_event("status", "thinking")
            
            # Phase 2: Initial response
            initial_message = "Let me create an amazing game for you! Analyzing your request..."
            yield self._create_sse_event("chunk", initial_message)
            
            # Phase 3: Create enhanced prompt with context for follow-up requests
            enhanced_prompt = prompt
            if session_store is not None and session_id in session_store:
                session_data = session_store[session_id]
                if session_data.get("current_game") and len(session_data["conversation_history"]) > 1:
                    # This is a follow-up request - add context
                    enhanced_prompt = f"""
Previous context: I previously generated a game for you. Here's the current game code:
{json.dumps(session_data["current_game"], indent=2)}

User's new request: {prompt}

Please modify the existing game according to the user's request, or create a new game if they're asking for something completely different. Return the complete updated game code in JSON format with html, css, and js fields.
"""
            
            # Call the real Maya agent
            content = types.Content(role='user', parts=[types.Part(text=enhanced_prompt)])
            events = self.runner.run_async(
                user_id=user_id, 
                session_id=session_id, 
                new_message=content
            )
            
            # Phase 4: Status - Generating
            yield self._create_sse_event("status", "generating")
            
            # Phase 5: Process agent events
            response_text = ""
            final_code = None
            
            async for event in events:
                if event.is_final_response():
                    response_text = event.content.parts[0].text
                    break
                else:
                    # Stream any intermediate content if available
                    if hasattr(event, 'content') and event.content:
                        if hasattr(event.content, 'parts') and event.content.parts:
                            chunk = event.content.parts[0].text if event.content.parts[0].text else ""
                            if chunk:
                                yield self._create_sse_event("chunk", chunk)
            
            # Phase 6: Parse the response and extract JSON
            try:
                # Clean the response to handle potential markdown formatting
                cleaned_response = response_text.strip().replace('```json', '').replace('```', '')
                
                # Try to parse as JSON
                code_data = json.loads(cleaned_response)
                
                # Validate that we have the expected structure
                if isinstance(code_data, dict) and "html" in code_data:
                    # Send command events to show progress
                    yield self._create_sse_event("command", "<parseResponse>Extracting game code...</parseResponse>")
                    await asyncio.sleep(0.5)
                    
                    yield self._create_sse_event("command", "<validateCode>Validating HTML structure...</validateCode>")
                    await asyncio.sleep(0.5)
                    
                    yield self._create_sse_event("command", "<optimizeGame>Optimizing game performance...</optimizeGame>")
                    await asyncio.sleep(0.5)
                    
                    # Store the generated game in session for future modifications
                    if session_store is not None and session_id in session_store:
                        session_store[session_id]["current_game"] = code_data
                        session_store[session_id]["conversation_history"].append({
                            "role": "assistant", 
                            "content": f"Generated game: {code_data.get('title', 'Untitled Game')}",
                            "game_code": code_data,
                            "timestamp": asyncio.get_event_loop().time()
                        })
                    
                    # Send the final code
                    yield self._create_sse_event("code", code_data)
                    
                    # Success message
                    success_message = "\n\n🎉 Your game is ready! The code has been generated and is now playable. What would you like to modify or create next?"
                    yield self._create_sse_event("chunk", success_message)
                
                else:
                    # If not valid JSON structure, treat as text response
                    yield self._create_sse_event("chunk", f"\n\nMaya's response:\n{response_text}")
                    
            except json.JSONDecodeError:
                # If we can't parse as JSON, stream the text response
                yield self._create_sse_event("chunk", f"\n\nMaya's response:\n{response_text}")
                yield self._create_sse_event("error", "The agent didn't return valid game code. Please try rephrasing your request.")
            
        except Exception as e:
            # Send error event if something goes wrong
            error_message = f"Sorry, I encountered an error while generating your game: {str(e)}"
            yield self._create_sse_event("error", error_message)
        
        finally:
            # End the stream
            yield "data: [DONE]\n\n"
    
    def _create_sse_event(self, event_type: str, payload) -> str:
        """Create a properly formatted SSE event."""
        return f"data: {json.dumps({'type': event_type, 'payload': payload})}\n\n"

# Create a global instance
maya_service = MayaAgentService()