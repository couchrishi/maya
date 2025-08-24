import pytest
from dotenv import load_dotenv
import json
import os
import asyncio

# Correctly load the .env file from the project root.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from maya_agent.agent import orchestrator_agent
from maya_agent.schemas import GameRequest
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

@pytest.mark.asyncio
async def test_orchestrator_agent_successful_stream():
    """
    Tests that the OrchestratorAgent yields a correct sequence of StreamEvent objects.
    """
    session_service = InMemorySessionService()
    runner = Runner(
        agent=orchestrator_agent,
        app_name="maya_test",
        session_service=session_service
    )
    
    session = await session_service.create_session(app_name="maya_test", user_id="test_user")
    session_id = session.id
    request = GameRequest(requirements="a simple breakout game")
    content = types.Content(role='user', parts=[types.Part(text=request.requirements)])
    
    events = []
    async for event in runner.run_async(user_id="test_user", session_id=session_id, new_message=content):
        # In a real app, the event would be a complex object.
        # For now, we'll assume it's a JSON string.
        if event.content and event.content.parts:
            events.append(json.loads(event.content.parts[0].text))

    assert events[0]['type'] == 'status'
    assert events[1]['type'] == 'status'
    assert events[2]['type'] == 'chunk'
    assert events[3]['type'] == 'code_chunk'
    assert events[4]['type'] == 'code'
    assert 'html' in events[4]['payload']
