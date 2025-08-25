# /agents/maya-agent/maya_agent/sub_agents/generator/agent.py
from google.adk.agents import LlmAgent
from google.adk.events.event import Event
from google.adk.events import EventActions
from google.genai import types
from .prompts import GENERATOR_INSTRUCTIONS
from .streaming import StreamingContentProcessor
from maya_agent.config import MODEL_NAME
import json
from typing import AsyncGenerator

class GameCreatorAgent(LlmAgent):
    """
    Game creation agent that handles LLM generation, response parsing, 
    and structured event streaming with ADK session state management.
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="game_creator_agent",
            instruction=GENERATOR_INSTRUCTIONS,
            model=MODEL_NAME,
            **kwargs
        )
    
    async def _run_async_impl(self, context, **kwargs) -> AsyncGenerator[Event, None]:
        """
        Main execution logic for game creation with real LLM integration.
        """
        # Extract user prompt from context
        user_prompt = self._extract_user_prompt(context)
        
        # Check session state for conversation context
        session_state = context.session.state
        current_game = session_state.get('current_game', None)
        conversation_history = session_state.get('conversation_history', [])
        
        # Yield initial status
        yield self._create_sse_event("status", "thinking")
        
        # Determine if this is a follow-up request
        is_follow_up = current_game is not None and len(conversation_history) > 0
        
        # Enhance prompt with context for follow-up requests
        enhanced_prompt = self._create_enhanced_prompt(user_prompt, current_game, is_follow_up)
        
        # Store conversation context
        conversation_history.append({
            "role": "user",
            "content": user_prompt,
            "timestamp": context.session.state.get('temp:current_time', 'unknown')
        })
        
        yield self._create_sse_event("status", "generating")
        
        # Create streaming content processor
        processor = StreamingContentProcessor(session_state)
        
        try:
            # Temporarily override the instruction to include the enhanced prompt
            original_instruction = self.instruction
            self.instruction = f"{original_instruction}\n\nUSER REQUEST: {enhanced_prompt}"
            
            try:
                # Accumulate all content and process when complete
                accumulated_content = ""
                
                async for event in super()._run_async_impl(context, **kwargs):
                    # Process all events with content
                    if hasattr(event, 'content') and event.content and event.content.parts:
                        if hasattr(event.content.parts[0], 'text') and event.content.parts[0].text:
                            text_content = event.content.parts[0].text
                            
                            # If this is a partial event, accumulate the content
                            if hasattr(event, 'partial') and event.partial:
                                accumulated_content += text_content
                                # Send partial content for live streaming effect
                                async for parsed_event in processor.process_token(text_content):
                                    yield parsed_event
                            
                            # If this is the final event, process the complete response
                            elif event.is_final_response():
                                # Use the complete accumulated content or the final event content
                                complete_content = accumulated_content + text_content
                                
                                # Process the complete content to generate structured events
                                async for structured_event in self._process_complete_response(complete_content, session_state):
                                    yield structured_event
                                return
                
                # Handle any final cleanup after the stream ends naturally
                async for final_event in processor.finalize():
                    yield final_event
            finally:
                # Restore the original instruction
                self.instruction = original_instruction
                
        except Exception as e:
            yield self._create_sse_event("error", f"Failed to generate game: {str(e)}")
            return
        
        # Add assistant response to conversation history and update state properly
        conversation_history.append({
            "role": "assistant", 
            "content": "Generated game successfully",
            "game_code": session_state.get('current_game', {}).get('html', ''),
            "timestamp": context.session.state.get('temp:current_time', 'unknown')
        })
        
        # Yield final state update event with conversation history
        yield Event(
            author="agent",
            content=types.Content(
                role="model",
                parts=[types.Part(text="")]  # Empty content for state-only update
            ),
            actions=EventActions(state_delta={'conversation_history': conversation_history})
        )
        
        # Game generation completed - streaming processor handles final messages
    
    def _extract_user_prompt(self, context) -> str:
        """Extract user prompt from ADK context."""
        if hasattr(context, 'new_message') and context.new_message:
            if hasattr(context.new_message, 'parts') and context.new_message.parts:
                return context.new_message.parts[0].text
        return "create a simple game"
    
    async def _process_complete_response(self, complete_content: str, session_state: dict):
        """Process the complete LLM response and send structured events."""
        import re
        
        # Extract sections using regex patterns
        explanation_match = re.search(r'## Building Your Game\s*(.*?)(?=```html|$)', complete_content, re.DOTALL)
        code_match = re.search(r'```html\s*(.*?)\s*```', complete_content, re.DOTALL)
        features_match = re.search(r'## (?:Game Features|Added Features)\s*(.*?)(?=## |$)', complete_content, re.DOTALL)
        suggestions_match = re.search(r'## Suggested? Modifications?\s*(.*?)(?=## |$)', complete_content, re.DOTALL)
        
        # Send explanation
        if explanation_match:
            explanation_text = explanation_match.group(1).strip()
            if explanation_text:
                yield self._create_sse_event("explanation", explanation_text)
        
        # Send code
        if code_match:
            html_code = code_match.group(1).strip()
            if html_code:
                # Send code chunk for streaming effect
                yield self._create_sse_event("code_chunk", html_code)
                
                # Create game data structure
                game_data = {
                    "html": html_code,
                    "css": "",  # CSS embedded in HTML
                    "js": ""    # JS embedded in HTML
                }
                
                # Send final code event with proper state management
                yield self._create_sse_event_with_state("code", game_data, {
                    'current_game': game_data,
                    'last_action': 'game_creation'
                })
        
        # Send features
        if features_match:
            features_text = features_match.group(1).strip()
            if features_text:
                yield self._create_sse_event("features", features_text)
        
        # Send suggestions
        if suggestions_match:
            suggestions_text = suggestions_match.group(1).strip()
            if suggestions_text:
                yield self._create_sse_event("suggestions", suggestions_text)

    def _create_enhanced_prompt(self, user_prompt: str, current_game: dict, is_follow_up: bool) -> str:
        """Create enhanced prompt with conversation context."""
        if is_follow_up and current_game:
            return f"""The user wants to modify a game you have already created.

PREVIOUS GAME CODE:
```html
{current_game.get('html', '')}
```

USER'S NEW REQUEST:
"{user_prompt}"

Your task is to generate the complete, updated game code based on this new request, following the standard format with ## Building Your Game, ```html code block, and ## Game Features sections."""
        else:
            return user_prompt
    
    
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
    
    def _create_sse_event_with_state(self, event_type: str, payload, state_delta: dict) -> Event:
        """Create SSE event with proper ADK state management."""
        return Event(
            author="agent",
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=json.dumps({'type': event_type, 'payload': payload})
                    )
                ]
            ),
            actions=EventActions(state_delta=state_delta)
        )

# Create the game creator agent instance
game_creator_agent = GameCreatorAgent()