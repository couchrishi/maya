# /agents/maya_agent/maya_agent/schemas.py
from pydantic import BaseModel

class GameRequest(BaseModel):
    """Defines the structure for a game generation request."""
    requirements: str

class GameCode(BaseModel):
    """Defines the structure for the generated game code."""
    html: str
    css: str
    js: str