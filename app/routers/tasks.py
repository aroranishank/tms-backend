from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from app import models, schemas
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=schemas.PaginatedUserTasksResponse)
def get_my_tasks(
    search: Optional[str] = Query(None, description="Search term for task title or description"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """Get user's tasks with search and pagination"""
    
    # Base query for user's own tasks
    query = db.query(models.Task).filter(
        models.Task.owner_id == current_user.id,
        models.Task.is_deleted == False
    )
    
    # Apply search filter if provided
    if search:
        if search.strip() == "*":
            # "*" means get all user's tasks - no additional filter needed
            pass
        elif search.strip() == "":
            # Empty string means no results
            query = query.filter(False)
        else:
            # Search in task title and description using LIKE
            search_term = f"%{search}%"
            query = query.filter(
                models.Task.title.ilike(search_term) | 
                models.Task.description.ilike(search_term)
            )
    
    # Get total count for pagination
    total_items = query.count()
    
    # Calculate pagination
    import math
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 1
    offset = (page - 1) * limit
    
    # Apply pagination and order by creation date (newest first)
    tasks = query.order_by(models.Task.created_at.desc()).offset(offset).limit(limit).all()
    
    # Build pagination info
    pagination = schemas.PaginationInfo(
        current_page=page,
        total_pages=total_pages,
        total_items=total_items,
        items_per_page=limit,
        has_next=page < total_pages,
        has_previous=page > 1
    )
    
    return schemas.PaginatedUserTasksResponse(
        tasks=tasks,
        pagination=pagination
    )

@router.post("/", response_model=schemas.TaskOut)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Validate priority
    if task.priority and task.priority not in ["low", "medium", "high", "urgent"]:
        raise HTTPException(status_code=400, detail="priority must be one of: low, medium, high, urgent")
    
    db_task = models.Task(**task.dict(), owner_id=current_user.id, created_by=current_user.id, updated_by=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, updated: schemas.TaskUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Build query based on user type
    if current_user.is_admin:
        # Admin can update any task
        task = db.query(models.Task).filter(
            models.Task.id == task_id,
            models.Task.is_deleted == False
        ).first()
    else:
        # Regular user can only update their own tasks
        task = db.query(models.Task).filter(
            models.Task.id == task_id,
            models.Task.owner_id == current_user.id,
            models.Task.is_deleted == False
        ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get update data
    update_data = updated.dict(exclude_unset=True)
    
    # Restrict normal users to only update start_datetime, end_datetime, and status
    if not current_user.is_admin:
        allowed_fields = {"start_datetime", "end_datetime", "status"}
        restricted_fields = set(update_data.keys()) - allowed_fields
        if restricted_fields:
            raise HTTPException(
                status_code=403, 
                detail=f"Normal users can only update start_datetime, end_datetime, and status. Restricted fields: {', '.join(restricted_fields)}"
            )
    
    # Auto-set completion_datetime when status changes to "completed"
    if update_data.get("status") == "completed" and task.status != "completed":
        update_data["completion_datetime"] = datetime.now(timezone.utc)
    elif update_data.get("status") != "completed" and task.status == "completed":
        # Clear completion_datetime if status changes from completed to something else
        update_data["completion_datetime"] = None
    
    # Admin-only validations
    if current_user.is_admin:
        # Validate priority if provided
        if updated.priority and updated.priority not in ["low", "medium", "high", "urgent"]:
            raise HTTPException(status_code=400, detail="priority must be one of: low, medium, high, urgent")
        
        # Validate owner_id if provided (admin can reassign tasks)
        if updated.owner_id is not None:
            target_user = db.query(models.User).filter(
                models.User.id == updated.owner_id,
                models.User.is_deleted == False
            ).first()
            if not target_user:
                raise HTTPException(status_code=400, detail="Target user not found")
            if target_user.is_admin:
                raise HTTPException(status_code=400, detail="Cannot assign tasks to admin users")
    
    # Set updated_by for all updates
    update_data["updated_by"] = current_user.id
    
    for key, value in update_data.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Build query based on user type
    if current_user.is_admin:
        # Admin can delete any task
        task = db.query(models.Task).filter(
            models.Task.id == task_id,
            models.Task.is_deleted == False
        ).first()
    else:
        # Regular user can only delete their own tasks
        task = db.query(models.Task).filter(
            models.Task.id == task_id,
            models.Task.owner_id == current_user.id,
            models.Task.is_deleted == False
        ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Soft delete the task
    task.is_deleted = True
    task.deleted_at = datetime.now(timezone.utc)
    task.updated_by = current_user.id
    db.commit()
    
    return {"message": f"Task '{task.title}' deleted successfully"}
