from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Path, Query, Depends
from app.auth.authenticate import get_current_user
from pydantic import BaseModel, Field
from typing import Optional

from app.service.report.report import ReportService
from app.schemas.report import (
    ReportListRequest,
    ReportListResponse,
    ReportCreateRequest,
)

report_module = APIRouter(prefix="")


@report_module.post("/create-daily")
async def create_report(
    report_input: ReportCreateRequest,
    auth: UUID = Depends(get_current_user),
    report_service: ReportService = Depends(),
):
    result = await report_service.create_report(
        conversation_id=report_input.conversation_id
    )

    return result


@report_module.get("/detail/{conversation_id}")
async def get_reports(
    conversation_id: UUID = Path(
        ..., title="User ID", description="The ID of the user"
    ),
    report_service: ReportService = Depends(),
):
    result = await report_service.get_daily_report(conversation_id)
    return result


@report_module.post("/search")
async def search_reports(
    q: ReportListRequest = Depends(),
    report_service: ReportService = Depends(),
):
    reports = await report_service.get_search_reports(
        keywords=q.keywords,
        limit=q.limit,
        cursor=q.cursor,
    )
    next_cursor = reports[-1].id if len(reports) >= q.limit else None

    return ReportListResponse(
        reports=[
            ReportListResponse.Report(
                id=report.id,
                tags=[
                    tag
                    for tags_object in report.report_summary.tags
                    for tag in tags_object.tags
                ],
                ai_summary=report.report_summary.contents,
                thumbnail=report.drawing_diary.image_url
                if report.drawing_diary
                else None,
                created_at=report.created_at,
            )
            for report in reports
        ],
        next_cursor=next_cursor,
    )


@report_module.get("/monthly-reports")
async def monthly_reports_handler(
    year: int = Query(..., description="Year of the reports"),
    month: int = Query(..., description="Month of the reports"),
    limit: int = Query(20, ge=1, le=100, description="Number of reports per page"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    report_service: ReportService = Depends(),
):
    reports = await report_service.get_monthly_reports(year=year, month=month)
    next_cursor = reports[-1].id if len(reports) >= limit else None

    return ReportListResponse(
        reports=[
            ReportListResponse.Report(
                id=report.id,
                tags=[
                    tag
                    for tags_object in report.report_summary.tags
                    for tag in tags_object.tags
                ],
                ai_summary=report.report_summary.contents,
                thumbnail=report.drawing_diary.image_url
                if report.drawing_diary
                else None,
                created_at=report.created_at,
            )
            for report in reports
        ],
        next_cursor=next_cursor,
    )
