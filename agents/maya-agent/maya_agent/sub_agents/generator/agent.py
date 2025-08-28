# /agents/maya-agent/maya_agent/sub_agents/generator/agent.py
from google.adk.agents import LlmAgent
from google.adk.events.event import Event
from google.adk.events import EventActions
from google.genai import types
from .prompts import GENERATOR_INSTRUCTIONS_BASIC, GENERATOR_INSTRUCTIONS_WITH_ASSETS
from .streaming import StreamingContentProcessor
from maya_agent.config import FAST_MODEL_NAME
import json
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


class GameCreatorAgent(LlmAgent):
    """
    Game creation agent that checks artifact service for assets and switches instructions accordingly.
    - If assets found in artifact service -> use GENERATOR_INSTRUCTIONS_WITH_ASSETS
    - If no assets found -> use GENERATOR_INSTRUCTIONS_BASIC
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="game_creator_agent",
            instruction=GENERATOR_INSTRUCTIONS_BASIC,  # Default instruction
            model=FAST_MODEL_NAME,
            tools=[],
            before_model_callback=self._before_model_callback,
            **kwargs
        )
    
    async def _run_async_impl(self, context, **kwargs) -> AsyncGenerator[Event, None]:
        """
        Main execution logic for game creation with proper streaming and SSE events.
        """
        # Extract user prompt from context
        user_prompt = self._extract_user_prompt(context)
        
        # Check session state for conversation context
        session_state = context.session.state
        current_game = session_state.get('current_game', None)
        conversation_history = session_state.get('conversation_history', [])
        
        # Yield initial status
        yield self._create_sse_event("status", "thinking")
        
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
    
    async def _before_model_callback(self, callback_context, llm_request):
        """
        Callback to check artifact service for assets and create multimodal content.
        - If assets found -> load PNG files and create multimodal content for LLM analysis
        - If no assets found -> use GENERATOR_INSTRUCTIONS_BASIC
        """
        try:
            # Check artifact service for asset filenames
            artifacts = await callback_context.list_artifacts()
            # Handle both string and object formats
            if artifacts and isinstance(artifacts[0], str):
                asset_filenames = [artifact for artifact in artifacts if artifact.endswith('.png')]
            else:
                asset_filenames = [artifact.name for artifact in artifacts if hasattr(artifact, 'name') and artifact.name.endswith('.png')]
            
            logger.info(f"🔍 CALLBACK: Found {len(asset_filenames)} asset files: {asset_filenames}")
            
            if asset_filenames:
                logger.info("🎨 CALLBACK: Assets detected - loading files for multimodal analysis")
                llm_request.config.system_instruction = GENERATOR_INSTRUCTIONS_WITH_ASSETS
                
                # Load actual asset files from artifact service
                asset_parts = []
                
                if hasattr(llm_request, 'contents') and llm_request.contents:
                    user_content = llm_request.contents[0]
                    
                    # Keep original text prompt
                    if user_content.parts and user_content.parts[0].text:
                        original_prompt = user_content.parts[0].text
                        
                        # Create enhanced text with asset context
                        enhanced_prompt = f"""{original_prompt}

VISUAL ASSETS PROVIDED:
I'm providing {len(asset_filenames)} PNG images created specifically for this game. Examine each image carefully and RECREATE them using code-based graphics (CSS/HTML/JavaScript). Do not use <img> tags or external URLs - recreate the visual elements using only code."""
                        
                        # Start with enhanced text part
                        asset_parts.append(types.Part(text=enhanced_prompt))
                        
                        # Load and add each asset as image part
                        for filename in asset_filenames:
                            try:
                                # Load artifact as types.Part directly from ADK artifact service
                                image_part = await callback_context.load_artifact(filename)
                                
                                if image_part:
                                    asset_parts.append(image_part)
                                    logger.info(f"🖼️ CALLBACK: Loaded asset {filename}")
                                else:
                                    logger.warning(f"🚫 CALLBACK: Asset {filename} not found")
                                    
                            except Exception as asset_error:
                                logger.error(f"🚫 CALLBACK: Error loading asset {filename}: {asset_error}")
                        
                        # Replace user content with multimodal parts
                        user_content.parts = asset_parts
                        logger.info(f"🎨 CALLBACK: Created multimodal content with {len(asset_parts)} parts (1 text + {len(asset_parts)-1} images)")
                        
            else:
                logger.info("📝 CALLBACK: No assets found - using basic instructions")
                llm_request.config.system_instruction = GENERATOR_INSTRUCTIONS_BASIC
                
        except Exception as e:
            logger.error(f"🔍 CALLBACK: Error in multimodal callback: {e}")
            # Fallback to basic instructions on error
            llm_request.config.system_instruction = GENERATOR_INSTRUCTIONS_BASIC
        
        return None  # Allow LLM to proceed
    
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