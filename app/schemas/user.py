from enum import Enum
from pydantic import BaseModel, validator, Field
from datetime import datetime
from typing import Optional, Dict
from app.models.user import UserRole


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    nickname: str | None = None


class UserLogin(UserBase):
    password: str


class User(UserBase):
    id: int
    nickname: Optional[str]
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        response_model_exclude = {"password"}


class UserUpdate(BaseModel):
    nickname: str | None = None
    is_active: bool | None = None
    role: UserRole | None = None


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str]
    expires_in: int


class Channel(str, Enum):
    SMS = "sms"
    CALL = "call"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    SNA = "sna"


class VerificationCheckResponse(BaseModel):
    to: Optional[str]
    channel: Channel
    status: Optional[str]
    valid: Optional[bool]


class VerificationResult(BaseModel):
    success: bool
    data: Dict[str, VerificationCheckResponse]
