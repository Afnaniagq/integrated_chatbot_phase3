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
        # Build context in a more structured way to ensure the AI understands the different parts
        full_context_parts = []

        # Add user context
        if user_context and user_context['tasks']:
            task_list = []
            for task in user_context['tasks']:
                task_info = f"- {task['title']} (Priority: {task['priority']}"
                if task['category']:
                    task_info += f", Category: {task['category']}"
                if task['due_date']:
                    task_info += f", Due: {task['due_date']}"
                task_info += ")"
                task_list.append(task_info)

            full_context_parts.append("USER TASKS:")
            full_context_parts.append("\n".join(task_list))
            full_context_parts.append("")  # Empty line for readability

        if user_context and user_context['categories']:
            category_names = [cat['name'] for cat in user_context['categories']]
            full_context_parts.append("USER CATEGORIES:")
            full_context_parts.append(", ".join(category_names))
            full_context_parts.append("")  # Empty line for readability

        # Add conversation history if available
        if conversation_history:
            full_context_parts.append("CONVERSATION HISTORY (most recent at the end):")
            for idx, msg in enumerate(conversation_history):
                # Only show first 100 characters of each message to keep context manageable
                content_preview = msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content']
                full_context_parts.append(f"  [{idx+1}] {msg['role'].upper()}: {content_preview}")
            full_context_parts.append("")  # Empty line for readability

        # Add the new user message
        full_context_parts.append(f"CURRENT REQUEST: {new_message}")

        # Combine all parts
        full_context = "\n".join(full_context_parts)

        # Construct the messages list for the API call
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_context}
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
        import openai

        # Step 1: Save user message to database (ensuring persistence even if AI fails)
        user_message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="user",
            content=user_message_content
        )
        session.add(user_message)
        session.commit()
        session.refresh(user_message)

        # Step 2: Fetch user context (tasks, categories) and conversation history
        try:
            user_context = await self.get_user_context(session, user_id)
            conversation_history = await self.get_conversation_history(session, conversation_id)
        except Exception as e:
            logger.error(f"Error fetching context: {e}")
            # Continue with minimal context if possible
            user_context = {"tasks": [], "categories": []}
            conversation_history = []

        # Step 3: Prepare AI prompt with combined context
        system_prompt = "You are a proactive Productivity Assistant. You have access to the user's current task list and help them organize, prioritize, and manage their time."
        formatted_messages = self.format_ai_prompt(
            system_prompt,
            user_context,
            conversation_history,
            user_message_content
        )

        # Step 4: Call OpenAI API with structured prompt
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=0.7,
                max_tokens=1000
            )

            ai_response_content = response.choices[0].message.content

            # Step 5: Save AI response to database
            ai_message = Message(
                conversation_id=conversation_id,
                user_id=user_id,  # The AI message is associated with the user's conversation
                role="assistant",
                content=ai_response_content
            )
            session.add(ai_message)
            session.commit()

            # Step 6: Return AI response content
            return ai_response_content

        except openai.AuthenticationError as e:
            logger.error(f"OpenAI Authentication Error: {e}")
            # User message is still saved, return helpful error message
            error_msg = "Sorry, there's an issue with the AI service configuration. Your message has been saved."
            return error_msg

        except openai.RateLimitError as e:
            logger.error(f"OpenAI Rate Limit Error: {e}")
            # User message is still saved, return helpful error message
            error_msg = "The AI service is temporarily busy. Your message has been saved and will be processed shortly."
            return error_msg

        except openai.APIConnectionError as e:
            logger.error(f"OpenAI API Connection Error: {e}")
            # User message is still saved, return helpful error message
            error_msg = "Unable to reach the AI service. Your message has been saved."
            return error_msg

        except Exception as e:
            logger.error(f"Unexpected error in process_message: {e}")
            # User message is still saved, return helpful error message
            error_msg = "An unexpected error occurred. Your message has been saved and we're looking into it."
            return error_msg