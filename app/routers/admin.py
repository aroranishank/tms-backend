from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.deps import get_db, get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/tasks", response_model=List[schemas.TaskWithUserOut])
def get_all_tasks(db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    """Get all tasks in the system with user details (admin only)"""
    tasks = db.query(models.Task).filter(models.Task.is_deleted == False).all()
    return tasks

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