# This file will define the OrchestratorAgent.

from google.adk.agents import Agent, LlmAgent
from google.adk.tools.agent_tool import AgentTool
from maya_agent.sub_agents.generator.agent import game_creator_agent
from maya_agent.sub_agents.publisher.agent import publisher_agent
from maya_agent.sub_agents.asset_generator.agent import asset_generator_agent
from maya_agent.prompts import ORCHESTRATOR_INSTRUCTIONS
from maya_agent.config import FAST_MODEL_NAME
import json
from typing import AsyncGenerator
from google.adk.events.event import Event
from google.genai import types

class OrchestratorAgent(LlmAgent):
    """
    Orchestrator agent that intelligently routes between game creation, asset generation, and publishing.
    Uses simplified routing with single Game Creator agent that checks artifacts automatically.
    """
    def __init__(self, **kwargs):
        super().__init__(
            name="maya_orchestrator",
            instruction=ORCHESTRATOR_INSTRUCTIONS,
            model=FAST_MODEL_NAME,
            sub_agents=[
                game_creator_agent,    # Single agent that checks artifacts automatically
                publisher_agent        # For game publishing
            ],
            tools=[
                AgentTool(agent=asset_generator_agent)  # Asset generation as AgentTool
            ],
            **kwargs
        )

    # Temporarily removed custom _run_async_impl to test if default ADK routing works
    # The issue might be that ADK LlmAgent with sub-agents expects LLM-driven routing
    
    def _extract_user_prompt(self, context) -> str:
        """Extract user prompt from ADK context."""
        if hasattr(context, 'new_message') and context.new_message:
            if hasattr(context.new_message, 'parts') and context.new_message.parts:
                return context.new_message.parts[0].text
        return "user request"
    
    
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