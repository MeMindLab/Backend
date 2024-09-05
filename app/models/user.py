from datetime import datetime, timedelta
from uuid import uuid4
from typing import TYPE_CHECKING, Optional


from enum import Enum as PythonEnum

from sqlalchemy import (
    String,
    Enum,
    Boolean,
    Uuid,
    DateTime,
    event,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import (
    relationship,
    mapped_column,
    Mapped,
    Session,
    ORMExecuteState,
    with_loader_criteria,
)
from sqlalchemy.dialects.postgresql import JSONB


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
    delete_reasons: Mapped[list[str]] = mapped_column(JSONB, nullable=True)

    # 추천인을 위한 자기 참조 관계 추가
    referrer_id: Mapped[Optional[Uuid]] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=True
    )
    referrer: Mapped["User"] = relationship(
        "User", remote_side=[id], backref="referred_users"
    )
    referral_code: Mapped[str] = mapped_column(
        String(10), unique=True, index=True, nullable=True
    )  # 추천인 코드 필드 추가

    referral_code_creation_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    referral_code_validity_period: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,  # 기본 유효 기간: 30일
    )  # 유효 기간(일 단위

    lemons: Mapped["Lemon"] = relationship(
        "Lemon", back_populates="user", uselist=False
    )

    def __repr__(self):
        referrer_email = self.referrer.email if self.referrer else None
        if self.lemons is not None:
            return f"<User(email={self.email}, nickname={self.nickname}, role={self.role.value}, is_verified={self.is_verified}, referrer={referrer_email}, lemons={self.lemons.lemon_count})>"
        else:
            return f"<User(email={self.email}, nickname={self.nickname}, role={self.role.value}, is_verified={self.is_verified}, referrer={referrer_email}, lemons=None)>"


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
