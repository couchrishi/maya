from pydantic import BaseModel, Field
from typing import List

class GameRequest(BaseModel):
    requirements: str = Field(description="Natural language description of the game.")

class GameCode(BaseModel):
    html: str
    css: str
    js: str

class PlayableGame(BaseModel):
    code: GameCode
    explanation: str
    gameType: str
    features: List[str]
    qualityScore: float
