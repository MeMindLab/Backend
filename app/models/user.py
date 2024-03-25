from sqlalchemy import Column, String, Enum
from enum import Enum as PythonEnum
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

    def __repr__(self):
        return f"{self.email}"


metadata = Base.metadata


