# app/models/report.py
# 레포트 관리 모델

import uuid
from typing import Dict
from sqlalchemy import (
    Integer,
    Uuid,
    BigInteger,
    String,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from snowflake import SnowflakeGenerator
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

    total_score: Mapped[int] = mapped_column(Integer, nullable=False)
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

    def calculate_percentages(self) -> Dict[str, float]:
        # Calculate the sum of all scores except total_score
        sum_scores = (
            self.comfortable_score
            + self.happy_score
            + self.sad_score
            + self.joyful_score
            + self.annoyed_score
            + self.lethargic_score
        )

        # Calculate the percentage for each score
        percentages = {
            "comfortable_percentage": round(
                (self.comfortable_score / sum_scores) * 100, 2
            ),
            "happy_percentage": round((self.happy_score / sum_scores) * 100, 2),
            "sad_percentage": round((self.sad_score / sum_scores) * 100, 2),
            "joyful_percentage": round((self.joyful_score / sum_scores) * 100, 2),
            "annoyed_percentage": round((self.annoyed_score / sum_scores) * 100, 2),
            "lethargic_percentage": round((self.lethargic_score / sum_scores) * 100, 2),
        }

        return percentages

    @classmethod
    def create(
        cls,
        total_score: int,
        comfortable_score: int,
        happy_score: int,
        sad_score: int,
        joyful_score: int,
        annoyed_score: int,
        lethargic_score: int,
    ) -> "Emotion":
        return cls(
            total_score=total_score,
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
    tags = mapped_column(type_=JSONB, nullable=False)

    report_summary_id = mapped_column(
        Uuid, ForeignKey("report_summary.id", ondelete="CASCADE"), nullable=False
    )

    report_summary = relationship(
        "ReportSummary",
        back_populates="tags",
    )

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
        ForeignKey("drawing_diary.drawing_diary_id", ondelete="CASCADE"),
        nullable=True,
    )
    emotion_id = mapped_column(
        ForeignKey("emotion.id", ondelete="CASCADE"), nullable=False
    )
    report_summary_id = mapped_column(
        ForeignKey("report_summary.id", ondelete="CASCADE"), nullable=False
    )
    conversation_id = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )

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

    snowflake_id = mapped_column(
        BigInteger,
        index=True,
        nullable=False,
        default=lambda: next(SnowflakeGenerator(42)),
    )

    @property
    def total_emotion_score(self):
        return self.emotions.total_score
