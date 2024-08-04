from fastapi import APIRouter
from app.api.endpoints.report.report import report_module

report_router = APIRouter()

report_router.include_router(
    report_module,
    prefix="/report",
    tags=["Report"],
    responses={404: {"description": "Not found"}},
)
