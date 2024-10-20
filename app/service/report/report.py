from uuid import UUID
from datetime import date
from fastapi import Depends, HTTPException

from app.repository.report import ReportRepository
from app.service.report import KeywordExtractor, EmotionExtractor, SummaryExtractor
from app.schemas.report import (
    ReportSummaryBase,
    EmotionBase,
    ReportBase,
    ReportCreateResponse,
    WeeklyScore,
)
from app.utils.image import ImageUtil
from .message_getter import MessageGetter
from .. import LemonService


class ReportService:
    def __init__(
        self,
        keyword_extractor: KeywordExtractor = Depends(KeywordExtractor),
        summary_extractor: SummaryExtractor = Depends(SummaryExtractor),
        emotion_extractor: EmotionExtractor = Depends(EmotionExtractor),
        report_repository: ReportRepository = Depends(ReportRepository),
        message_getter: MessageGetter = Depends(MessageGetter),
        image_util: ImageUtil = Depends(ImageUtil),
        lemon_service: LemonService = Depends(LemonService),
    ):
        self.keyword_extractor = keyword_extractor
        self.summary_extractor = summary_extractor
        self.emotion_extractor = emotion_extractor
        self.report_repository = report_repository
        self.message_getter = message_getter
        self.image_util = image_util
        self.lemon_service = lemon_service

    async def get_daily_report(self, conversation_id: UUID) -> ReportBase:
        report = await self.report_repository.get_report_by_conversation_id(
            conversation_id
        )

        chat_history = await self.message_getter.get_chat_history(conversation_id)

        report_summary = ReportSummaryBase(
            summary=report.report_summary.contents,
            tags=[tag for tag in report.report_summary.tags[0].tags]
            if report.report_summary.tags
            else [],
        )

        emotion = report.emotions
        percentages = emotion.calculate_percentages()

        emotions_base = EmotionBase(
            comfortable_percentage=percentages["comfortable_percentage"],
            happy_percentage=percentages["happy_percentage"],
            sad_percentage=percentages["sad_percentage"],
            joyful_percentage=percentages["joyful_percentage"],
            annoyed_percentage=percentages["annoyed_percentage"],
            lethargic_percentage=percentages["lethargic_percentage"],
            total_score=emotion.total_score,
        )

        images = await self.report_repository.get_images_by_conversation_id(
            conversation_id
        )

        image_urls = [
            await self.image_util.get_image_url_by_path(image.path) for image in images
        ]

        response = ReportBase(
            report_id=report.id,
            report_summary=report_summary,
            emotions=emotions_base,
            conversation_id=report.conversation_id,
            drawing_diary=report.drawing_diary,
            chat_history=chat_history,
            images=image_urls,
        )

        return response

    async def get_daily_report_by_id(self, report_id: UUID):
        report = await self.report_repository.get_report_by_id(report_id)
        chat_history = await self.message_getter.get_chat_history(
            report.conversation_id
        )
        report_summary = ReportSummaryBase(
            summary=report.report_summary.contents,
            tags=[tag for tag in report.report_summary.tags[0].tags]
            if report.report_summary.tags
            else [],
        )

        emotion = report.emotions
        percentages = emotion.calculate_percentages()

        emotions_base = EmotionBase(
            comfortable_percentage=percentages["comfortable_percentage"],
            happy_percentage=percentages["happy_percentage"],
            sad_percentage=percentages["sad_percentage"],
            joyful_percentage=percentages["joyful_percentage"],
            annoyed_percentage=percentages["annoyed_percentage"],
            lethargic_percentage=percentages["lethargic_percentage"],
            total_score=emotion.total_score,
        )

        images = await self.report_repository.get_images_by_conversation_id(
            report.conversation_id
        )

        image_urls = [
            await self.image_util.get_image_url_by_path(image.path) for image in images
        ]

        response = ReportBase(
            report_id=report.id,
            report_summary=report_summary,
            emotions=emotions_base,
            conversation_id=report.conversation_id,
            drawing_diary=report.drawing_diary,
            chat_history=chat_history,
            images=image_urls,
        )

        return response

    async def create_report(
        self, conversation_id: UUID, user_id: UUID
    ) -> ReportCreateResponse:
        existing_report = await self.report_repository.get_report_by_conversation_id(
            conversation_id
        )

        if existing_report:
            raise HTTPException(
                status_code=400, detail="Report already exists for this conversation"
            )

        keywords_result = await self.keyword_extractor.get_keywords(conversation_id)
        keywords = keywords_result["keywords"]

        summary_result = await self.summary_extractor.get_summary(conversation_id)
        summary = summary_result["summary"]

        emotion_result = await self.emotion_extractor.get_emotions(conversation_id)

        report_summary = await self.report_repository.create_report_summary(summary)
        await self.report_repository.create_tags(keywords, report_summary.id)
        emotion = await self.report_repository.create_emotion(
            emotions=emotion_result["emotions"],
            sentiment=emotion_result["sentiment"],
        )

        report = await self.report_repository.create_report(
            drawing_diary_id=None,
            emotion_id=emotion.id,
            report_summary_id=report_summary.id,
            conversation_id=conversation_id,
        )

        await self.lemon_service.decrement_lemon_by_user_id(user_id)

        return ReportCreateResponse(
            report_id=report.id,
            keyword=keywords,
        )

    async def get_search_reports(self, keywords, limit: int, cursor: str | None = None):
        result = await self.report_repository.get_search_reports(
            keywords, limit=limit, cursor=cursor
        )

        return result

    async def get_monthly_reports(
        self, year: int, month: int, limit: int, cursor: UUID | None
    ):
        # 해당 월의 대화 리스트 가져오기
        reports = await self.report_repository.get_monthly_reports(
            month=month, year=year, cursor=cursor, limit=limit
        )

        return reports

    async def get_weekly_scores(
        self, target_date: date, user_id: UUID
    ) -> list[WeeklyScore]:
        reports = await self.report_repository.get_weekly_scores(target_date, user_id)

        weekly_scores = [
            WeeklyScore(
                date=report.created_at.strftime("%m/%d"),
                score=report.emotions.total_score if report.emotions else 0,
            )
            for report in reports
        ]
        return weekly_scores
