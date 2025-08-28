#!/usr/bin/env python3
"""
Asset generation tool for Maya Game Creator Agent
Uses HuggingFace API to generate game assets
"""

import os
import io
import base64
import logging
from typing import Optional
from pydantic import BaseModel
from huggingface_hub import InferenceClient
from maya_agent.config import HF_TOKEN, HF_MODEL_NAME, ASSET_WIDTH, ASSET_HEIGHT, GRPZA_TRIGGER

logger = logging.getLogger(__name__)

# Simple call counter to enforce 1 asset per session
_call_count = 0


class GenerateAssetInput(BaseModel):
    """Input for generate_game_asset tool"""
    prompt: str

class GenerateAssetOutput(BaseModel):
    """Output for generate_game_asset tool"""
    success: bool
    base64_image: Optional[str] = None
    error: Optional[str] = None

def _generate_asset_direct(prompt: str) -> str:
    """Direct asset generation without rate limiting - for strategic asset generation"""
    try:
        if not HF_TOKEN:
            logger.error("No HF_TOKEN found in environment")
            return "ERROR: HF_TOKEN environment variable not set"
        
        client = InferenceClient(token=HF_TOKEN)
        
        logger.info(f"Generating asset with Flux model: {prompt}")
        
        # Make the API call
        image = client.text_to_image(
            prompt=prompt,
            model=HF_MODEL_NAME,
            width=ASSET_WIDTH,
            height=ASSET_HEIGHT,
        )
        
        # Convert PIL Image to base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        base64_string = base64.b64encode(img_bytes).decode('utf-8')
        
        logger.info(f"✅ Successfully generated asset: {len(base64_string)} chars")
        return base64_string
        
    except Exception as e:
        logger.error(f"Failed to generate asset: {str(e)}")
        return f"ERROR: Failed to generate asset - {str(e)}"

def generate_game_asset(prompt: str) -> str:
    """
    Generate a game asset using HuggingFace Flux-2D-Game-Assets-LoRA model
    
    Args:
        prompt: Description of the asset to generate
        
    Returns:
        Base64 encoded image data or error message
    """
    global _call_count
    
    try:
        _call_count += 1
        logger.info(f"Asset generation call #{_call_count} for: {prompt}")
        
        # Hard limit: only allow 1 asset generation call
        if _call_count > 1:
            logger.info("Blocking additional asset generation - limit reached")
            return "ERROR: Only 1 asset per game allowed. Use existing CSS styling for other elements."
        
        logger.info(f"Generating game asset for: {prompt}")
        
        # Set up HuggingFace client
        if not HF_TOKEN:
            logger.error("No HF_TOKEN found in environment")
            return "ERROR: HF_TOKEN environment variable not set"
        
        client = InferenceClient(token=HF_TOKEN)
        
        # Enhance prompt for game assets with GRPZA trigger if not present
        if not prompt.startswith(GRPZA_TRIGGER):
            enhanced_prompt = f"{GRPZA_TRIGGER}, {prompt}, white background, game asset, pixel art"
        else:
            enhanced_prompt = prompt
        
        logger.info(f"Enhanced prompt: {enhanced_prompt}")
        
        # Generate image
        image = client.text_to_image(
            prompt=enhanced_prompt,
            model=HF_MODEL_NAME,
            width=ASSET_WIDTH,
            height=ASSET_HEIGHT,
        )
        
        # Convert to base64
        img_buffer = io.BytesIO()
        image.save(img_buffer, format="PNG")
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
        
        logger.info(f"✅ Asset generated successfully. Base64 length: {len(img_base64)}")
        
        return img_base64
        
    except Exception as e:
        error_msg = f"Failed to generate asset: {str(e)}"
        logger.error(error_msg)
        
        return f"ERROR: {error_msg}"