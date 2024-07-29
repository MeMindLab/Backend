from datetime import datetime
from uuid import uuid4
from typing import TYPE_CHECKING


from enum import Enum as PythonEnum

from sqlalchemy import String, Enum, Boolean, Uuid, DateTime, event
from sqlalchemy.orm import (
    relationship,
    mapped_column,
    Mapped,
    Session,
    ORMExecuteState,
    with_loader_criteria,
)


from .common import CommonModel


if TYPE_CHECKING:
    from app.models.lemon import Lemon  # Defer import to avoid circular import


class UserRole(str, PythonEnum):
    user = "user"
    admin = "admin"


class SoftDeleteMixin:
    deleted_at = mapped_column(DateTime(timezone=True), nullable=True)

    def delete(self):
        if self.deleted_at is None:
            self.deleted_at = datetime.utcnow()

    def undelete(self):
        self.deleted_at = None

    def is_deleted(self):
        return self.deleted_at is not None


class User(CommonModel, SoftDeleteMixin):
    __tablename__ = "users"
    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    nickname: Mapped[str | None] = mapped_column(String(120), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.user)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    mobile: Mapped[str | None] = mapped_column(String(120), nullable=True)
    delete_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    lemons: Mapped["Lemon"] = relationship(
        "Lemon", back_populates="user", uselist=False
    )

    def __repr__(self):
        if self.lemons is not None:
            return f"<User(email={self.email}, nickname={self.nickname}, role={self.role.value}, is_verified={self.is_verified}, lemons={self.lemons.lemon_count})>"
        else:
            return f"<User(email={self.email}, nickname={self.nickname}, role={self.role.value}, is_verified={self.is_verified}, lemons=None)>"


@event.listens_for(Session, "do_orm_execute")
def apply_soft_delete_filter(state: ORMExecuteState):
    if not state.is_select:
        return

    if state.is_select and not state.statement.get_execution_options().get(
        "include_deleted"
    ):
        state.statement = state.statement.options(
            with_loader_criteria(
                SoftDeleteMixin,
                lambda cls: cls.deleted_at.is_(None),
                include_aliases=True,
            )
        )
