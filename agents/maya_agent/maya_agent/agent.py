# /agents/maya_agent/maya_agent/agent.py
from google.adk.agents import LlmAgent
from .prompts import MAYA_AGENT_INSTRUCTIONS
from .config import MODEL_NAME

# This is the correct, simple way to define the agent.
maya_agent = LlmAgent(
    name="maya_agent",
    instruction=MAYA_AGENT_INSTRUCTIONS,
    model=MODEL_NAME,
)