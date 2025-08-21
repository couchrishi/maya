# /agents/maya/prompts.py

MAYA_AGENT_INSTRUCTIONS = """
Generate a browser-based game using only HTML, CSS, and JavaScript.

Your output MUST be a single, valid JSON object with three keys: "html", "css", and "js".
Do not include any other text, explanations, or markdown.

EXAMPLE OUTPUT:
```json
{
  "html": "<!DOCTYPE html><html><body>...</body></html>",
  "css": "body { ... }",
  "js": "console.log('hello');"
}
```
"""

ITERATIVE_INSTRUCTIONS = """
Update the provided game code based on the user's request.

PREVIOUS CODE:
{previous_code}

USER REQUEST:
"{user_prompt}"

Your output MUST be a single, valid JSON object with the complete, updated code.
"""
