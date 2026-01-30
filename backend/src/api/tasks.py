from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List, Dict, Any
from sqlmodel import Session

from src.database import get_session
from src.api.deps import get_current_user_id, log_bulk_operation
from src.services.task_service import (
    create_task, get_tasks, get_task, update_task, toggle_task_completion, delete_task
)
from src.services.bulk_service import BulkService, BulkOperationType, BulkOperationParams
from src.models.task import Task, TaskCreate, TaskUpdate, TaskToggle, TaskRead

# Create a FastAPI router for task endpoints
router = APIRouter(redirect_slashes=False)


@router.get("", response_model=dict)
def read_tasks(
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
    priority: str = None,
    category: str = None,
    is_completed: bool = None,
    limit: int = 20,
    offset: int = 0
) -> dict:
    """
    Get all tasks for the current user with optional filters
    """
    user_uuid = UUID(current_user_id)
    tasks, total_count = get_tasks(
        session=session,
        user_id=user_uuid,
        priority=priority,
        category=category,
        is_completed=is_completed,
        limit=limit,
        offset=offset
    )

    return {
        "tasks": tasks,
        "total": total_count,
        "offset": offset
    }


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_new_task(
    task_create: TaskCreate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Task:
    """
    Create a new task for the current user
    """
    user_uuid = UUID(current_user_id)
    return create_task(session=session, task_create=task_create, user_id=user_uuid)


@router.get("/{task_id}", response_model=TaskRead)
def read_task(
    task_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Task:
    """
    Get a specific task by ID
    """
    user_uuid = UUID(current_user_id)
    task = get_task(session=session, task_id=task_id, user_id=user_uuid)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to access it"
        )

    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_existing_task(
    task_id: UUID,
    task_update: TaskUpdate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Task:
    """
    Update a specific task by ID
    """
    user_uuid = UUID(current_user_id)
    updated_task = update_task(
        session=session,
        task_id=task_id,
        task_update=task_update,
        user_id=user_uuid
    )

    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to update it"
        )

    return updated_task


@router.patch("/{task_id}/toggle", response_model=TaskRead)
def toggle_task_completion_status(
    task_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Task:
    """
    Toggle the completion status of a specific task
    """
    user_uuid = UUID(current_user_id)
    toggled_task = toggle_task_completion(
        session=session,
        task_id=task_id,
        user_id=user_uuid
    )

    if not toggled_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to update it"
        )

    return toggled_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_task(
    task_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a specific task by ID (soft delete)
    """
    user_uuid = UUID(current_user_id)
    success = delete_task(
        session=session,
        task_id=task_id,
        user_id=user_uuid
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found, already deleted, or you don't have permission to delete it"
        )


from pydantic import BaseModel

class BulkUpdateRequest(BaseModel):
    task_ids: List[UUID]
    update_type: str
    params: Dict[str, Any]


class BulkDeleteRequest(BaseModel):
    task_ids: List[UUID]


@router.post("/bulk/update/", status_code=status.HTTP_200_OK)
def bulk_update_tasks(
    request: BulkUpdateRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Bulk update multiple tasks with the same changes (status, category, priority)
    """
    user_uuid = UUID(current_user_id)

    # Validate update_type
    try:
        bulk_op_type = BulkOperationType(request.update_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid update type. Must be one of: {[op.value for op in BulkOperationType]}"
        )

    # Create bulk operation parameters
    bulk_params = BulkOperationParams(**request.params)

    # Perform bulk update
    result = BulkService.bulk_update_tasks(
        task_ids=request.task_ids,
        update_type=bulk_op_type,
        params=bulk_params,
        user_id=user_uuid,
        db_session=session
    )

    # Log the bulk operation
    log_bulk_operation(current_user_id, f"bulk_{request.update_type}_update", result.get("updated_count", 0))

    return result


@router.post("/bulk/delete/", status_code=status.HTTP_200_OK)
def bulk_delete_tasks(
    request: BulkDeleteRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Bulk soft-delete multiple tasks
    """
    user_uuid = UUID(current_user_id)

    # Perform bulk delete
    result = BulkService.bulk_delete_tasks(
        task_ids=request.task_ids,
        user_id=user_uuid,
        db_session=session
    )

    # Log the bulk operation
    log_bulk_operation(current_user_id, "bulk_delete", result.get("deleted_count", 0))

    return result