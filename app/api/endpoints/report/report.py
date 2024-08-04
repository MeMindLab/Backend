from uuid import UUID
from fastapi import APIRouter, UploadFile, Depends, File
from app.auth.authenticate import get_current_user
from pydantic import BaseModel

from app.service.report.report import ReportService


report_module = APIRouter(prefix="")


class ReportInSchema(BaseModel):
    conversation_id: UUID


@report_module.post("/create-daily", response_model=None)
async def create_report(
    report_input: ReportInSchema,
    auth: UUID = Depends(get_current_user),
    report_service: ReportService = Depends(),
):
    result = await report_service.create_report(
        conversation_id=report_input.conversation_id
    )

    return result
