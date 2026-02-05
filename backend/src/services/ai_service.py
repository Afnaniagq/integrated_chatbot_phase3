"""
AI Service for orchestrating communication between user, database context, and OpenAI API.

This service handles:
- Fetching user context (tasks and categories) from the database
- Retrieving conversation history
- Formatting AI prompts with context
- Calling OpenAI API with enriched context
- Managing message persistence
"""

import os
from typing import Dict, List, Optional
from uuid import UUID
from sqlmodel import Session, select
from openai import AsyncClient
from datetime import datetime
import logging

# Import models
from ..models.user import User
from ..models.task import Task
from ..models.category import Category
from ..models.chat import Conversation, Message

logger = logging.getLogger(__name__)


class AIService:
    """
    Orchestrate communication between user, database context, and OpenAI API
    """

    def __init__(self):
        """
        Initialize the AI Service with OpenAI client
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = AsyncClient(api_key=api_key)
        self.model = "gpt-4o"  # Use gpt-4o as specified in requirements

    async def get_user_context(self, session: Session, user_id: UUID) -> Dict:
        """
        Fetch user's current tasks and categories to inject into AI context

        Args:
            session: Database session
            user_id: UUID of the user

        Returns:
            Dictionary containing user's tasks and categories
        """
        # Fetch user's active tasks
        tasks_query = select(Task).where(
            Task.user_id == user_id,
            Task.is_completed == False  # Only active/incomplete tasks
        )
        tasks = session.exec(tasks_query).all()

        # Fetch user's categories
        categories_query = select(Category).where(Category.user_id == user_id)
        categories = session.exec(categories_query).all()

        # Format the context
        user_context = {
            "tasks": [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value if task.priority else "medium",
                    "category": task.category,
                    "is_completed": task.is_completed,
                    "due_date": task.due_date.isoformat() if task.due_date else None
                }
                for task in tasks
            ],
            "categories": [
                {
                    "id": str(category.id),
                    "name": category.name
                }
                for category in categories
            ]
        }

        return user_context

    async def get_conversation_history(self, session: Session, conversation_id: UUID) -> List[Dict]:
        """
        Retrieve last 10 messages from the conversation for AI context

        Args:
            session: Database session
            conversation_id: UUID of the conversation

        Returns:
            List of last 10 messages from the conversation
        """
        # Fetch the last 10 messages, ordered by creation time (most recent last)
        messages_query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(10)
        )
        messages = session.exec(messages_query).all()

        # Sort by created_at to have chronological order (oldest first, newest last)
        messages.sort(key=lambda x: x.created_at)

        # Format the conversation history
        conversation_history = [
            {
                "role": message.role,
                "content": message.content,
                "timestamp": message.created_at.isoformat()
            }
            for message in messages
        ]

        return conversation_history

    def format_ai_prompt(
        self,
        system_prompt: str,
        user_context: Dict,
        conversation_history: List[Dict],
        new_message: str
    ) -> List[Dict]:
        """
        Format the AI prompt with system instructions, user context, conversation history, and new message

        Args:
            system_prompt: The base system prompt
            user_context: User's tasks and categories
            conversation_history: Previous messages in the conversation
            new_message: The new message from the user

        Returns:
            Formatted list of messages for the AI API
        """
        # Create the full context string
        context_str = f"USER CONTEXT:\n"
        context_str += f"- Current Tasks: {[{'title': t['title'], 'priority': t['priority'], 'category': t['category']} for t in user_context['tasks']]}\n"
        context_str += f"- Categories: {[c['name'] for c in user_context['categories']]}\n\n"

        if conversation_history:
            context_str += f"CONVERSATION HISTORY:\n"
            for msg in conversation_history:
                context_str += f"  {msg['role'].upper()}: {msg['content']}\n"
            context_str += "\n"

        context_str += f"NEW MESSAGE: {new_message}"

        # Construct the messages list for the API call
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context_str}
        ]

        return messages

    async def process_message(
        self,
        session: Session,
        user_id: UUID,
        conversation_id: UUID,
        user_message_content: str
    ) -> str:
        """
        Main orchestration method that coordinates all other methods

        Args:
            session: Database session
            user_id: UUID of the user
            conversation_id: UUID of the conversation
            user_message_content: Content of the user's message

        Returns:
            AI response content
        """
        # Step 1: Save user message to database
        user_message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="user",
            content=user_message_content
        )
        session.add(user_message)
        session.commit()
        session.refresh(user_message)

        # Step 2: Fetch user context (tasks, categories)
        user_context = await self.get_user_context(session, user_id)

        # Step 3: Fetch conversation history (last 10 messages)
        conversation_history = await self.get_conversation_history(session, conversation_id)

        # Step 4: Prepare AI prompt with combined context
        system_prompt = "You are a proactive Productivity Assistant. You have access to the user's current task list and help them organize, prioritize, and manage their time."
        formatted_messages = self.format_ai_prompt(
            system_prompt,
            user_context,
            conversation_history,
            user_message_content
        )

        # Step 5: Call OpenAI API with structured prompt
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=0.7,
                max_tokens=1000
            )

            ai_response_content = response.choices[0].message.content

            # Step 6: Save AI response to database
            ai_message = Message(
                conversation_id=conversation_id,
                user_id=user_id,  # The AI message is associated with the user's conversation
                role="assistant",
                content=ai_response_content
            )
            session.add(ai_message)
            session.commit()

            # Step 7: Return AI response content
            return ai_response_content

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            # Even if AI API fails, the user message is already saved
            # We can return an error message or re-raise depending on requirements
            raise e