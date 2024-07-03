from pydantic import BaseModel
from sqlalchemy import Column, String, Enum, Boolean
from enum import Enum as PythonEnum

from sqlalchemy.orm import relationship

from app.core.database import Base
from .common import CommonModel


class UserRole(str, PythonEnum):
    user = "user"
    admin = "admin"


class User(CommonModel):
    __tablename__ = "users"
    email = Column(String(120), unique=True, index=True)
    password = Column(String(255))
    username = Column(String(120), nullable=True)
    nickname = Column(String(120), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user)
    is_verified = Column(Boolean, default=False)

    lemons = relationship("Lemon", back_populates="user", uselist=False)

    def __repr__(self):
        if self.lemons:
            return f"<User(email={self.email}, nickname={self.nickname}, role={self.role.value}, is_verified={self.is_verified}, lemons={self.lemons.lemon_count})>"
        else:
            return f"<User(email={self.email}, nickname={self.nickname}, role={self.role.value}, is_verified={self.is_verified}, lemons=None)>"
