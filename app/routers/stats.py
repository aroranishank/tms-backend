from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models
from app.deps import get_db, get_current_admin

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/")
def get_stats(db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    total_users = db.query(models.User).count()
    total_tasks = db.query(models.Task).count()
    tasks_by_status = (
        db.query(models.Task.status, db.func.count(models.Task.id))
        .group_by(models.Task.status)
        .all()
    )
    return {
        "total_users": total_users,
        "total_tasks": total_tasks,
        "tasks_by_status": {status: count for status, count in tasks_by_status}
    }
