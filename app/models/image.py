# app/models/image

import uuid
from sqlalchemy import (
    Uuid,
    String,
    ForeignKey,
)

from sqlalchemy.orm import mapped_column, relationship
from app.core.database import Base
from app.models.common import TimestampMixin


class Image(Base, TimestampMixin):
    __tablename__ = "images"

    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    path = mapped_column(String(256), nullable=False)
    extension = mapped_column(String(8), nullable=False)

    conversation_id = mapped_column(ForeignKey("conversations.id"), nullable=True)
    conversation = relationship("Conversation", back_populates="images")

    message_id = mapped_column(ForeignKey("messages.id"), nullable=True)
    message = relationship("Message", back_populates="image")

    @classmethod
    def create(
        cls,
        path: str,
        extension: str,
        conversation_id: uuid.UUID,
        message_id: uuid.UUID,
    ):
        return cls(
            path=path,
            extension=extension,
            conversation_id=conversation_id,
            message_id=message_id,
        )
