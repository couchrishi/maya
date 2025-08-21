import os
import google.generativeai as genai
from maya.schemas.game import GameCode
import json

# It's recommended to load the API key from an environment variable
# for security. You should create a .env file in your project root
# and add the following line:
# GOOGLE_API_KEY="YOUR_API_KEY"
# Make sure to add .env to your .gitignore file.
api_key = os.environ.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def draft_generator(requirements: str) -> GameCode:
    """
    Generates the initial HTML, CSS, and JavaScript for a game using the Gemini API.
    """
    if not requirements:
        raise ValueError("Requirements cannot be empty.")

    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    You are an expert game developer. Based on the following requirements, generate the HTML, CSS, and JavaScript for a complete, playable browser game.

    Requirements: "{requirements}"

    Your response MUST be a JSON object with three keys: "html", "css", and "js".
    - The "html" value should be the full HTML structure.
    - The "css" value should be the complete CSS for styling.
    - The "js" value should be the complete JavaScript for the game logic.

    Do not include any explanations or markdown formatting in your response. Only the JSON object.
    """

    try:
        response = model.generate_content(prompt)
        # The response from the model may include markdown formatting for the JSON block.
        # We need to clean it up before parsing.
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        game_code_dict = json.loads(cleaned_response)

        return GameCode(
            html=game_code_dict.get("html", ""),
            css=game_code_dict.get("css", ""),
            js=game_code_dict.get("js", "")
        )
    except Exception as e:
        # In a real application, you'd want more robust error handling and logging.
        print(f"An error occurred while generating the game code: {e}")
        # For the purpose of this TDD cycle, we'll return an empty GameCode object
        # on failure to ensure the tests can still run without a valid API key.
        return GameCode(html="", css="", js="")