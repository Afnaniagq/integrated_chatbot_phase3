import json
import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from openai import OpenAI
from sqlalchemy.orm import Session
from src.database import get_session as get_db
from src.models.task import Task 

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/chat")
async def chat_endpoint(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    messages = data.get("messages", [])
    
    # We need a user ID to save the task to the right person
    # If you aren't passing the token in ChatPanel headers yet, 
    # this might need temporary adjustment.
    
    def generate():
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "create_task",
                        "description": "Create a new task in the database",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "The title of the task"},
                                "description": {"type": "string", "description": "More details"},
                                "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                            },
                            "required": ["title"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "refresh_dashboard",
                        "description": "Refresh the dashboard UI",
                        "parameters": {"type": "object", "properties": {}}
                    }
                }
            ]
        )

        for chunk in response:
            delta = chunk.choices[0].delta
            
            # Handle Text
            if delta.content:
                yield f'0:{json.dumps(delta.content)}\n'
            
            # Handle Tool Calls
            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    # Note: In a real production app, you would execute the DB 
                    # logic here or in a secondary step. 
                    # For the AI SDK, we send the tool call to the frontend.
                    yield f'9:{json.dumps({
                        "toolCallId": tool_call.id, 
                        "toolName": tool_call.function.name, 
                        "args": tool_call.function.arguments or "{}"
                    })}\n'

    return StreamingResponse(generate(), media_type="text/plain")