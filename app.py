# /app.py
from google.adk.adk_app import AdkApp
from agents.maya_agent.agent import maya_agent

adk_app = AdkApp(
    agents=[maya_agent]
)
