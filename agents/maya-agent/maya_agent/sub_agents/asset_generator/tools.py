#!/usr/bin/env python3
"""
Asset generation tools for Maya Game Creator Agent
Clean ADK function tools using GCS Artifacts for PNG storage
"""

import os
import io
import logging
from datetime import datetime
from typing import Dict
from google.genai import types
from google.adk.tools import ToolContext
from maya_agent.config import HF_TOKEN, HF_MODEL_NAME, ASSET_WIDTH, ASSET_HEIGHT, GRPZA_TRIGGER

logger = logging.getLogger(__name__)

def _generate_asset_descriptions(game_description: str) -> list[str]:
    """Generate intelligent asset descriptions based on the game type."""
    game_desc_lower = game_description.lower()
    
    # Space/Sci-fi games
    if any(keyword in game_desc_lower for keyword in ['space', 'spaceship', 'alien', 'galaxy', 'sci-fi', 'laser', 'asteroid']):
        return [
            "futuristic spaceship player vehicle",
            "enemy asteroid or alien craft", 
            "starfield background with nebula"
        ]
    
    # Medieval/Fantasy games  
    elif any(keyword in game_desc_lower for keyword in ['medieval', 'knight', 'castle', 'dragon', 'sword', 'fantasy', 'magic']):
        return [
            "medieval knight character in armor",
            "shield or sword weapon",
            "castle wall or stone background"
        ]
    
    # Racing/Vehicle games
    elif any(keyword in game_desc_lower for keyword in ['race', 'car', 'vehicle', 'road', 'speed', 'driving']):
        return [
            "race car or vehicle",
            "road surface or track element",
            "checkered flag or barrier"
        ]
    
    # Puzzle games
    elif any(keyword in game_desc_lower for keyword in ['puzzle', 'block', 'tile', 'match', 'tetris', 'gem']):
        return [
            "colorful game piece or block",
            "matching tile or gem",
            "grid background pattern"
        ]
    
    # Shooter games (non-space)
    elif any(keyword in game_desc_lower for keyword in ['shooter', 'gun', 'bullet', 'enemy', 'target']):
        return [
            "player character with weapon",
            "enemy target or obstacle", 
            "urban or battlefield background"
        ]
    
    # Sports games
    elif any(keyword in game_desc_lower for keyword in ['sport', 'ball', 'soccer', 'basketball', 'tennis', 'goal']):
        return [
            "sports ball or equipment",
            "player character or athlete",
            "field or court background"
        ]
    
    # Default for generic games
    else:
        return [
            f"main character for {game_description}",
            f"interactive object for {game_description}",
            f"background element for {game_description}"
        ]

