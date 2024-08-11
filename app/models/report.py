# app/models/report.py
# 레포트 관리 모델

import uuid
from typing import Dict
from sqlalchemy import (
    Integer,
    Uuid,
    JSON,
    String,
    ForeignKey,
    Text,
    func,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.common import TimestampMixin


# 그림일기(생성형 이미지)
class DrawingDiary(Base, TimestampMixin):
    __tablename__ = "drawing_diary"
    drawing_diary_id = mapped_column(
        Uuid, primary_key=True, index=True, default=uuid.uuid4
    )
    image_url = mapped_column(String(256), nullable=False)
    image_title = mapped_column(String(50), nullable=False)

    reports = relationship("Report", back_populates="drawing_diary")

    @classmethod
    def create(cls, image_url: str, image_title: str):
        return cls(
            image_url=image_url,
            image_title=image_title,
        )


class Emotion(Base, TimestampMixin):
    __tablename__ = "emotion"
    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)

    comfortable_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    happy_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sad_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    joyful_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    annoyed_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lethargic_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    report = relationship(
        "Report",
        back_populates="emotions",
    )

    @hybrid_property
    def total_emotion_score(self) -> int:
        return (
            self.comfortable_score
            + self.happy_score
            + self.sad_score
            + self.joyful_score
            + self.annoyed_score
            + self.lethargic_score
        )

    @total_emotion_score.expression
    def _total_emotion_score_expression(cls) -> int:
        return (
            func.coalesce(cls.comfortable_score, 0)
            + func.coalesce(cls.happy_score, 0)
            + func.coalesce(cls.sad_score, 0)
            + func.coalesce(cls.joyful_score, 0)
            + func.coalesce(cls.annoyed_score, 0)
            + func.coalesce(cls.lethargic_score, 0)
        )

    @classmethod
    def calculate_emotion_percentages(cls) -> Dict[str, Mapped[float]]:
        total_score = cls._total_emotion_score_expression()
        total = func.coalesce(
            total_score,
            0.0,
        )

        return {
            "comfortable_percent": func.round(
                func.coalesce(cls.comfortable_score / total * 100, 0.0), 2
            ),
            "happy_percent": func.round(
                func.coalesce(cls.happy_score / total * 100, 0.0), 2
            ),
            "sad_percent": func.round(
                func.coalesce(cls.sad_score / total * 100, 0.0), 2
            ),
            "fun_percent": func.round(
                func.coalesce(cls.joyful_score / total * 100, 0.0), 2
            ),
            "annoyed_percent": func.round(
                func.coalesce(cls.annoyed_score / total * 100, 0.0), 2
            ),
            "lethargic_percent": func.round(
                func.coalesce(cls.lethargic_score / total * 100, 0.0), 2
            ),
        }

    @classmethod
    def create(
        cls,
        comfortable_score: int,
        happy_score: int,
        sad_score: int,
        joyful_score: int,
        annoyed_score: int,
        lethargic_score: int,
    ) -> "Emotion":
        return cls(
            comfortable_score=comfortable_score,
            happy_score=happy_score,
            sad_score=sad_score,
            joyful_score=joyful_score,
            annoyed_score=annoyed_score,
            lethargic_score=lethargic_score,
        )


class ReportSummary(Base, TimestampMixin):
    __tablename__ = "report_summary"
    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    contents = mapped_column(Text, nullable=False)

    tags = relationship("Tags", back_populates="report_summary")

    reports = relationship("Report", back_populates="report_summary")


class Tags(Base, TimestampMixin):
    __tablename__ = "tags"
    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    tags = mapped_column(type_=JSON, nullable=False)
    report_summary_id = mapped_column(
        Uuid, ForeignKey("report_summary.id"), nullable=False
    )

    report_summary = relationship("ReportSummary", back_populates="tags")

    @classmethod
    def create(cls, tags: list[str], report_id: uuid.UUID):
        return cls(
            tags=tags,
            report_summary_id=report_id,
        )


class Report(Base, TimestampMixin):
    __tablename__ = "report"
    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    drawing_diary_id = mapped_column(
        ForeignKey("drawing_diary.drawing_diary_id"),
        nullable=True,
    )
    emotion_id = mapped_column(ForeignKey("emotion.id"), nullable=False)
    report_summary_id = mapped_column(ForeignKey("report_summary.id"), nullable=False)
    conversation_id = mapped_column(ForeignKey("conversations.id"), nullable=False)

    conversation = relationship("Conversation", back_populates="reports")

    drawing_diary = relationship(
        "DrawingDiary",
        back_populates="reports",
        foreign_keys=[drawing_diary_id],
    )
    emotions = relationship(
        "Emotion",
        back_populates="report",
    )
    report_summary = relationship(
        "ReportSummary",
        back_populates="reports",
    )

    @property
    def total_emotion_score(self):
        return self.emotions.total_score
