# Product Requirements Document: Maya AI Frontend (V2)

## 1. Overview

This document outlines the product requirements for the frontend of the Maya AI game creation platform. The frontend is a web-based interface that allows users to interact with the Maya AI to generate, preview, and iterate on browser-based games. The user experience must be highly dynamic and responsive, providing real-time feedback of the AI's thought process and actions, all within a distinct cyberpunk aesthetic.

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

The entry point to the application, designed to be immersive and encourage creativity.

-   **Immersive Background:** A dynamic, animated 3D background that aligns with the cyberpunk and game-creation theme.
-   **Central Prompt Input:** A large, central text area for the user to enter their game idea.
-   **Submission & Navigation:** On submission (click or Enter), a "Creating project..." modal is displayed briefly, and then the user is navigated to the `/session` route, passing the prompt text.
-   **Game Templates:** The page will display cards for starting from templates.

### 3.2. Session Page (`/session`)

The main workspace for AI interaction and game creation. It features a two-panel layout.

#### 3.2.1. Left Panel: Live Chat Interface

This panel displays a real-time, streaming conversation with the Maya AI.

-   **Stateful Conversation:** The chat history is maintained in the application's state.
-   **Initial State:** The user's prompt from the Home Page is the first message. The AI immediately responds with an introductory message (e.g., "Analyzing...").
-   **Live AI Feedback:** The AI's message bubble will have several states:
    -   **Thinking:** A "Thinking..." message with an animated indicator will be shown while the AI is processing.
    -   **Streaming Response:** The AI's thoughts, plans, and code generation commands (e.g., `<createFile file="main.js">`) will be streamed into the message bubble token by token, providing a live view of its work.
-   **Suggested Prompts:** After a generation is complete, the AI will suggest the next logical step or enhancement as a clickable prompt.
-   **Iterative Input:** The user can type follow-up prompts to modify the existing game.

#### 3.2.2. Right Panel: Game Workspace

This panel is for viewing the output of the AI's generation.

-   **Tabbed Interface:** The panel will have three tabs: "Preview," "Assets," and "Code."
-   **Initial State:** On first load, the "Preview" tab is active and displays an empty state.
-   **Live Preview Update:** The game preview in the `iframe` will be updated in real-time as the AI generates and modifies the code.
-   **Assets Tab:** Displays a list of assets used in the game. This will be populated based on the AI's generation output.
-   **Code Tab:** Displays the complete, final code for the generated game.

## 4. Technical Requirements

-   **Framework:** React (v18) with Vite
-   **Language:** TypeScript
-   **Styling:** Tailwind CSS with `shadcn/ui`.
-   **3D Graphics:** `three.js` with `@react-three/fiber` and `@react-three/drei` for the Home Page background.
-   **State Management:**
    -   React Router state for passing the initial prompt.
    -   A client-side state management solution (React Context or a lightweight library) is required to manage the complex session state (chat history, game code, AI status, etc.).
-   **API Communication:**
    -   The API client must support **streaming** to handle the real-time responses from the backend.
    -   The frontend will send the initial prompt and subsequent iterative prompts to the backend.
    -   It will receive a stream of text and commands from the backend, which it will parse and display in the chat interface. The final output will include the full game code to be rendered in the preview.

## 5. Out of Scope for V1

-   User accounts and project saving.
-   Real-time collaborative editing.
-   Manual asset uploading.
-   Game sharing functionality.