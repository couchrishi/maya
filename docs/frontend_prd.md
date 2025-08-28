# Product Requirements Document: Maya AI Frontend (V3 - Comprehensive)

## 1. Overview

This document outlines the comprehensive product requirements for the frontend of the Maya AI game creation platform. The frontend is a web-based interface that allows users to interact with the Maya AI to generate, preview, and iterate on browser-based games. The user experience must be highly dynamic and responsive, providing real-time feedback of the AI's thought process and actions, all within a distinct cyberpunk aesthetic.

## 2. User Flow

The primary user journey is as follows:

1.  **Landing:** The user arrives at the immersive **Home Page**.
2.  **Prompting:** The user describes their game idea in a prominent input field and submits it.
3.  **Project Creation:** A modal appears, indicating that a new project is being set up.
4.  **Navigation:** The user is navigated to the **Session Page**.
5.  **Live Generation:** The user watches the AI's thought process and code generation stream in real-time in the chat panel.
6.  **Preview:** The generated game appears in the preview panel.
7.  **Iteration:** The user can provide follow-up prompts to modify and improve the game.

## 3. Key Features

### 3.1. Home Page (`/`)

-   **Immersive Background:** A dynamic, animated 3D background using `three.js`.
-   **Central Prompt Input:** A large, central text area for the user's game idea.
-   **Submission & Navigation:** On submission, a "Creating project..." modal is displayed, and the user is navigated to the `/session` route, passing the prompt text.
-   **Game Templates:** Clickable cards for starting from pre-defined game templates.

### 3.2. Session Page (`/session`)

A two-panel layout for AI interaction and game creation.

#### 3.2.1. Left Panel: Live Chat Interface

-   **Stateful Conversation:** The chat history is maintained in the application's state.
-   **Live AI Feedback:** The AI's message bubble will have multiple, distinct states, updated in real-time.
-   **Suggested Prompts:** After a generation, the AI will suggest the next logical step as a clickable prompt.
-   **Iterative Input:** A text input for follow-up prompts.

#### 3.2.2. Right Panel: Game Workspace

-   **Tabbed Interface:** "Preview," "Assets," and "Code."
-   **Live Preview Update:** The game preview `iframe` will be updated in real-time as the AI generates and modifies the code.
-   **Assets Tab:** Displays a list of assets used in the game.
-   **Code Tab:** Displays the complete, final code for the generated game.

## 4. Detailed UI States & API Contract

### 4.1. Component States

| Component         | State           | UI Representation                                                                                             |
| ----------------- | --------------- | ------------------------------------------------------------------------------------------------------------- |
| **ChatInterface** | `Idle`          | Standard welcome message. Input field is active.                                                              |
|                   | `Thinking`      | A message bubble with an animated "Thinking..." indicator appears. Input field is disabled.                   |
|                   | `Streaming`     | The AI's message bubble is populated token-by-token. The text cursor blinks at the end of the stream.         |
|                   | `Suggestion`    | After a successful generation, clickable "Suggested next step" buttons appear.                               |
| **GamePanel**     | `Empty`         | "Preview" tab shows a "Ready to Create" message with an icon. "Code" tab shows "No Code Yet".                 |
|                   | `Generating`    | "Preview" and "Code" tabs show a "Generating..." loading indicator.                                           |
|                   | `Success`       | "Preview" tab renders the game in an `iframe`. "Code" tab displays the full, formatted code.                  |
|                   | `Error`         | "Preview" tab shows an error message. A toast notification appears with the error details.                    |

### 4.2. Streaming API Contract

The frontend expects to receive a stream of Server-Sent Events (SSE) from the backend. Each event will be a JSON object with a `type` and a `payload`.

| Type         | Payload                                                              | Description                                                                                             |
| ------------ | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `status`     | `"thinking"` or `"generating"`                                       | Informs the frontend of the AI's current high-level status, used to control UI states.                  |
| `chunk`      | A string of text (e.g., `"Here's my plan:\n"`)                        | A token or chunk of the AI's natural language response to be appended to the current message bubble.    |
| `command`    | A string representing a file operation (e.g., `<createFile ...>`)    | A command to be displayed in the chat, showing the AI's actions.                                        |
| `code`       | `{ "html": "...", "css": "...", "js": "..." }`                        | The final, complete game code. This event signals the end of a successful generation.                   |
| `error`      | A string with the error message (e.g., `"Failed to generate code."`) | Signals that an error has occurred. The payload should be displayed in a toast and the GamePanel.       |

## 5. Technical Requirements

-   **Framework:** React (v18) with Vite
-   **Language:** TypeScript
-   **Styling:** Tailwind CSS with `shadcn/ui`.
    -   **Fonts:** `Orbitron` for headings, `Rajdhani` for body text.
    -   **Icons:** `lucide-react`.
-   **3D Graphics:** `three.js` with `@react-three/fiber` and `@react-three/drei`.
-   **State Management:** React Context for session state.
-   **API Communication:** A dedicated API client using the native `fetch` API to handle the SSE stream.

## 6. Out of Scope for V1

-   User accounts and project saving.
-   Manual asset uploading.
-   Game sharing functionality.
