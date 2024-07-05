from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.user import UserRole


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    nickname: str | None = None


class UserLogin(UserBase):
    password: str


class UserSignInResponse(UserBase):
    id: int
    nickname: Optional[str]
    is_active: bool
    is_verified: bool
    role: UserRole
    created_at: datetime
    updated_at: datetime


class UserSchema(UserSignInResponse):
    lemons: Optional[int]

    class Config:
        from_attributes = True


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


class VerificationResult(BaseModel):
    to: Optional[str]
    channel: Channel
    status: Optional[str]
    valid: Optional[bool]


class VerificationCheckResponse(BaseModel):
    success: bool
    data: VerificationResult
