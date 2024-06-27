from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.common import TimestampMixin


class Lemon(Base, TimestampMixin):
    __tablename__ = "lemons"

    id = Column(Integer, primary_key=True, index=True)
    lemon_count = Column(Integer, nullable=False, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 외래 키 설정

    user = relationship("User", back_populates="lemons")
