import pytest
from maya.tools.draft_generator import draft_generator
from maya.schemas.game import GameCode, GameRequest
from dotenv import load_dotenv

load_dotenv()

def test_draft_generator_success():
    """
    Tests that the draft_generator tool successfully creates a GameCode object
    with non-empty html, css, and js fields when given a valid request.
    """
    request = GameRequest(requirements="a simple pong game")
    result = draft_generator(request.requirements)
    assert isinstance(result, GameCode)
    assert result.html
    assert result.css
    assert result.js

def test_draft_generator_input_validation():
    """
    Tests that the draft_generator tool raises a ValueError when
    given an empty string as a requirement.
    """
    with pytest.raises(ValueError):
        draft_generator("")
