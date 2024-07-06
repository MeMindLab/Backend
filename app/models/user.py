from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Enum, Boolean, Integer
from enum import Enum as PythonEnum

from sqlalchemy.orm import relationship, mapped_column, Mapped
from .common import CommonModel


if TYPE_CHECKING:
    from app.models.lemon import Lemon  # Defer import to avoid circular import


class UserRole(str, PythonEnum):
    user = "user"
    admin = "admin"


class User(CommonModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    nickname: Mapped[str | None] = mapped_column(String(120), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.user)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    lemons: Mapped["Lemon"] = relationship(
        "Lemon", back_populates="user", uselist=False
    )

    def __repr__(self):
        if self.lemons is not None:
            return f"<User(email={self.email}, nickname={self.nickname}, role={self.role.value}, is_verified={self.is_verified}, lemons={self.lemons.lemon_count})>"
        else:
            return f"<User(email={self.email}, nickname={self.nickname}, role={self.role.value}, is_verified={self.is_verified}, lemons=None)>"
