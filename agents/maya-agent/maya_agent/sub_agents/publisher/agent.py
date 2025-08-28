# Game Publisher Agent - Simple Firebase CLI deployment with publisher events

from google.adk.agents import LlmAgent
from google.adk.events.event import Event
from google.genai import types
from .prompts import PUBLISHER_INSTRUCTIONS
from .schemas import FirebaseConfig
from .tools_adk import create_hosting_tools, publish_game
from maya_agent.config import FAST_MODEL_NAME
import json
from typing import AsyncGenerator

class GamePublisherAgent(LlmAgent):
    """LLMAgent for publishing HTML5 games using Firebase CLI with event streaming"""
    
    def __init__(self, **kwargs):
        firebase_config = FirebaseConfig()
        tools = create_hosting_tools(firebase_config)
        
        super().__init__(
            name="game_publisher_agent",
            instruction=PUBLISHER_INSTRUCTIONS,
            model=FAST_MODEL_NAME,
            tools=tools,
            **kwargs
        )
    
    async def _run_async_impl(self, context, **kwargs) -> AsyncGenerator[Event, None]:
        """
        Custom implementation that handles publishing with structured events.
        """
        # Extract user prompt
        user_prompt = self._extract_user_prompt(context)
        
        # Emit Publisher start event
        yield Event(
            author="game_publisher_agent",
            content=types.Content(
                role="model",
                parts=[types.Part(text=f"🚀 Publisher: Starting game deployment process")]
            )
        )
        
        # Phase 1: Validation - Check if game exists
        yield Event(
            author="game_publisher_agent",
            content=types.Content(
                role="model",
                parts=[types.Part(text="🔍 Publisher: Validating game data for deployment")]
            )
        )
        yield self._create_publisher_event("publish_status", "validating")
        
        # Get game data from session state
        current_game = context.session.state.get('current_game')
        
        if not current_game or not current_game.get('html'):
            # No game found - send error event and stop
            yield self._create_publisher_event("publish_error", "no_game")
            yield self._create_chat_event("❌ I don't see a game to publish yet! Let's create one first. What kind of game would you like to build?")
            return
        
        # Phase 2: Preparation
        yield Event(
            author="game_publisher_agent",
            content=types.Content(
                role="model",
                parts=[types.Part(text="📦 Publisher: Preparing game files for Firebase deployment")]
            )
        )
        yield self._create_publisher_event("publish_status", "preparing")
        
        # Phase 3: Deployment
        yield Event(
            author="game_publisher_agent",
            content=types.Content(
                role="model",
                parts=[types.Part(text="🚀 Publisher: Initiating Firebase hosting deployment")]
            )
        )
        yield self._create_publisher_event("publish_status", "deploying")
        
        try:
            # Call the publish_game tool directly
            from google.adk.tools import ToolContext
            
            # Create a simplified tool context with the session state
            class SimpleToolContext:
                def __init__(self, state):
                    self.state = state
            
            # Pass session state to tool context
            tool_context = SimpleToolContext(context.session.state)
            
            # Emit tool execution event
            yield Event(
                author="game_publisher_agent",
                content=types.Content(
                    role="model",
                    parts=[types.Part(text="⚙️ Publisher: Executing Firebase CLI deployment tool")]
                )
            )
            
            result = publish_game(user_prompt, tool_context)
            
            if result["success"]:
                # Phase 4: Success
                yield Event(
                    author="game_publisher_agent",
                    content=types.Content(
                        role="model",
                        parts=[types.Part(text=f"✅ Publisher: Deployment successful! Game live at {result['live_url']}")]
                    )
                )
                
                yield self._create_publisher_event("publish_success", {
                    "live_url": result["live_url"],
                    "site_name": result["site_name"],
                    "message": result["message"]
                })
                
                # Send celebration message
                celebration_msg = f"""🎉 Amazing! I've successfully deployed your game to the web.

Your game is now live and ready to play at:
{result["live_url"]}

Anyone with this link can play your game instantly - no downloads needed! 

Want to create another game or make changes to this one?"""
                
                yield self._create_chat_event(celebration_msg)
                
            else:
                # Deployment failed
                yield Event(
                    author="game_publisher_agent",
                    content=types.Content(
                        role="model",
                        parts=[types.Part(text=f"❌ Publisher: Deployment failed - {result.get('message', 'Unknown error')}")]
                    )
                )
                
                yield self._create_publisher_event("publish_error", "deployment_failed")
                yield self._create_chat_event(f"❌ {result['message']} Let me try again - these things happen sometimes with hosting services!")
                
        except Exception as e:
            # Unexpected error
            yield Event(
                author="game_publisher_agent",
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=f"💥 Publisher: Unexpected error during deployment - {str(e)}")]
                )
            )
            
            yield self._create_publisher_event("publish_error", "unexpected_error")
            yield self._create_chat_event(f"❌ Something unexpected happened during deployment: {str(e)}. Please try again!")
        
        # Emit Publisher completion event
        yield Event(
            author="game_publisher_agent",
            content=types.Content(
                role="model",
                parts=[types.Part(text="🏁 Publisher: Publishing workflow completed")]
            )
        )
    
    def _extract_user_prompt(self, context) -> str:
        """Extract user prompt from ADK context."""
        if hasattr(context, 'new_message') and context.new_message:
            if hasattr(context.new_message, 'parts') and context.new_message.parts:
                return context.new_message.parts[0].text
        return "publish the game"
    
    def _create_publisher_event(self, event_type: str, payload) -> Event:
        """Create publisher-specific SSE event."""
        return Event(
            author="agent",
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=json.dumps({'type': event_type, 'payload': payload})
                    )
                ]
            )
        )
    
    def _create_chat_event(self, message: str) -> Event:
        """Create a regular chat message event."""
        return Event(
            author="agent",
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=json.dumps({'type': 'publish_message', 'payload': message})
                    )
                ]
            )
        )

# Create the publisher agent instance  
publisher_agent = GamePublisherAgent()