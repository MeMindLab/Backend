# app/models/image

import uuid
from sqlalchemy import (
    Integer,
    Uuid,
    JSON,
    String,
    ForeignKey,
    Text,
    func,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.chat import Message, Conversation


class Image(Base):
    __tablename__ = "images"

    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    path = mapped_column(String(256), nullable=False)
    extension = mapped_column(String(8), nullable=False)

    conversation_id = mapped_column(Uuid, ForeignKey("conversations.id"), nullable=True)
    message_id = mapped_column(Uuid, ForeignKey("messages.id"), nullable=True)

    conversation = relationship("Conversation", back_populates="images")
    message = relationship("Message", back_populates="images")
