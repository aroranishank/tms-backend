from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app import models, security, schemas
from app.deps import get_db, get_current_user
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == form_data.username,
        models.User.is_deleted == False
    ).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = security.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    print("Login Success", access_token);
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserOut)
def get_current_user_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.UserOut)
def update_current_user_profile(
    user_update: schemas.UserUpdate, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if username already exists (if being changed)
    if user_update.username and user_update.username != current_user.username:
        existing_user = db.query(models.User).filter(
            models.User.username == user_update.username,
            models.User.is_deleted == False,
            models.User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists (if being changed)
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(models.User).filter(
            models.User.email == user_update.email,
            models.User.is_deleted == False,
            models.User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    if update_data.get("password"):
        update_data["hashed_password"] = security.get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user
