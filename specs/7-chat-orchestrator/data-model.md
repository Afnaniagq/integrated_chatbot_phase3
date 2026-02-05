# Data Model & Service Design: Core Chat Orchestrator

## Overview
This document defines the service architecture and data flow for the AI orchestrator service that connects database context with the OpenAI API.

## Service Architecture

### AIService Class Design

**Class Name**: AIService
**Responsibility**: Orchestrate communication between user, database context, and OpenAI API

#### Methods:

1. **Constructor** (`__init__`):
   - Parameters: database session, OpenAI API key
   - Initializes OpenAI AsyncClient with API key from environment
   - Sets up configuration for AI calls

2. **get_user_context** (async):
   - Parameters: user_id
   - Returns: Dictionary containing user's tasks and categories
   - Purpose: Fetches user's current tasks and categories to inject into AI context
   - Implementation: Query database for user's active tasks and categories

3. **get_conversation_history** (async):
   - Parameters: conversation_id
   - Returns: List of last 10 messages from the conversation
   - Purpose: Retrieves recent conversation history to maintain context
   - Implementation: Query database for recent messages in conversation ordered by timestamp

4. **process_message** (async):
   - Parameters: user_id, conversation_id, user_message_content
   - Returns: AI response content
   - Purpose: Main orchestration method that coordinates all other methods
   - Implementation:
     - Save user message to database
     - Fetch user context (tasks, categories)
     - Fetch conversation history (last 10 messages)
     - Prepare AI prompt with combined context
     - Call OpenAI API with structured prompt
     - Save AI response to database
     - Return AI response content

5. **format_ai_prompt**:
   - Parameters: system_prompt, user_context, conversation_history, new_message
   - Returns: Formatted string for AI API call
   - Purpose: Structures all context elements into proper format for AI
   - Implementation: Combines system prompt with user context and conversation history

## Data Flow Design

### Message Processing Flow

1. **User Message Arrival**:
   - User sends message via POST /api/messages/
   - Message is validated and prepared for AI processing

2. **Initial Persistence**:
   - User message is immediately saved to database
   - This ensures message persistence even if AI processing fails

3. **Context Assembly**:
   - Fetch user's current tasks and categories from database
   - Fetch last 10 messages from current conversation
   - Combine all elements into structured context

4. **AI API Call**:
   - Prepare formatted prompt with system instructions, user context, conversation history, and new message
   - Call OpenAI API with gpt-4o model
   - Handle any API errors gracefully

5. **Response Persistence**:
   - Save AI response to database as a message with role="assistant"
   - Return AI response to user

## Data Structures

### User Context Structure
```python
{
  "tasks": [
    {
      "id": UUID,
      "title": str,
      "description": str,
      "priority": str,
      "category": str,
      "is_completed": bool,
      "due_date": datetime
    }
  ],
  "categories": [
    {
      "id": UUID,
      "name": str
    }
  ]
}
```

### Conversation History Structure
```python
[
  {
    "role": "user" or "assistant",
    "content": str,
    "timestamp": datetime
  }
]
```

### AI Prompt Structure
```
SYSTEM PROMPT: "You are a proactive Productivity Assistant. You have access to the user's current task list and help them organize, prioritize, and manage their time."

USER CONTEXT:
- Current Tasks: [list of active tasks with titles and priorities]
- Categories: [list of user-defined categories]

CONVERSATION HISTORY:
[Recent messages with roles and content]

NEW MESSAGE: {user's current message}

RESPONSE:
```

## Error Handling Design

### Types of Errors and Responses

1. **Database Connection Errors**:
   - During user message save: Return 500 error immediately
   - During context retrieval: Return 500 error with message saved
   - During AI response save: Log error but still return response to user

2. **OpenAI API Errors**:
   - AuthenticationError: Log error, return 500 with message still saved
   - RateLimitError: Return 429, message still saved
   - ConnectionError: Return 500, message still saved
   - General Exception: Log error, return 500, message still saved

3. **Graceful Degradation**:
   - If AI service fails, user message is still saved
   - If context retrieval fails partially, AI service still attempts with partial context
   - If history is too long, limit to most recent messages

## Integration Points

### With Database Layer
- Fetch user's tasks and categories using SQLModel queries
- Fetch conversation history using SQLModel queries
- Save user messages before AI processing
- Save AI responses after AI processing

### With API Layer
- Receive message content from POST /api/messages/ endpoint
- Return AI response content to user
- Handle authentication through existing JWT system

### With OpenAI Service
- Use AsyncClient for non-blocking API calls
- Format prompts according to OpenAI API requirements
- Handle response format according to OpenAI API responses

## Security Considerations

### Context Injection Security
- Only include data belonging to the authenticated user
- Validate user_id matches the authenticated user
- Prevent access to other users' tasks or conversations

### Message Content Validation
- Validate message content length to prevent extremely large payloads
- Sanitize input to prevent injection attacks in AI prompts
- Ensure proper role assignments in database (user vs assistant)

## Performance Considerations

### Context Size Optimization
- Limit tasks and categories to active/useful data
- Limit conversation history to last 10 messages
- Implement proper indexing for efficient database queries
- Cache frequently accessed context elements if needed