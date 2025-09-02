from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app import models, schemas
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=list[schemas.TaskOut])
def get_my_tasks(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Task).filter(
        models.Task.owner_id == current_user.id,
        models.Task.is_deleted == False
    ).all()

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