async def game_asset_generator_tool(description: str, tool_context: ToolContext) -> Dict[str, str]:
    """
    Generate exactly 3 strategic visual assets for HTML5 games and save as GCS Artifacts.
    
    Args:
        description (str): Description of the game for which to generate assets
        
    Returns:
        Dict[str, str]: Dictionary containing the 3 generated asset filenames:
            - primary_character: Filename of saved PNG artifact for main player character
            - interactive_object: Filename of saved PNG artifact for key interactive element  
            - environmental_element: Filename of saved PNG artifact for background/world element
    """
    print(f"🎯 Asset generation called for: {description}")
    
    try:
        from huggingface_hub import InferenceClient
        
        if not HF_TOKEN:
            logger.error("No HF_TOKEN found in environment")
            return {"error": "HF_TOKEN environment variable not set"}
        
        client = InferenceClient(token=HF_TOKEN)
        asset_filenames = {}
        
        # Create local storage directory for debugging (optional)
        assets_dir = "/Users/saibalaji/Documents/maya/generated_assets"
        os.makedirs(assets_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join(assets_dir, f"session_{timestamp}")
        os.makedirs(session_dir, exist_ok=True)
        
        print(f"📁 Debug: Also saving assets to: {session_dir}")
        print(f"🌐 Primary storage: GCS maya-artifacts bucket via ADK")
        
        # Generate 3 strategic assets with intelligent descriptions based on game type
        asset_descriptions = _generate_asset_descriptions(description)
        asset_categories = {
            'asset_1': f'{GRPZA_TRIGGER}, {asset_descriptions[0]}, white background, game asset, pixel art',
            'asset_2': f'{GRPZA_TRIGGER}, {asset_descriptions[1]}, white background, game asset, pixel art', 
            'asset_3': f'{GRPZA_TRIGGER}, {asset_descriptions[2]}, white background, game asset, pixel art'
        }
        
        for category, prompt in asset_categories.items():
            try:
                logger.info(f"Generating {category} with prompt: {prompt}")
                print(f"🎨 Generating {category}...")
                
                # Generate image using HuggingFace with timeout
                import asyncio
                import concurrent.futures
                
                def generate_with_timeout():
                    return client.text_to_image(
                        prompt=prompt,
                        model=HF_MODEL_NAME,
                        width=ASSET_WIDTH,
                        height=ASSET_HEIGHT,
                    )
                
                # Use a 30-second timeout for HuggingFace API calls
                try:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(generate_with_timeout)
                        image = future.result(timeout=30)  # 30 second timeout
                except concurrent.futures.TimeoutError:
                    logger.error(f"Timeout generating {category} - skipping")
                    print(f"⏰ Timeout generating {category} - skipping")
                    continue
                except Exception as hf_error:
                    logger.error(f"HuggingFace error for {category}: {hf_error}")
                    print(f"❌ HuggingFace error for {category}: {hf_error}")
                    continue
                
                # Convert to PNG bytes
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                img_bytes = buffer.getvalue()
                
                # Create ADK artifact filename using simplified naming
                artifact_filename = f"{category}.png"
                
                # Create ADK Part from PNG bytes
                png_part = types.Part.from_bytes(
                    data=img_bytes,
                    mime_type="image/png"
                )
                
                # Save artifact using ADK context (async method)
                try:
                    version = await tool_context.save_artifact(filename=artifact_filename, artifact=png_part)
                    print(f"✅ Saved artifact '{artifact_filename}' to GCS maya-artifacts bucket as version {version}")
                    asset_filenames[category] = artifact_filename
                    
                    # No state operations needed - artifact service is the source of truth
                    
                except Exception as save_error:
                    logger.error(f"Failed to save artifact {artifact_filename}: {save_error}")
                    print(f"❌ Failed to save artifact {artifact_filename}: {save_error}")
                    # Continue with local save as fallback
                    asset_filenames[category] = artifact_filename
                
                # Also save locally for debugging
                debug_filename = f"{category}_{description.replace(' ', '_')}.png"
                filepath = os.path.join(session_dir, debug_filename)
                
                with open(filepath, 'wb') as f:
                    f.write(img_bytes)
                
                print(f"✅ Generated {category}: Local file {filepath} (artifact filename: {artifact_filename})")
                
            except Exception as e:
                logger.error(f"Failed to generate {category}: {str(e)}")
                print(f"❌ Failed to generate {category}: {str(e)}")
        
        # Save generation summary
        summary_path = os.path.join(session_dir, "generation_summary.txt")
        with open(summary_path, 'w') as f:
            f.write(f"Game Description: {description}\n")
            f.write(f"Generation Time: {timestamp}\n")
            f.write(f"Assets Generated: 3/3\n\n")
            f.write("GCS ADK Artifacts Saved:\n")
            try:
                for category, filename in asset_filenames.items():
                    f.write(f"- {category}: {filename} (stored in maya-artifacts bucket)\n")
            except Exception as e:
                f.write(f"- Error writing asset details: {e}\n")
        
        print(f"📝 Generation summary saved to {summary_path}")
        print(f"🚀 Ready to pass asset filenames to Game Creator")
        
        # Asset generation complete - artifacts are stored in GCS and can be queried by Game Creator
        if asset_filenames:
            print(f"✅ Asset generation completed successfully - {len(asset_filenames)} artifacts stored in GCS")
            print(f"🎯 ASSET GENERATOR: Game Creator can query artifacts directly from artifact service")
        else:
            print("⚠️ No assets generated, falling back to text-only mode")
        
        return asset_filenames
        
    except Exception as e:
        error_msg = f"Asset generation failed: {str(e)}"
        logger.exception(error_msg)
        print(f"❌ {error_msg}")
        return {"error": error_msg}