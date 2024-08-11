from uuid import UUID
from fastapi import Depends

from app.repository.report import ReportRepository
from app.service.report import KeywordExtractor, EmotionExtractor, SummaryExtractor


class ReportService:
    def __init__(
        self,
        keyword_extractor: KeywordExtractor = Depends(KeywordExtractor),
        summary_extractor: SummaryExtractor = Depends(SummaryExtractor),
        emotion_extractor: EmotionExtractor = Depends(EmotionExtractor),
        report_repository: ReportRepository = Depends(ReportRepository),
    ):
        self.keyword_extractor = keyword_extractor
        self.summary_extractor = summary_extractor
        self.emotion_extractor = emotion_extractor
        self.report_repository = report_repository

    async def create_report(self, conversation_id: UUID):
        keywords_result = await self.keyword_extractor.get_keywords(conversation_id)
        keywords = keywords_result["keywords"]

        summary_result = await self.summary_extractor.get_summary(conversation_id)
        summary = summary_result["summary"]

        emotion_result = await self.emotion_extractor.get_emotions(conversation_id)

        report_summary = await self.report_repository.create_report_summary(summary)
        await self.report_repository.create_tags(keywords, report_summary.id)
        emotion = await self.report_repository.create_emotion(
            emotions=emotion_result["emotions"]
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
