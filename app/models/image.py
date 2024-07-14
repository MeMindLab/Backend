# app/models/image

from uuid import uuid4
from sqlalchemy import (
    Uuid,
    String,
    ForeignKey,
)

from sqlalchemy.orm import mapped_column, relationship
from app.core.database import Base


class Image(Base):
    __tablename__ = "images"

    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid4)
    path = mapped_column(String(256), nullable=False)
    extension = mapped_column(String(8), nullable=False)

    conversation_id = mapped_column(Uuid, ForeignKey("conversations.id"), nullable=True)
    message_id = mapped_column(Uuid, ForeignKey("messages.id"), nullable=True)

    conversation = relationship("Conversation", back_populates="images")
    message = relationship("Message", back_populates="images")
