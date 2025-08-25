# This file will define the OrchestratorAgent.

from google.adk.agents import Agent, LlmAgent
from maya_agent.sub_agents.generator.agent import game_creator_agent
from maya_agent.sub_agents.publisher.agent import publisher_agent
from maya_agent.prompts import ORCHESTRATOR_INSTRUCTIONS
from maya_agent.config import MODEL_NAME
import json
from typing import AsyncGenerator
from google.adk.events.event import Event
from google.genai import types

class OrchestratorAgent(LlmAgent):
    """
    A custom agent that orchestrates the game generation process using intelligent sub-agent delegation.
    """
    def __init__(self, **kwargs):
        super().__init__(
            name="maya_orchestrator",
            instruction=ORCHESTRATOR_INSTRUCTIONS,
            model=MODEL_NAME,
            sub_agents=[
                game_creator_agent,    # For game creation and modification
                publisher_agent        # For game publishing (LLMAgent with Firebase MCP)
            ],
            tools=[],  # No direct tools - sub-agents handle everything
            **kwargs
        )

    async def _run_async_impl(
        self, context, **kwargs
    ) -> AsyncGenerator[Event, None]:
        """
        Let the LLM intelligently route to the appropriate sub-agent based on user intent and session context.
        No hardcoded routing logic - pure LLM intelligence with access to both agents.
        """
        # Let the orchestrator LLM decide which agent to use based on user intent and session context
        async for event in super()._run_async_impl(context, **kwargs):
            yield event
    
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