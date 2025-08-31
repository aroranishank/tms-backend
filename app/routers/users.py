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

@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user_update: schemas.AdminUserUpdate, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.is_deleted == False
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if username already exists (if being updated)
    if user_update.username and user_update.username != user.username:
        existing_username = db.query(models.User).filter(
            models.User.username == user_update.username,
            models.User.is_deleted == False,
            models.User.id != user_id
        ).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists (if being updated)
    if user_update.email and user_update.email != user.email:
        existing_email = db.query(models.User).filter(
            models.User.email == user_update.email,
            models.User.is_deleted == False,
            models.User.id != user_id
        ).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Validate user_type if being updated
    if user_update.user_type and user_update.user_type not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="user_type must be either 'user' or 'admin'")
    
    # Prevent admin from demoting themselves
    if user.id == admin.id and user_update.user_type == "user":
        raise HTTPException(status_code=400, detail="Cannot demote your own admin privileges")
    
    # Update fields
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.password is not None:
        user.hashed_password = security.get_password_hash(user_update.password)
    if user_update.user_type is not None:
        user.user_type = user_update.user_type
    
    db.commit()
    db.refresh(user)
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
