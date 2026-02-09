from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from src.api import health, tasks, trash, auth, conversations, messages, chat
from dotenv import load_dotenv
from src.config import *
import os

load_dotenv()

# FIX 1: Set redirect_slashes=False to stop the 307 Redirect loops
# This prevents the backend from forcing the frontend to refresh when a URL has a trailing slash.
app = FastAPI(title="Todo API", redirect_slashes=False)

# FIX 2: Ensure CORS includes both localhost and 127.0.0.1
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "https://todofullstack-nine.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registering routes
app.include_router(health.router, prefix="/api", tags=["health"])

# FIX 3: Be careful with the prefix. 
# If your tasks router already defines @router.get("/"), then prefix="/api/tasks" works.
# If your tasks router defines @router.get("/tasks"), use prefix="/api".
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(trash.router, prefix="/api/trash", tags=["trash"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.on_event("startup")
def on_startup():
    from src.database import create_db_and_tables
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"status": "online"}