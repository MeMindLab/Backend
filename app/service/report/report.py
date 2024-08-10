from uuid import UUID
from fastapi import Depends

from app.repository.report import ReportRepository
from app.service.report import KeywordExtractor
from app.service.report.summary import SummaryExtractor


class ReportService:
    def __init__(
        self,
        keyword_extractor: KeywordExtractor = Depends(KeywordExtractor),
        summary_extractor: SummaryExtractor = Depends(SummaryExtractor),
        report_repository: ReportRepository = Depends(ReportRepository),
    ):
        self.keyword_extractor = keyword_extractor
        self.summary_extractor = summary_extractor
        self.report_repository = report_repository

    async def create_report(self, conversation_id: UUID):
        # Step 1: DrawingDiary 생성

        keywords_result = await self.keyword_extractor.get_keywords(conversation_id)
        keywords = keywords_result["keywords"]

        summary_result = await self.summary_extractor.get_summary(conversation_id)
        summary = summary_result["summary"]

        # 4. 보고서 생성 및 저장

        # Step 2: ReportSummary 생성

        # report_summary = await self.report_repository.create_report_summary(summary)
        # await self.report_repository.create_tags(keywords, report_summary.id)

        # Step 3: Tags 생성 및 ReportSummary와 연결

        # Step 4: Emotion 생성

        # Step 5: Report 생성

        # 최종 리턴 값
        return {
            "report_id": "report id soon add",
            "keyword": keywords,
        }
