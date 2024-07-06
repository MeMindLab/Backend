from fastapi import APIRouter
from app.api.endpoints.media.media import media_module


upload_router = APIRouter()

upload_router.include_router(
    media_module,
    prefix="",
    tags=["Media"],
    responses={404: {"description": "Not found"}},
)
