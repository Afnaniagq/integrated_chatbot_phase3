"""
Category Service Module

This module provides service layer functions for category operations following the same patterns
as the task_service.py module.
"""

from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select
from ..models.category import Category, CategoryCreate, CategoryUpdate


def create_category(*, session: Session, category_create: CategoryCreate) -> Category:
    """
    Create a new category for a specific user.
    """
    # Convert Pydantic model to dict
    category_data = category_create.dict()

    # Remove user_id from the dict so it doesn't clash with the explicit user_id argument
    # This prevents the "got multiple values for keyword argument 'user_id'" error.
    category_data.pop('user_id', None)

    db_category = Category(
        **category_data
    )

    session.add(db_category)
    session.commit()
    session.refresh(db_category)

    return db_category


def get_categories_by_user(*, session: Session, user_id: UUID) -> List[Category]:
    """
    Get all categories for a specific user.
    """
    statement = select(Category).where(Category.user_id == user_id)
    categories = session.exec(statement).all()
    return categories


def get_category_by_id(*, session: Session, category_id: UUID, user_id: UUID) -> Optional[Category]:
    """
    Get a specific category by ID for a specific user (enforcing user isolation).
    """
    statement = select(Category).where(
        Category.id == category_id,
        Category.user_id == user_id
    )
    category = session.exec(statement).first()
    return category


def update_category(*, session: Session, category_id: UUID, category_update: CategoryUpdate, user_id: UUID) -> Optional[Category]:
    """
    Update a category for a specific user.
    """
    db_category = get_category_by_id(session=session, category_id=category_id, user_id=user_id)
    if not db_category:
        return None

    category_data = category_update.dict(exclude_unset=True)
    # Remove user_id if present to prevent changing ownership
    category_data.pop('user_id', None)

    for key, value in category_data.items():
        setattr(db_category, key, value)

    session.add(db_category)
    session.commit()
    session.refresh(db_category)

    return db_category


def delete_category(*, session: Session, category_id: UUID, user_id: UUID) -> bool:
    """
    Delete a category for a specific user.
    """
    db_category = get_category_by_id(session=session, category_id=category_id, user_id=user_id)
    if not db_category:
        return False

    session.delete(db_category)
    session.commit()
    return True