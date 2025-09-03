from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List, Optional
from app import models, schemas
from app.deps import get_db, get_current_admin
import math

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/tasks", response_model=schemas.PaginatedTasksResponse)
def search_tasks(
    search: Optional[str] = Query(None, description="Search term for task title, description, or user info"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db), 
    admin: models.User = Depends(get_current_admin)
):
    """Search tasks with pagination (admin only)"""
    
    # Base query with joins to get user information and load owner relationship
    query = db.query(models.Task).join(models.User, models.Task.owner_id == models.User.id).filter(
        and_(
            models.Task.is_deleted == False,
            models.User.is_deleted == False
        )
    ).options(joinedload(models.Task.owner))
    
    # Apply search filter if provided
    if search:
        if search.strip() == "*":
            # "*" means get all tasks - no additional filter needed
            pass
        elif search.strip() == "":
            # Empty string means no results
            query = query.filter(False)  # This will return no results
        else:
            # Search in task title, description, username, and email using LIKE
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    models.Task.title.ilike(search_term),
                    models.Task.description.ilike(search_term),
                    models.User.username.ilike(search_term),
                    models.User.email.ilike(search_term)
                )
            )
    
    # Get total count for pagination
    total_items = query.count()
    
    # Calculate pagination
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 1
    offset = (page - 1) * limit
    
    # Apply pagination
    tasks = query.offset(offset).limit(limit).all()
    
    # Build pagination info
    pagination = schemas.PaginationInfo(
        current_page=page,
        total_pages=total_pages,
        total_items=total_items,
        items_per_page=limit,
        has_next=page < total_pages,
        has_previous=page > 1
    )
    
    return schemas.PaginatedTasksResponse(
        tasks=tasks,
        pagination=pagination
    )

@router.post("/users/{user_id}/tasks", response_model=schemas.TaskOut)
def create_task_for_user(
    user_id: int, 
    task: schemas.AdminTaskCreate, 
    db: Session = Depends(get_db), 
    admin: models.User = Depends(get_current_admin)
):
    """Create a task for a specific user (admin only)"""
    # Check if user exists and is not deleted
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.is_deleted == False
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create task
    db_task = models.Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_datetime=task.due_date,
        start_datetime=task.start_datetime,
        end_datetime=task.end_datetime,
        owner_id=user_id,
        created_by=admin.id,
        updated_by=admin.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task