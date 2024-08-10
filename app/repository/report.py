import uuid
from datetime import datetime, date
from uuid import UUID
from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report, Tags, ReportSummary
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
