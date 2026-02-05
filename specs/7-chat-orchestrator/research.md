# Research Findings: Core Chat Orchestrator

## Overview
This document captures the research findings for implementing the AI orchestrator service that connects the database context with the OpenAI API.

## Resolved Research Tasks

### 1. OpenAI Library Integration Patterns
**Finding**: OpenAI library v1.x uses a client-based approach with async methods
**Details**:
- Use `openai.AsyncClient` for async operations
- API call pattern: `await client.chat.completions.create(...)`
- Requires OPENAI_API_KEY environment variable
- Common model choices: gpt-4o, gpt-4-turbo, gpt-3.5-turbo

**Code Pattern**:
```python
from openai import AsyncClient
client = AsyncClient(api_key=os.getenv("OPENAI_API_KEY"))

response = await client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "System prompt"},
        {"role": "user", "content": "User message"}
    ]
)
```

### 2. Async Service Patterns in FastAPI
**Finding**: FastAPI naturally supports async/await patterns with proper dependency injection
**Details**:
- API endpoints should be declared as async def
- Service methods should be async def
- Database operations should use async session if available
- Proper error handling with try/except blocks

**Code Pattern**:
```python
@router.post("/", response_model=MessageRead)
async def create_message(...):
    async with get_async_session() as session:
        try:
            response = await ai_service.process_message(session, ...)
        except Exception as e:
            # Handle error, but ensure message is still saved
            raise
```

### 3. Context Injection Techniques for AI Prompts
**Finding**: Effective context injection combines system prompt with dynamic user data
**Details**:
- System prompt defines AI persona and capabilities
- Dynamic context includes current tasks, categories, and recent messages
- Format context in a clear, structured way for the AI to understand
- Limit context size to avoid token limits

**Example Pattern**:
```
You are a proactive Productivity Assistant. You have access to the user's current task list and help them organize, prioritize, and manage their time.

USER CONTEXT:
- Current Tasks: [list of active tasks with titles and priorities]
- Categories: [list of user-defined categories]
- Recent Conversation: [last 10 messages in conversation]

NEW MESSAGE: {user's current message}
RESPONSE:
```

### 4. Error Handling Strategies for External API Calls
**Finding**: Robust error handling should separate API failures from business logic
**Details**:
- Catch specific OpenAI exceptions (AuthenticationError, RateLimitError, APIConnectionError, etc.)
- Implement retry mechanisms where appropriate
- Ensure database operations aren't affected by AI API failures
- Provide meaningful error responses to the user

**Code Pattern**:
```python
try:
    response = await client.chat.completions.create(...)
    # Save AI response to database
except openai.AuthenticationError:
    # Log error and possibly alert admin
    raise HTTPException(status_code=500, detail="AI service configuration error")
except openai.RateLimitError:
    # Save user message but return informative error
    raise HTTPException(status_code=429, detail="AI service temporarily unavailable")
except Exception as e:
    # Log error and handle gracefully
    # Ensure user message is still saved even if AI fails
    logger.error(f"Unexpected error in AI service: {e}")
    raise HTTPException(status_code=500, detail="AI service temporarily unavailable")
```

### 5. Database Access Patterns in Codebase
**Finding**: The existing codebase uses SQLModel with dependency-injected sessions
**Details**:
- Database sessions are injected via Depends(get_session) in FastAPI
- Queries use the `select()` syntax from SQLModel
- Transactions are managed by the session context
- Existing patterns for fetching related data (tasks, categories) are consistent

**Code Pattern from Existing Code**:
```python
# From tasks API
from sqlmodel import Session, select

def read_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks
```

## Technology Decisions

### 1. OpenAI Integration Approach
**Decision**: Use openai.AsyncClient for all API calls
**Rationale**: Provides native async support that fits with FastAPI's async patterns
**Implementation**: Initialize client with API key from environment, use async methods throughout

### 2. Service Architecture Pattern
**Decision**: Create a stateless AIService class with async methods
**Rationale**: Fits with existing architecture patterns and ensures proper separation of concerns
**Implementation**: Create methods for context injection, message processing, and response handling

### 3. Message Persistence Strategy
**Decision**: Implement "save first, then process" approach
**Rationale**: Ensures message persistence regardless of AI API success/failure
**Implementation**: Save user message immediately, then call AI API, then save AI response

### 4. Context Injection Method
**Decision**: Combine system prompt with dynamic user context and conversation history
**Rationale**: Provides AI with sufficient context to give relevant, personalized responses
**Implementation**: Fetch user's tasks and categories, plus last 10 messages from conversation

### 5. Error Handling Approach
**Decision**: Separate AI API failures from database operations with graceful degradation
**Rationale**: Prevents AI service issues from breaking the entire message flow
**Implementation**: Save messages even if AI fails, return appropriate error responses

## Implementation Approach

### 1. AIService Class Design
- Initialize with OpenAI client and database session
- Methods: get_user_context(), get_conversation_history(), process_message()
- Proper async/await throughout

### 2. Message Processing Flow
1. Validate and save user message to database
2. Fetch user context (tasks, categories)
3. Fetch conversation history (last 10 messages)
4. Call OpenAI API with combined context
5. Save AI response to database
6. Return AI response to user

### 3. Error Handling Points
- During user message save (before AI call)
- During context retrieval (tasks, categories, history)
- During OpenAI API call
- During AI response save

## Risks and Mitigations

### 1. API Key Security
**Risk**: Hardcoded or improperly handled API keys
**Mitigation**: Use environment variables exclusively, never expose in code

### 2. Rate Limiting
**Risk**: OpenAI API rate limits affecting user experience
**Mitigation**: Implement retry logic and graceful degradation

### 3. Context Size Limits
**Risk**: Too much context exceeding AI token limits
**Mitigation**: Limit retrieved messages and data to reasonable sizes

### 4. Database Transaction Issues
**Risk**: Failures in AI API breaking database transactions
**Mitigation**: Use separate transactions for message persistence vs AI processing