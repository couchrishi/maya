# /agents/maya-agent/maya_agent/sub_agents/generator/streaming.py
from enum import Enum
from typing import AsyncGenerator, Optional
import re
import json
from google.adk.events.event import Event
from google.genai import types

class ParseState(Enum):
    """States for tracking the current parsing context."""
    WAITING = "waiting"
    IN_EXPLANATION = "explanation"
    IN_CODE_BLOCK = "code"
    IN_FEATURES = "features"
    IN_SUGGESTIONS = "suggestions"

class StreamingContentProcessor:
    """
    Processes streaming LLM tokens incrementally, detecting sections and 
    yielding SSE events as content becomes available.
    """
    
    def __init__(self, session_state: dict = None):
        self.session_state = session_state or {}
        self.buffer = ""
        self.current_state = ParseState.WAITING
        self.code_buffer = ""
        self.current_section_content = ""
        self.html_code_complete = False
        
        # Section detection patterns - more flexible matching
        self.section_patterns = {
            'explanation_start': re.compile(r'## Building Your Game|## Updating Your Game', re.IGNORECASE),
            'code_start': re.compile(r'```html|```HTML', re.IGNORECASE),
            'code_end': re.compile(r'```', re.IGNORECASE),
            'features_start': re.compile(r'## Game Features|## Updated Features', re.IGNORECASE),
            'suggestions_start': re.compile(r'## Suggested Modifications|## Suggestions', re.IGNORECASE)
        }
    
    async def process_token(self, token: str) -> AsyncGenerator[Event, None]:
        """
        Process a single token and yield events when sections are detected or completed.
        """
        self.buffer += token
        
        # Check for state transitions
        new_state = self._detect_state_transition()
        if new_state != self.current_state:
            # Yield any content from the previous state
            if self.current_section_content.strip():
                async for event in self._yield_section_content():
                    yield event
            
            # Transition to new state
            self._transition_to_state(new_state)
        
        # Process content based on current state
        if self.current_state == ParseState.IN_EXPLANATION:
            async for event in self._process_explanation_content():
                yield event
        elif self.current_state == ParseState.IN_CODE_BLOCK:
            async for event in self._process_code_content():
                yield event
        elif self.current_state == ParseState.IN_FEATURES:
            async for event in self._process_features_content():
                yield event
        elif self.current_state == ParseState.IN_SUGGESTIONS:
            async for event in self._process_suggestions_content():
                yield event
    
    async def finalize(self) -> AsyncGenerator[Event, None]:
        """
        Handle any remaining content when streaming is complete.
        """
        # Yield any remaining section content
        if self.current_section_content.strip():
            async for event in self._yield_section_content():
                yield event
        
        # If we have complete HTML code, create final game data
        if self.code_buffer.strip() and not self.html_code_complete:
            game_data = {
                "html": self.code_buffer.strip(),
                "css": "",  # CSS embedded in HTML
                "js": ""    # JS embedded in HTML
            }
            
            # Send structured code event (state will be handled by agent)
            yield self._create_sse_event("code", game_data)
            self.html_code_complete = True
    
    def _detect_state_transition(self) -> ParseState:
        """Detect if we should transition to a new parsing state."""
        
        # Priority order: Code block (highest), Features, Explanation (lowest)
        # This ensures we detect transitions properly
        
        # Check for code block start (highest priority)
        if self.section_patterns['code_start'].search(self.buffer):
            return ParseState.IN_CODE_BLOCK
        
        # Check for suggestions section start
        if self.section_patterns['suggestions_start'].search(self.buffer):
            return ParseState.IN_SUGGESTIONS
        
        # Check for features section start
        if self.section_patterns['features_start'].search(self.buffer):
            return ParseState.IN_FEATURES
        
        # Check for explanation section start (lowest priority)
        if self.section_patterns['explanation_start'].search(self.buffer):
            return ParseState.IN_EXPLANATION
        
        return self.current_state
    
    def _transition_to_state(self, new_state: ParseState):
        """Handle state transition logic."""
        self.current_state = new_state
        
        if new_state == ParseState.IN_EXPLANATION:
            # Extract content after the section header
            match = self.section_patterns['explanation_start'].search(self.buffer)
            if match:
                self.current_section_content = self.buffer[match.end():]
        
        elif new_state == ParseState.IN_CODE_BLOCK:
            # Reset code buffer and find start position
            match = self.section_patterns['code_start'].search(self.buffer)
            if match:
                self.code_buffer = ""
                self.current_section_content = self.buffer[match.end():]
        
        elif new_state == ParseState.IN_FEATURES:
            # Extract content after the section header
            match = self.section_patterns['features_start'].search(self.buffer)
            if match:
                self.current_section_content = self.buffer[match.end():]
        
        elif new_state == ParseState.IN_SUGGESTIONS:
            # Extract content after the section header
            match = self.section_patterns['suggestions_start'].search(self.buffer)
            if match:
                self.current_section_content = self.buffer[match.end():]
    
    async def _process_explanation_content(self) -> AsyncGenerator[Event, None]:
        """Process content when in explanation state."""
        # Check if we've moved past the explanation section
        code_start = self.section_patterns['code_start'].search(self.buffer)
        if code_start:
            # Extract explanation up to code start
            explanation_content = self.buffer[:code_start.start()]
            # Remove the section header
            explanation_content = self.section_patterns['explanation_start'].sub('', explanation_content, count=1)
            
            # Only yield if we haven't sent this content before
            explanation_text = explanation_content.strip()
            if explanation_text and explanation_text != self.current_section_content:
                yield self._create_sse_event("explanation", explanation_text)
                self.current_section_content = explanation_text
    
    async def _process_code_content(self) -> AsyncGenerator[Event, None]:
        """Process content when in code block state."""
        # Check for code block end
        code_end = self.section_patterns['code_end'].search(self.buffer)
        
        if code_end:
            # Extract complete code block
            code_start = self.section_patterns['code_start'].search(self.buffer)
            if code_start:
                code_content = self.buffer[code_start.end():code_end.start()]
                full_code = code_content.strip()
                
                # Send code chunk event only if we have new content
                if full_code and full_code != self.code_buffer:
                    yield self._create_sse_event("code_chunk", full_code)
                    self.code_buffer = full_code
                
                # Create game data structure
                if not self.html_code_complete and self.code_buffer:
                    game_data = {
                        "html": self.code_buffer,
                        "css": "",  # CSS embedded in HTML
                        "js": ""    # JS embedded in HTML
                    }
                    
                    # Send structured code event (state will be handled by agent)
                    yield self._create_sse_event("code", game_data)
                    self.html_code_complete = True
                
                self.current_section_content = ""
        else:
            # Still in code block, accumulate content but don't yield partial events
            # This prevents individual tokens from being sent as separate SSE events
            code_start = self.section_patterns['code_start'].search(self.buffer)
            if code_start:
                partial_code = self.buffer[code_start.end():]
                self.code_buffer = partial_code  # Just accumulate, don't yield
    
    async def _process_features_content(self) -> AsyncGenerator[Event, None]:
        """Process content when in features state."""
        # For features, we can stream incrementally as text arrives
        current_pos = len(self.current_section_content)
        
        # Find features section start
        match = self.section_patterns['features_start'].search(self.buffer)
        if match:
            features_content = self.buffer[match.end():]
            
            # Stream new content if we have enough (increased threshold to reduce noise)
            if len(features_content) > current_pos + 200:  # 200 char threshold
                new_content = features_content[current_pos:]
                if new_content.strip():
                    yield self._create_sse_event("features", new_content.strip())
                    self.current_section_content = features_content
    
    async def _process_suggestions_content(self) -> AsyncGenerator[Event, None]:
        """Process content when in suggestions state."""
        # For suggestions, we can stream incrementally as text arrives
        current_pos = len(self.current_section_content)
        
        # Find suggestions section start
        match = self.section_patterns['suggestions_start'].search(self.buffer)
        if match:
            suggestions_content = self.buffer[match.end():]
            
            # Stream new content if we have enough (increased threshold to reduce noise)
            if len(suggestions_content) > current_pos + 200:  # 200 char threshold
                new_content = suggestions_content[current_pos:]
                if new_content.strip():
                    yield self._create_sse_event("suggestions", new_content.strip())
                    self.current_section_content = suggestions_content
    
    async def _yield_section_content(self) -> AsyncGenerator[Event, None]:
        """Yield remaining content from current section."""
        if self.current_state == ParseState.IN_EXPLANATION and self.current_section_content:
            yield self._create_sse_event("explanation", self.current_section_content.strip())
        elif self.current_state == ParseState.IN_FEATURES and self.current_section_content:
            yield self._create_sse_event("features", self.current_section_content.strip())
        elif self.current_state == ParseState.IN_SUGGESTIONS and self.current_section_content:
            yield self._create_sse_event("suggestions", self.current_section_content.strip())
    
    def _create_sse_event(self, event_type: str, payload) -> Event:
        """Create properly formatted SSE event for frontend."""
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