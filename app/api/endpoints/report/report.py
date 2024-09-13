from uuid import UUID
from datetime import date, datetime
from fastapi import APIRouter, Path, Query, Depends
from app.auth.authenticate import get_current_user
from typing import Optional


from app.service import ReportService
from app.schemas.report import (
    ReportListRequest,
    ReportListResponse,
    ReportCreateRequest,
    ReportCreateResponse,
    WeeklyScoresResponse,
)

report_module = APIRouter(prefix="")


@report_module.post("/create-daily", response_model=ReportCreateResponse)
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


@report_module.get("/{report_id}")
async def get_reports_handler(
    report_id: UUID = Path(..., title="Report ID", description="The ID of the Report"),
    report_service: ReportService = Depends(),
):
    result = await report_service.get_daily_report_by_id(report_id)
    return result


@report_module.post("/search", response_model=ReportListResponse)
async def search_reports(
    q: ReportListRequest = Depends(),
    report_service: ReportService = Depends(),
):
    reports = await report_service.get_search_reports(
        keywords=q.keywords,
        limit=q.limit,
        cursor=q.cursor,
    )
    next_cursor = str(reports[-1].snowflake_id) if len(reports) >= q.limit else None

    return ReportListResponse(
        reports=[
            ReportListResponse.Report(
                report_id=report.id,
                conversation_id=report.conversation_id,
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
    reports = await report_service.get_monthly_reports(
        year=year, month=month, cursor=cursor, limit=limit
    )

    next_cursor = str(reports[-1].snowflake_id) if len(reports) >= limit else None

    return ReportListResponse(
        reports=[
            ReportListResponse.Report(
                report_id=report.id,
                conversation_id=report.conversation_id,
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


@report_module.get("/weekly-scores")
async def weekly_scores_handler(
    target_date: date = Query(
        datetime.utcnow().date(), description="Date in YYYY-MM-DD format"
    ),
    report_service: ReportService = Depends(),
):
    results = await report_service.get_weekly_scores(target_date)
    return WeeklyScoresResponse(results=results)
