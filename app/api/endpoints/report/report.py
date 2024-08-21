from uuid import UUID
from fastapi import APIRouter, UploadFile, Depends, Path
from app.auth.authenticate import get_current_user
from pydantic import BaseModel, Field
from typing import Optional

from app.service.report.report import ReportService
from app.schemas.report import ReportBase


report_module = APIRouter(prefix="")


class ReportInSchema(BaseModel):
    conversation_id: UUID


@report_module.post("/create-daily")
async def create_report(
    report_input: ReportInSchema,
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


class ListRequestBase(BaseModel):
    limit: int = Field(20, ge=1, le=20)
    cursor: str | None = Field(None, max_length=100)


class ListResponseBase(BaseModel):
    next_cursor: UUID | None = None


class ReportListRequest(ListRequestBase):
    keywords: str


class ReportListResponse(ListResponseBase):
    class Report(BaseModel):
        id: UUID
        tags: list[str]
        ai_summary: str
        thumbnail: Optional[str] = None

    reports: list[Report]


@report_module.put("/search")
async def search_reports(
    q: ReportListRequest = Depends(),
    report_service: ReportService = Depends(),
):
    reports = await report_service.get_search_reports(
        keywords=q.keywords,
        limit=q.limit,
        cursor=q.cursor,
    )
    # next_cursor = reports[-1].id if len(reports) >= q.limit else None

    return {
        reports: "repors soon",
        #   "next_cursor": next_cursor,
    }

    # return ReportListResponse(
    #     reports=[
    #         ReportListResponse.Report(
    #             id=report.id,
    #             tags=[tag for tag in report.report_summary.tags],
    #             ai_summary=report.report_summary.contents,  # 예시로 추가된 필드
    #             thumbnail=report.drawing_diary.image_url
    #             if report.drawing_diary
    #             else None,
    #         )
    #         for report in reports
    #     ],
    #     next_cursor=next_cursor,
    # )
