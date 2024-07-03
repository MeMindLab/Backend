from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.common import TimestampMixin
from app.schemas.lemon import LemonCreate


class Lemon(Base, TimestampMixin):
    __tablename__ = "lemons"

    id = Column(Integer, primary_key=True, index=True)
    lemon_count = Column(Integer, nullable=False, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    user = relationship("User", back_populates="lemons")

    # pydantic request받아서 orm객체로 변환
    @classmethod
    def create(cls, request: LemonCreate, user_id: int) -> "Lemon":
        return cls(
            lemon_count=request.lemon_count,
            user_id=user_id,
        )

    def __repr__(self):
        return f"Lemon(id={self.id}, lemon_count={self.lemon_count}, user_id={self.user_id})"
