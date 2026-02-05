from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Todo API")

# FIX: This tells the backend to allow your Frontend (Port 3000) to send data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://todofullstack-nine.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
from src.api import health, tasks, trash, auth, conversations, messages

# Registering routes with consistent prefixes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(trash.router, prefix="/api/trash", tags=["trash"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])

@app.on_event("startup")
def on_startup():
    from src.database import create_db_and_tables
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"status": "online"}