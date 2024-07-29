# 대화 관리 모델
import uuid
from datetime import datetime, date
from sqlalchemy import Text, Integer, Boolean, Uuid, DateTime, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.common import TimestampMixin

from app.models.user import User


class Message(Base, TimestampMixin):
    __tablename__ = "messages"
    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    index: Mapped[int] = mapped_column(Integer, nullable=False)
    is_from_user: Mapped[bool] = mapped_column(Boolean, nullable=False)
    message = mapped_column(Text, nullable=True)
    message_timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    conversation_id = mapped_column(ForeignKey("conversations.id"), nullable=False)

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )  # 추가: Conversation 모델과의 관계 설정

    images = relationship("Image", back_populates="message")

    @classmethod
    def create(
        cls,
        conversation_id: uuid.UUID,
        is_from_user: bool,
        message: str,
        index: int,
    ) -> "Message":
        """Create and return a new Message instance."""
        return cls(
            conversation_id=conversation_id,
            is_from_user=is_from_user,
            message=message,
            index=index,
        )


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"
    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)

    user_id = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    images = relationship("Image", back_populates="conversation")
    date = mapped_column(Date, nullable=False, default=date.today())

    # 외래 키 설정
    user: Mapped["User"] = relationship("User", backref="conversation_user")
    reports = relationship("Report", back_populates="conversation")
    messages = relationship(
        "Message", back_populates="conversation"
    )  # 추가: Message 모델과의 양방향 관계 설정

    @classmethod
    def create(cls, date: date, user_id: uuid.UUID) -> "Conversation":
        return cls(
            user_id=user_id,
            date=date,
        )
