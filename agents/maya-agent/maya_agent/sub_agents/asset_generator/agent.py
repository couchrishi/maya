# Asset Generator Agent - Clean ADK LlmAgent with function tools

from google.adk.agents import LlmAgent
from google.adk.events.event import Event
from google.adk.events import EventActions
from google.genai import types
from .prompts import ASSET_GENERATOR_INSTRUCTIONS
from .tools import game_asset_generator_tool
# from .tools_vertex import game_asset_generator_vertex_tool
from maya_agent.config import FAST_MODEL_NAME
from typing import AsyncGenerator

class AssetGeneratorAgent(LlmAgent):
    """
    Clean asset generation agent using ADK function tools.
    Generates exactly 3 strategic visual assets for games.
    Has both HuggingFace and Vertex AI tools available.
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="asset_generator",
            description="Generates 3 strategic visual assets for HTML5 games: primary character, interactive object, and environmental element. Can use either HuggingFace or Vertex AI backends.",
            instruction=ASSET_GENERATOR_INSTRUCTIONS,
            model=FAST_MODEL_NAME,
            tools=[
                game_asset_generator_tool,         # HuggingFace backend
                #game_asset_generator_vertex_tool   # Vertex AI backend
            ],
            **kwargs
        )

# Create the asset generator agent instance for AgentTool usage
asset_generator_agent = AssetGeneratorAgent()