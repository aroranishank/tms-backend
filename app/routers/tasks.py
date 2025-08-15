from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=list[schemas.TaskOut])
def get_my_tasks(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Task).filter(models.Task.owner_id == current_user.id).all()

@router.post("/", response_model=schemas.TaskOut)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = models.Task(**task.dict(), owner_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, updated: schemas.TaskUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in updated.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task
