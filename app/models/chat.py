# app/models/chat.py
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Text, Integer, Boolean, Uuid, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.common import TimestampMixin

from app.models.user import User


class Message(Base, TimestampMixin):
    __tablename__ = "messages"
    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid4().hex)
    index: Mapped[int] = mapped_column(Integer, nullable=False)
    is_from_user: Mapped[bool] = mapped_column(Boolean, nullable=False)
    message = mapped_column(Text, nullable=True)
    message_timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    images = relationship("Image", back_populates="message")


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"
    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid4().hex)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    images = relationship("Image", back_populates="conversation")

    # 외래 키 설정
    user: Mapped["User"] = relationship("User", backref="conversation_user")
