# app/models/report.py
from uuid import uuid4
from sqlalchemy import (
    Integer,
    Uuid,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.common import TimestampMixin


class Tags(Base, TimestampMixin):
    __tablename__ = "tags"
    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid4)
    tags = mapped_column(type_=JSON, nullable=False)
    report_summary_id = mapped_column(
        Uuid, ForeignKey("report_summary.id"), nullable=False
    )

    report_summary = relationship("ReportSummary", back_populates="tags")


class ReportSummary(Base, TimestampMixin):
    __tablename__ = "report_summary"
    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid4)
    score = mapped_column(Integer, nullable=False)

    tags = relationship("Tags", back_populates="report_summary")


class Emotion(Base, TimestampMixin):
    __tablename__ = "emotion"
    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid4)
    comfortable: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    happy: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sad: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fun: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    annoyed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lethargic: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    report_id = mapped_column(Uuid, ForeignKey("report.id"), nullable=False)
    report_emotion = relationship("Report", back_populates="emotions")


class Report(Base, TimestampMixin):
    __tablename__ = "report"
    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid4)

    emotions = relationship("Emotion", back_populates="report_emotion")
