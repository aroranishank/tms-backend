from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app import models, schemas, security
from app.deps import get_db, get_current_admin

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    # Check if username already exists
    existing_username = db.query(models.User).filter(
        models.User.username == user.username,
        models.User.is_deleted == False
    ).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    existing_email = db.query(models.User).filter(
        models.User.email == user.email,
        models.User.is_deleted == False
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Validate user_type
    if user.user_type not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="user_type must be either 'user' or 'admin'")
    
    hashed_pw = security.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        user_type=user.user_type
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    return db.query(models.User).filter(models.User.is_deleted == False).all()

@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.is_deleted == False
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.is_deleted == False
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deleting themselves
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Soft delete the user
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    db.commit()
    
    return {"message": f"User '{user.username}' deleted successfully"}
