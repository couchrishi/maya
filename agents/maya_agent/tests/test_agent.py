import pytest
from dotenv import load_dotenv
import json
import os
import anyio

# Correctly load the .env file from the project root.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from agents.maya_agent.maya_agent.agent import maya_agent
from agents.maya_agent.maya_agent.schemas import GameRequest
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

@pytest.mark.anyio
async def test_maya_agent_initial_generation():
    """
    Tests that the MayaAgent returns a valid JSON object with the correct keys.
    """
    session_service = InMemorySessionService()
    
    # Create a session first
    await session_service.create_session(
        app_name="maya_test",
        user_id="test_user", 
        session_id="test_session"
    )
    
    runner = Runner(
        agent=maya_agent,
        app_name="maya_test",
        session_service=session_service
    )
    request = GameRequest(requirements="a simple breakout game")
    
    # Use the runner to execute the agent.
    content = types.Content(role='user', parts=[types.Part(text=request.requirements)])
    events = runner.run_async(user_id="test_user", session_id="test_session", new_message=content)
    
    response_str = ""
    async for event in events:
        if event.is_final_response():
            response_str = event.content.parts[0].text
            break
    
    assert response_str
    
    # Clean the response to handle potential markdown formatting.
    cleaned_response = response_str.strip().replace('```json', '').replace('```', '')
    
    # Validate that the response is a valid JSON object.
    response_obj = json.loads(cleaned_response)
    
    assert "html" in response_obj
    assert "css" in response_obj
    assert "js" in response_obj

@pytest.mark.anyio
async def test_maya_agent_empty_prompt():
    """
    Tests that the MayaAgent handles an empty prompt gracefully.
    """
    session_service = InMemorySessionService()
    
    # Create a session first
    await session_service.create_session(
        app_name="maya_test",
        user_id="test_user", 
        session_id="test_session"
    )
    
    runner = Runner(
        agent=maya_agent,
        app_name="maya_test",
        session_service=session_service
    )
    content = types.Content(role='user', parts=[types.Part(text="")])
    events = runner.run_async(user_id="test_user", session_id="test_session", new_message=content)
    
    response_str = ""
    async for event in events:
        if event.is_final_response():
            response_str = event.content.parts[0].text
            break
    assert response_str
    
    try:
        response_obj = json.loads(response_str)
        assert "html" not in response_obj
    except json.JSONDecodeError:
        pass