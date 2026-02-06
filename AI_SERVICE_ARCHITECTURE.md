# AI Service Architecture Documentation

## Overview
The Core Chat Orchestrator implements an AI service that connects user interactions, database context, and OpenAI API to provide intelligent, context-aware responses for productivity assistance.

## Service Components

### 1. AIService Class
Located in `backend/src/services/ai_service.py`, this class orchestrates communication between user, database context, and OpenAI API.

#### Key Methods:
- **`get_user_context()`**: Fetches user's current tasks and categories from database
- **`get_conversation_history()`**: Retrieves last 10 messages from conversation for context
- **`format_ai_prompt()`**: Structures system prompt, user context, and conversation history for AI
- **`process_message()`**: Main orchestration method that coordinates all other methods

### 2. API Integration
Located in `backend/src/api/messages.py`, the POST `/api/messages/` endpoint now uses the AI service to process user messages and generate intelligent responses.

## Data Flow Architecture

### Message Processing Flow
1. **User Message Arrival**: User sends message via POST `/api/messages/`
2. **Initial Persistence**: User message is immediately saved to database to ensure persistence
3. **Context Assembly**:
   - Fetch user's current tasks and categories
   - Fetch last 10 messages from conversation
   - Combine elements into structured context
4. **AI API Call**: Prepare formatted prompt and call OpenAI API with gpt-4o model
5. **Response Persistence**: Save AI response to database
6. **Return Response**: Send AI response back to user

## Security & Isolation

### User Context Security
- All database queries filter by authenticated user's `user_id`
- Conversation access validation ensures users only access their own data
- Context injection only includes data belonging to the authenticated user

### Error Handling
- All OpenAI API failures are caught with specific exception handlers:
  - `AuthenticationError`: Configuration issues
  - `RateLimitError`: API availability issues
  - `APIConnectionError`: Connectivity issues
- User messages are persisted even when AI API calls fail
- Graceful degradation with helpful error messages

## Async Architecture
- All service methods that interact with external resources are async
- Database operations use proper async/await patterns
- No blocking operations to ensure responsive user experience

## Integration Points

### Database Layer
- Fetch user's tasks and categories using SQLModel queries
- Save user messages before AI processing
- Save AI responses after successful API calls

### API Layer
- Receive message content from POST `/api/messages/` endpoint
- Handle authentication through existing JWT system
- Return AI response content to user

### OpenAI Service
- Use `AsyncClient` for non-blocking API calls
- Format prompts according to OpenAI API requirements
- Handle response format according to OpenAI API specifications

## Key Design Patterns

### Message Persistence First
- User messages are saved to database BEFORE AI API calls
- Ensures message persistence regardless of AI processing success/failure

### Context Injection
- System prompt defines AI persona as "proactive Productivity Assistant"
- Dynamic context includes current tasks, categories, and conversation history
- Structured format ensures AI understands different context elements

### Graceful Degradation
- When AI API is unavailable, user messages are still saved
- Informative error messages returned to users
- Minimal context used when fetching context fails

## Environment Configuration
- Requires `OPENAI_API_KEY` environment variable for API access
- Uses gpt-4o model as specified in requirements
- Temperature setting of 0.7 for balanced creativity/relevance

## Error Recovery Strategy
- Message persistence is guaranteed regardless of AI API success
- Context fetching failures are handled gracefully with fallback values
- All error scenarios maintain data integrity and system stability