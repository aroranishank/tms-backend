from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, security
from app.deps import get_db, get_current_admin

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pw = security.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    return db.query(models.User).all()
