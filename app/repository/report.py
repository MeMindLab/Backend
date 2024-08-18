from uuid import UUID


from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.report import Report, Tags, ReportSummary, DrawingDiary, Emotion
from app.models.image import Image
from app.core.dependencies import get_db


class ReportRepository:
    def __init__(
        self,
        session: AsyncSession = Depends(get_db),
    ):
        self.session = session

    async def create_tags(self, keywords: list[str], report_summary_id: UUID) -> Tags:
        tags = Tags(tags=keywords, report_summary_id=report_summary_id)

        self.session.add(tags)
        await self.session.commit()
        await self.session.refresh(tags)
        return tags

    async def create_report_summary(self, summary: str) -> ReportSummary:
        report_summary = ReportSummary(contents=summary)
        self.session.add(report_summary)
        await self.session.commit()
        await self.session.refresh(report_summary)
        return report_summary

    async def create_drawing_diary(
        self, image_url: str, image_title: str
    ) -> DrawingDiary:
        drawing_diary = DrawingDiary.create(image_url, image_title)
        self.session.add(drawing_diary)
        await self.session.commit()
        await self.session.refresh(drawing_diary)
        return drawing_diary

    async def create_emotion(self, emotions: dict, sentiment: int) -> Emotion:
        emotion = Emotion.create(
            total_score=sentiment,
            comfortable_score=emotions["comfortable"],
            happy_score=emotions["happy"],
            sad_score=emotions["sadness"],
            joyful_score=emotions["joyful"],
            annoyed_score=emotions["annoyed"],
            lethargic_score=emotions["lethargic"],
        )

        self.session.add(emotion)
        await self.session.commit()
        await self.session.refresh(emotion)
        return emotion

    async def update_emotion(self, emotion: Emotion) -> Emotion:
        self.session.add(Emotion)
        await self.session.commit()
        await self.session.refresh(emotion)
        return emotion

    async def create_report(
        self,
        drawing_diary_id: UUID | None,
        emotion_id: UUID,
        report_summary_id: UUID,
        conversation_id: UUID,
    ) -> Report:
        report = Report(
            drawing_diary_id=drawing_diary_id,
            emotion_id=emotion_id,
            report_summary_id=report_summary_id,
            conversation_id=conversation_id,
        )
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_report_by_conversation_id(self, conversation_id: UUID) -> Report:
        query = (
            select(Report)
            .options(
                selectinload(Report.emotions),
                selectinload(Report.report_summary).selectinload(ReportSummary.tags),
                selectinload(Report.drawing_diary),
            )
            .where(Report.conversation_id == conversation_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_images_by_conversation_id(self, conversation_id: UUID):
        query = (
            select(Image)
            .where(Image.conversation_id == conversation_id)
            .order_by(Image.created_at)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_report(self, report: Report) -> Report:
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report
