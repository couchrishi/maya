import json
import asyncio
from typing import AsyncGenerator
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents', 'maya-agent'))

from maya_agent.agent import orchestrator_agent
from maya_agent.schemas import GameRequest
from google.adk.runners import Runner, RunConfig
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import GcsArtifactService
from google.adk.agents.run_config import StreamingMode
from google.genai import types
import uuid

class MayaAgentService:
    """Service to integrate the real Maya agent with FastAPI SSE streaming."""
    
    def __init__(self):
        self.session_service = InMemorySessionService()
        # Use GCS for persistent asset storage
        self.artifact_service = GcsArtifactService(bucket_name="maya-artifacts")
        self.runner = Runner(
            agent=orchestrator_agent,  # Updated to use orchestrator_agent
            app_name="maya_api",
            session_service=self.session_service,
            artifact_service=self.artifact_service
        )
    
    async def ensure_session(self, session_id: str, user_id: str = "api_user") -> str:
        """Ensure a session exists for the given session_id."""
        try:
            # Try to get existing session
            existing_session = await self.session_service.get_session(
                app_name="maya_api",
                user_id=user_id,
                session_id=session_id
            )
            if not existing_session:
                # Create new session if it doesn't exist
                await self.session_service.create_session(
                    app_name="maya_api",
                    user_id=user_id,
                    session_id=session_id
                )
        except Exception:
            # Create session if get_session fails
            await self.session_service.create_session(
                app_name="maya_api",
                user_id=user_id,
                session_id=session_id
            )
        return session_id
    
    async def generate_game_stream(self, prompt: str, session_id: str = None, user_id: str = "api_user") -> AsyncGenerator[str, None]:
        """Generate a game using the real Maya agent with SSE streaming and ADK session state."""
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Ensure session exists
        await self.ensure_session(session_id, user_id)
        
        try:
            # Call the Maya orchestrator agent with streaming configuration
            content = types.Content(role='user', parts=[types.Part(text=prompt)])
            
            # Configure for real SSE streaming 
            run_config = RunConfig(
                streaming_mode=StreamingMode.SSE,
                max_llm_calls=20  # Increased to allow Firebase MCP configuration and deployment
            )
            
            # Run the orchestrator agent (which delegates to GameCreatorAgent)
            events = self.runner.run_async(
                user_id=user_id, 
                session_id=session_id, 
                new_message=content,
                run_config=run_config
            )
            
            # Stream events directly from the agent (agent now handles SSE formatting)
            async for event in events:
                if hasattr(event, 'content') and event.content and event.content.parts:
                    # Extract the JSON payload from the event
                    event_text = event.content.parts[0].text
                    
                    # Forward as SSE event - agent already formats as JSON
                    yield f"data: {event_text}\n\n"
            
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