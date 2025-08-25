# Pydantic schemas for the Publisher Agent

from pydantic import BaseModel

class FirebaseConfig(BaseModel):
    """Firebase project configuration"""
    project_id: str = "saib-ai-playground"
    storage_bucket: str = "saib-ai-playground.appspot.com"