from uuid import UUID
from fastapi import APIRouter, UploadFile, Depends, Path
from app.auth.authenticate import get_current_user
from pydantic import BaseModel

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


@report_module.get("/{conversation_id}")
async def get_reports(
    conversation_id: UUID = Path(
        ..., title="User ID", description="The ID of the user"
    ),
    report_service: ReportService = Depends(),
):
    result = await report_service.get_daily_report(conversation_id)
    return result
