# Plan: Chat UI (Phase 5)

This document outlines the architectural plan for implementing the Chat UI, focusing on component hierarchy, styling strategy, and state management.

## 1. Architecture Overview

The Chat UI will be implemented as a modular React application, integrating seamlessly into the existing dashboard. It will primarily consist of a floating chat bubble that toggles the visibility of a full chat panel. Communication with the AI backend will be handled through dedicated service functions, wrapped by OpenAI ChatKit hooks for real-time updates.

## 2. Component Hierarchy

The UI will follow a clear, hierarchical component structure, promoting reusability and maintainability.

-   **`ChatWidget` (Root Component)**:
    -   Location: `frontend/src/components/chat/ChatWidget.tsx`
    -   Purpose: Renders the floating chat bubble icon in the bottom-right corner of the screen. Manages the open/closed state of the `ChatPanel`.
    -   Children: `ChatBubbleIcon`, `ChatPanel` (conditionally rendered).
    -   Interactions: Click on `ChatBubbleIcon` toggles `ChatPanel` visibility.

-   **`ChatPanel`**:
    -   Location: `frontend/src/components/chat/ChatPanel.tsx`
    -   Purpose: The main chat interface, containing message history, input field, and action buttons. Handles API calls for fetching history and sending messages.
    -   Children: `MessageList`, `ChatInput`, `ActionButton` (for tools/settings).
    -   Interactions: Renders `MessageList` for conversation history, passes message submission to `ChatInput`.

-   **`MessageList`**:
    -   Location: `frontend/src/components/chat/MessageList.tsx`
    -   Purpose: Displays individual chat messages. Manages auto-scrolling to the latest message.
    -   Children: `ChatMessage` (one for each message).
    -   Props: `messages` (array of message objects).

-   **`ChatMessage`**:
    -   Location: `frontend/src/components/chat/ChatMessage.tsx`
    -   Purpose: Renders a single chat message (user or AI). Handles Markdown rendering for AI messages.
    -   Props: `message` (object with content, sender, timestamp).

-   **`ChatInput`**:
    -   Location: `frontend/src/components/chat/ChatInput.tsx`
    -   Purpose: Provides a text input field for the user to type messages. Includes a send button.
    -   Interactions: Emits `onSendMessage` event with message content.

-   **`ThinkingIndicator`**:
    -   Location: `frontend/src/components/chat/ThinkingIndicator.tsx`
    -   Purpose: Displays a visual cue (pulse/typing animation) when the AI is processing.
    -   Props: `isThinking` (boolean).

-   **`ErrorDisplay` (Global/Context-driven)**:
    -   Location: `frontend/src/components/common/ErrorDisplay.tsx` (or similar, leveraged by a global context)
    -   Purpose: Displays toast or chat-bubble alerts for errors (e.g., unauthorized access, connection timeouts).

## 3. Styling Strategy

-   **Tailwind CSS**: All styling will be implemented using Tailwind CSS utility classes. This ensures consistency with the existing dashboard's theme and promotes rapid UI development.
-   **Theming**: Customizations will be applied via `tailwind.config.js` to ensure brand consistency. No custom CSS files will be introduced for component-specific styling.
-   **Icons**: All icons will be sourced from `lucide-react` to maintain a unified visual language.

## 4. State Management Strategy

The application's state will be managed using a combination of React's built-in hooks (`useState`, `useContext`, `useReducer`) and potentially a centralized state management library if complexity increases. OpenAI ChatKit's hooks will abstract much of the real-time message handling.

-   **Local Component State**: `useState` will be used for UI-specific states (e.g., `ChatWidget`'s `isOpen` state, `ChatInput`'s `message` text).
-   **Context API for Global State (Optional, for now)**: For broader states like user authentication status or global error notifications, React Context API might be used. However, the plan is to initially rely on prop drilling and ChatKit's provided context/hooks.
-   **OpenAI ChatKit Hooks**:
    -   `useChat()`: Central hook for managing conversation history, sending messages, and handling AI responses. This will likely abstract the direct API calls to the backend.
    -   `useToolCalls()`: To monitor and react to AI tool execution (e.g., triggering dashboard refresh).
-   **Data Fetching/Mutation**:
    -   Initial conversation history will be fetched using `useEffect` with a dedicated service function wrapped by ChatKit.
    -   Message sending will trigger mutations via ChatKit's provided functions, which will then interact with our backend API.
-   **Error Handling State**: Errors will be captured locally (e.g., `useState` in `ChatPanel`) and propagated to a global error display mechanism (e.g., a toast notification system) if they are critical and require user attention.

## 5. API Integration

-   The Chat UI will interact with the existing backend API endpoint for chat, which in turn utilizes `backend/src/services/ai_service.py`.
-   A dedicated `frontend/src/services/chatService.ts` (or similar) will encapsulate direct API calls, if any, made outside of ChatKit's abstraction.

## 6. Development Workflow

-   **Modular Development**: Each component will be developed and tested in isolation where possible.
-   **Storybook (Optional)**: Consider using Storybook for isolated component development and documentation if time permits.
-   **Incremental Integration**: Start with `ChatWidget` and `ChatPanel`, then integrate `MessageList` and `ChatInput`. Finally, connect to the backend API.