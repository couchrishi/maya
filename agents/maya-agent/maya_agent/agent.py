# This file will define the OrchestratorAgent.

from google.adk.agents import Agent, LlmAgent
from maya_agent.sub_agents.generator.agent import game_creator_agent
from maya_agent.prompts import ORCHESTRATOR_INSTRUCTIONS
from maya_agent.config import MODEL_NAME
import json
from typing import AsyncGenerator
from google.adk.events.event import Event
from google.genai import types

class OrchestratorAgent(LlmAgent):
    """
    A custom agent that orchestrates the game generation process using sub-agent delegation.
    """
    def __init__(self, **kwargs):
        super().__init__(
            name="maya_orchestrator",
            instruction=ORCHESTRATOR_INSTRUCTIONS,
            model=MODEL_NAME,
            sub_agents=[game_creator_agent],  # Use sub-agent instead of tools
            **kwargs
        )

    async def _run_async_impl(
        self, context, **kwargs
    ) -> AsyncGenerator[Event, None]:
        """
        The main execution logic for the orchestrator agent - delegates to GameCreatorAgent.
        """
        # Check session state to understand the request type
        session_state = context.session.state
        
        # Extract user prompt
        user_prompt = self._extract_user_prompt(context)
        
        # Simple routing logic - for now, all requests go to game creation
        # In the future, could route to different specialists based on intent
        if self._is_game_creation_request(user_prompt, session_state):
            # Delegate completely to GameCreatorAgent
            async for event in game_creator_agent.run_async(context):
                yield event
        else:
            # Fallback - use orchestrator for non-game requests
            yield self._create_sse_event("chunk", "I'm Maya, your AI game creation assistant. What kind of game would you like me to create?")
    
    def _extract_user_prompt(self, context) -> str:
        """Extract user prompt from ADK context."""
        if hasattr(context, 'new_message') and context.new_message:
            if hasattr(context.new_message, 'parts') and context.new_message.parts:
                return context.new_message.parts[0].text
        return ""
    
    def _is_game_creation_request(self, user_prompt: str, session_state: dict) -> bool:
        """
        Determine if this is a game creation/modification request.
        For now, assume all requests are game-related.
        Future: Could use intent classification.
        """
        # For now, always delegate to game creator
        # Future: Could implement intent classification here
        return True
    
    def _create_sse_event(self, event_type: str, payload) -> Event:
        """Creates a properly formatted SSE event."""
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

orchestrator_agent = OrchestratorAgent()