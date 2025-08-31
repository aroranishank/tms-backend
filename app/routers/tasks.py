from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
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
    
    db_task = models.Task(**task.dict(), owner_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, updated: schemas.TaskUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(
        models.Task.id == task_id, 
        models.Task.owner_id == current_user.id,
        models.Task.is_deleted == False
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Validate priority if provided
    if updated.priority and updated.priority not in ["low", "medium", "high", "urgent"]:
        raise HTTPException(status_code=400, detail="priority must be one of: low, medium, high, urgent")
    
    # Auto-set completion_datetime when status changes to "completed"
    update_data = updated.dict(exclude_unset=True)
    if update_data.get("status") == "completed" and task.status != "completed":
        update_data["completion_datetime"] = datetime.utcnow()
    elif update_data.get("status") != "completed" and task.status == "completed":
        # Clear completion_datetime if status changes from completed to something else
        update_data["completion_datetime"] = None
    
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
    task.deleted_at = datetime.utcnow()
    db.commit()
    
    return {"message": f"Task '{task.title}' deleted successfully"}
