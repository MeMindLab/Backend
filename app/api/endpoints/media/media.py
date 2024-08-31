from uuid import UUID


from fastapi import APIRouter, UploadFile, Depends, File
from app.service.supbase import SupabaseService
from app.service.drawing_diary import DrawingDiaryService
from app.auth.authenticate import get_current_user

from pydantic import BaseModel


media_module = APIRouter(prefix="")


class ImageUploadResponse(BaseModel):
    conversation_id: UUID
    image_url: str


class UploadImageRequest(BaseModel):
    conversation_id: UUID
    is_drawing: bool


@media_module.post("/upload", status_code=200)
async def upload_image(
    upload_req: UploadImageRequest = Depends(),
    file: UploadFile = File(...),
    supabase: SupabaseService = Depends(),
    auth: UUID = Depends(get_current_user),
):
    uploaded_url = await supabase.upload_image(
        user_id=auth,
        conversation_id=upload_req.conversation_id,
        file=file,
        is_drawing=upload_req.is_drawing,
    )

    return ImageUploadResponse(
        conversation_id=upload_req.conversation_id,
        image_url=uploaded_url,
    )


class GenerateImageRequest(BaseModel):
    keywords: list[str]


@media_module.post("/generate-image", status_code=200)
async def generate_image(
    drawing_diary_service: DrawingDiaryService = Depends(DrawingDiaryService),
    q: GenerateImageRequest = Depends(),
):
    result = await drawing_diary_service.generate_image(keywords=q.keywords)
    return result


class UpdateImageRequest(BaseModel):
    conversation_id: UUID
    image_url: str
    image_title: str


class UpdateImageResponse(BaseModel):
    message: str


@media_module.post("/update-image", status_code=200)
async def update_dalle_image(
    update_request: UpdateImageRequest = Depends(),
    drawing_service: DrawingDiaryService = Depends(),
):
    await drawing_service.create_drawing_diary(
        image_url=update_request.image_url,
        conversation_id=update_request.conversation_id,
        image_title=update_request.image_title,
    )

    return UpdateImageResponse(message="success to save")
