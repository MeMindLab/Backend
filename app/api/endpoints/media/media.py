from fastapi import APIRouter, UploadFile, Depends, File
from app.service.supbase import SupabaseService
from pydantic import BaseModel
from uuid import UUID

media_module = APIRouter(prefix="")


class ImageUpload(BaseModel):
    id: UUID
    conversation_id: int


class ImageUploadResponse(BaseModel):
    image_url: str
    converstaion_id: str


@media_module.post("/upload", status_code=200)
async def upload_image(
    self,
    supabase: SupabaseService = Depends(),
    file: UploadFile = File(...),
) -> str:
    upload_url = await supabase.upload_image(file)

    return upload_url
