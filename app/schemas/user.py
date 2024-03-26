from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.user import UserRole


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    username: str | None = None
    nickname: str | None = None


class UserLogin(UserBase):
    password: str


class User(UserBase):
    id: int
    username: Optional[str]
    nickname: Optional[str]
    is_active: bool
    role: UserRole or None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: str | None = None
    nickname: str | None = None
    is_active: bool | None = None
    role: UserRole or None = None


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    expires_in: int
