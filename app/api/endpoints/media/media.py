from uuid import UUID


from fastapi import APIRouter, UploadFile, Depends, File
from app.service.supbase import SupabaseService
from app.service.image import ImageService
from app.auth.authenticate import get_current_user

from pydantic import BaseModel


media_module = APIRouter(prefix="")


class ImageUpload(BaseModel):
    id: UUID
    conversation_id: int


class ImageUploadResponse(BaseModel):
    image_url: str
    conversation_id: str


@media_module.post("/upload", status_code=200)
async def upload_image(
    supabase: SupabaseService = Depends(),
    file: UploadFile = File(...),
    auth: UUID = Depends(get_current_user),
):
    uploaded_url = await supabase.upload_image(user_id=auth, file=file)

    return ImageUploadResponse(
        converstaion_id="conversatino id",
        image_url=uploaded_url,
    )


class GenerateImageRequest(BaseModel):
    keywords: list[str]


@media_module.post("/generate-image", status_code=200)
async def generate_image(
    image_service: ImageService = Depends(ImageService),
    q: GenerateImageRequest = Depends(),
):
    result = await image_service.generate_image(keywords=q.keywords)
    return result
