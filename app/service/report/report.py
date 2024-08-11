from uuid import UUID
from fastapi import Depends

from app.repository.report import ReportRepository
from app.service.report import KeywordExtractor, EmotionExtractor, SummaryExtractor
from app.schemas.report import ReportSummaryBase, EmotionBase, ReportBase
from .message_getter import MessageGetter


class ReportService:
    def __init__(
        self,
        keyword_extractor: KeywordExtractor = Depends(KeywordExtractor),
        summary_extractor: SummaryExtractor = Depends(SummaryExtractor),
        emotion_extractor: EmotionExtractor = Depends(EmotionExtractor),
        report_repository: ReportRepository = Depends(ReportRepository),
        message_getter: MessageGetter = Depends(MessageGetter),
    ):
        self.keyword_extractor = keyword_extractor
        self.summary_extractor = summary_extractor
        self.emotion_extractor = emotion_extractor
        self.report_repository = report_repository
        self.message_getter = message_getter

    async def get_daily_report(self, conversation_id: UUID):
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

        response = ReportBase(
            report_id=report.id,
            report_summary=report_summary,
            emotions=emotions_base,
            conversation_id=report.conversation_id,
            drawing_diary_id=report.drawing_diary_id,
            chat_history=chat_history,
        )

        return response

    async def create_report(self, conversation_id: UUID):
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

        # 최종 리턴 값
        return {
            "report_id": report.id,
            "keyword": keywords,
        }
