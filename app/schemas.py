from pydantic import BaseModel
from typing import Optional, List

# ---------- User Schemas ----------
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_admin: bool

    class Config:
        orm_mode = True

# ---------- Task Schemas ----------
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    pass

class TaskOut(TaskBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

# ---------- Auth Schemas ----------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
