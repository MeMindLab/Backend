# app/models/lemon.py

from uuid import uuid4, UUID
from sqlalchemy import Integer, ForeignKey, Uuid
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.core.database import Base
from app.models.common import TimestampMixin
from app.schemas.lemon import LemonCreate
from app.models.user import User


class Lemon(Base, TimestampMixin):
    __tablename__ = "lemons"

    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid4)
    lemon_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    user_id = mapped_column(ForeignKey("users.id"), unique=True)

    user: Mapped["User"] = relationship("User", back_populates="lemons")

    @classmethod
    def create(cls, request: LemonCreate, user_id: UUID) -> "Lemon":
        return cls(
            lemon_count=request.lemon_count,
            user_id=user_id,
        )

    def __repr__(self):
        return f"Lemon(id={self.id}, lemon_count={self.lemon_count}, user_id={self.user_id})"
