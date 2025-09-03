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
    is_admin: Optional[bool] = None

class UserOut(UserBase):
    id: int
    user_type: str
    is_admin: bool

    class Config:
        from_attributes = True

class PaginationInfo(BaseModel):
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int
    has_next: bool
    has_previous: bool

class PaginatedUsersResponse(BaseModel):
    users: List[UserOut]
    pagination: PaginationInfo

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

class AdminTaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    priority: Optional[str] = "medium"
    due_date: Optional[datetime] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    owner_id: Optional[int] = None  # Allow reassigning tasks (admin only)
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    due_datetime: Optional[datetime] = None

class TaskOut(TaskBase):
    id: int
    owner_id: int
    completion_datetime: Optional[datetime] = None
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True

class TaskWithUserOut(TaskBase):
    id: int
    owner_id: int
    completion_datetime: Optional[datetime] = None
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    owner: UserOut

    class Config:
        from_attributes = True

class PaginatedTasksResponse(BaseModel):
    tasks: List[TaskWithUserOut]
    pagination: PaginationInfo

# ---------- Auth Schemas ----------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
