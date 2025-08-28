
# Firebase MCP Server Documentation

The **Firebase MCP server** enables AI-powered development tools (like Claude Desktop, Cursor, VS Code Copilot, etc.) to interface with your Firebase projects. Any tool that can act as an MCP client may connect to the MCP server.

## Key Capabilities

- Create and manage Firebase projects
- Manage Firebase Authentication users
- Work with Cloud Firestore and Firebase Data Connect
- Retrieve Firebase Data Connect schemas
- Understand security rules for Firestore and Cloud Storage
- Send messages with Firebase Cloud Messaging

Some tools integrate Gemini in Firebase to:
- Generate Data Connect schemas/operations
- Consult Gemini about Firebase products

> **Note:** Gemini in Firebase can produce plausible but inaccurate outputs. Validate all outputs before use—don’t use untrusted generated code in production. Avoid entering PII into chat.

---

## Before You Begin

1. **Install Node.js and npm** (latest versions recommended).
2. **Authenticate Firebase CLI**:

    ```
    npx -y firebase-tools@latest login --reauth
    ```

You must authenticate the CLI before starting the MCP server. An expired or invalid auth token will require reauthentication.

---

## Setting up the MCP Client

The MCP server works with any compatible MCP client using standard I/O (stdio). Here are setup examples for popular editors:

### Basic Configuration Template

Add this to your respective config file:

{
"mcpServers": {
"firebase": {
"command": "npx",
"args": ["-y", "firebase-tools@latest", "experimental:mcp"]
}
}
}

text

### Client-specific Setup

**Firebase Studio:**  
File: `.idx/mcp.json` (create if missing)

**Gemini CLI/Code Assist:**  
Files: `.gemini/settings.json` (project) or `~/.gemini/settings.json`

**Claude Desktop:**  
Edit `claude_desktop_config.json` via **Claude > Settings > Developer > Edit Config**

**Cline:**  
Edit `cline_mcp_settings.json` via MCP Servers icon > Configure MCP Servers

**Cursor:**  
File: `.cursor/mcp.json` (project) or `~/.cursor/mcp.json`

**VS Code Copilot:**  
File: `.vscode/mcp.json` (project)
"servers": {
"firebase": {
"type": "stdio",
"command": "npx",
"args": ["-y", "firebase-tools@latest", "experimental:mcp"]
}
}

text
Or for all projects, add to user settings:
"mcp": {
"servers": {
"firebase": {
"type": "stdio",
"command": "npx",
"args": ["-y", "firebase-tools@latest", "experimental:mcp"]
}
}
}

text

**Windsurf Editor:**  
File: `~/.codeium/windsurf/mcp_config.json`

---

### Optional Configuration

Add optional parameters as needed:
- `--dir ABSOLUTE_DIR_PATH`: Path to a directory containing `firebase.json`
- `--only FEATURE_1,FEATURE_2`: Comma-separated features to activate

Example:
"firebase": {
"command": "npx",
"args": [
"-y", "firebase-tools@latest", "experimental:mcp",
"--dir", "/Users/turing/my-project",
"--only", "auth,firestore,storage"
]
}

text

---

## MCP Server Capabilities

| Tool Name                     | Feature Group | Description                                                      |
|-------------------------------|--------------|------------------------------------------------------------------|
| firebase_get_project          | core         | Get info about the active Firebase project.                      |
| firebase_list_apps            | core         | List registered apps in current Firebase project.                |
| firebase_create_project       | core         | Create a new Firebase project.                                   |
| firebase_init                 | core         | Initialize selected Firebase features in workspace.              |
| firestore_list_collections    | firestore    | List collections from Firestore DB.                              |
| firestore_get_rules           | firestore    | Retrieve Firestore security rules.                               |
| firestore_validate_rules      | firestore    | Validate Firestore Rules for syntax and errors.                  |
| auth_get_user                 | auth         | Retrieve a user by email/UID.                                    |
| auth_list_users               | auth         | List all users in the project.                                   |
| dataconnect_generate_schema   | dataconnect  | Generate a Data Connect schema from a descriptive prompt.        |
| storage_get_rules             | storage      | Retrieve Storage security rules.                                 |
| messaging_send_message        | messaging    | Send a message via Firebase Cloud Messaging.                     |
| apphosting_fetch_logs         | apphosting   | Get recent App Hosting backend logs.                             |

*For a full list of capabilities, see the official documentation.*

---

## Licensing

- Documentation: [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/)
- Code samples: [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0/)
- Trademarks belong to their respective owners.

_Last updated: 2025-08-18 UTC_