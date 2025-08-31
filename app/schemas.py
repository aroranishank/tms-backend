from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ---------- User Schemas ----------
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    user_type: str = "user"  # "user" or "admin", defaults to "user"

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class AdminUserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    user_type: Optional[str] = None

class UserOut(UserBase):
    id: int
    user_type: str
    is_admin: bool

    class Config:
        orm_mode = True

# ---------- Task Schemas ----------
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    priority: Optional[str] = "medium"  # "low", "medium", "high", "urgent"
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    due_datetime: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    due_datetime: Optional[datetime] = None

class TaskOut(TaskBase):
    id: int
    owner_id: int
    completion_datetime: Optional[datetime] = None

    class Config:
        orm_mode = True

# ---------- Auth Schemas ----------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
