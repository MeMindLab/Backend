import json

from uuid import UUID
from fastapi import Depends

from app.service.report import KeywordExtractor


class ReportService:
    def __init__(
        self,
        keyword_extractor: KeywordExtractor = Depends(KeywordExtractor),
    ):
        self.keyword_extractor = keyword_extractor

    async def create_report(self, conversation_id: UUID):
        keywords_result = await self.keyword_extractor.get_keywords(conversation_id)
        keywords = keywords_result["keywords"]

        # 4. 보고서 생성 및 저장

        keyword_list = ["test", "test1", "test2"]
        summary = "summary!!"
        emotion = []
        # 최종 리턴 값
        return {"keywords": keywords}
