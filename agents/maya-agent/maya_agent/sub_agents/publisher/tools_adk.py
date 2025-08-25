# Simple Firebase CLI tools for game publishing

import json
import tempfile
import subprocess
import random
import string
from pathlib import Path
from typing import List
from google.adk.tools import ToolContext
from .schemas import FirebaseConfig


def generate_site_name(game_prompt: str, tool_context: ToolContext) -> str:
    """Generate a unique, web-friendly site name from game description"""
    import re
    
    # Extract key words from game prompt
    words = re.findall(r'\b\w+\b', game_prompt.lower())
    
    # Filter out common words
    stop_words = {'game', 'create', 'make', 'a', 'an', 'the', 'with', 'and', 'or', 'but'}
    meaningful_words = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Take first 2-3 meaningful words
    base_name = '-'.join(meaningful_words[:3])
    
    # Fallback if no meaningful words found
    if not base_name:
        base_name = 'maya-game'
    
    # Add random suffix for uniqueness
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    
    site_name = f"{base_name}-{suffix}"
    
    # Ensure valid Firebase site name (lowercase, hyphens, no spaces)
    site_name = re.sub(r'[^a-z0-9-]', '', site_name)
    site_name = re.sub(r'-+', '-', site_name)  # Remove duplicate hyphens
    site_name = site_name.strip('-')  # Remove leading/trailing hyphens
    
    return site_name

def publish_game(game_prompt: str, tool_context: ToolContext) -> dict:
    """Publish HTML5 game to Firebase Hosting using Firebase CLI"""
    firebase_config = FirebaseConfig()
    
    try:
        # Get game data from session state
        current_game = tool_context.state.get('current_game')
        if not current_game:
            return {
                "success": False,
                "live_url": "",
                "site_name": "",
                "message": "No current game found in session. Please create a game first."
            }
        
        # Validate that we have the required game data
        if not isinstance(current_game, dict) or 'html' not in current_game:
            return {
                "success": False,
                "live_url": "",
                "site_name": "",
                "message": "Invalid game data format in session."
            }
        
        # Get the complete HTML (CSS and JS are embedded)
        complete_html = current_game.get('html', '')
        if not complete_html.strip():
            return {
                "success": False,
                "live_url": "",
                "site_name": "",
                "message": "No game HTML content found. Please create a game first."
            }
        
        # Generate site name
        site_name = generate_site_name(game_prompt, tool_context)
        
        # Create temporary directory for deployment
        with tempfile.TemporaryDirectory() as temp_dir:
            deploy_dir = Path(temp_dir)
            
            # Use the complete HTML directly (CSS/JS already embedded)
            index_html = complete_html
            
            # Write the HTML file
            with open(deploy_dir / "index.html", 'w') as f:
                f.write(index_html)
            
            # Create firebase.json configuration
            firebase_config_content = {
                "hosting": {
                    "site": site_name,
                    "public": ".",
                    "ignore": [
                        "firebase.json",
                        "**/.*",
                        "**/node_modules/**"
                    ],
                    "rewrites": [{
                        "source": "**",
                        "destination": "/index.html"
                    }]
                }
            }
            
            with open(deploy_dir / "firebase.json", 'w') as f:
                json.dump(firebase_config_content, f, indent=2)
            
            # Set Firebase project context
            try:
                subprocess.run([
                    "firebase", "use", firebase_config.project_id
                ], cwd=deploy_dir, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                return {
                    "success": False,
                    "live_url": "",
                    "site_name": "",
                    "message": f"Failed to set Firebase project: {e.stderr.decode()}"
                }
            
            # Create hosting site
            try:
                subprocess.run([
                    "firebase", "hosting:sites:create", site_name,
                    "--project", firebase_config.project_id
                ], cwd=deploy_dir, check=True, capture_output=True)
            except subprocess.CalledProcessError:
                # Site might already exist, continue
                pass
            
            # Deploy to Firebase
            try:
                subprocess.run([
                    "firebase", "deploy",
                    "--project", firebase_config.project_id
                ], cwd=deploy_dir, check=True, capture_output=True, text=True)
                
                # Generate live URL
                live_url = f"https://{site_name}.web.app"
                
                return {
                    "success": True,
                    "message": f"🎉 Your game is now live at {live_url}!",
                    "site_name": site_name,
                    "live_url": live_url
                }
                
            except subprocess.CalledProcessError as e:
                return {
                    "success": False,
                    "live_url": "",
                    "site_name": "",
                    "message": f"Deployment failed: {e.stderr.decode()}"
                }
    
    except Exception as e:
        return {
            "success": False,
            "live_url": "",
            "site_name": "",
            "message": f"Unexpected error: {str(e)}"
        }


def create_hosting_tools(firebase_config: FirebaseConfig) -> List:
    """Create essential Firebase hosting tools for the Publisher Agent"""
    return [publish_game]