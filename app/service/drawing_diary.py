from fastapi import Depends, HTTPException
from uuid import UUID

from app.repository.image import ImageRepository
from app.repository.drawing_image import DrawingImageRepository


from app.models.report import DrawingDiary
from app.repository.report import ReportRepository
from app.utils.image import ImageUtil


class DrawingDiaryService:
    def __init__(
        self,
        image_repository: ImageRepository = Depends(ImageRepository),
        image_utils: ImageUtil = Depends(ImageUtil),
        drawing_diary_repository=Depends(DrawingImageRepository),
        report_repository=Depends(ReportRepository),
    ):
        self.image_repository = image_repository
        self.image_utils = image_utils
        self.drawing_diary_repository = drawing_diary_repository
        self.report_repository = report_repository

    async def create_drawing_diary(
        self,
        image_url: str,
        image_title: str,
        conversation_id: UUID,
    ):
        if not image_url or not image_title:
            raise HTTPException(status_code=400, detail="Invalid image url or title")

        try:
            # Create DrawingDiary instance
            drawing_diary = DrawingDiary.create(
                image_url=image_url, image_title=image_title
            )

            # Save to repository
            await self.drawing_diary_repository.save_drawing_diary(drawing_diary)

            existing_report = await self.report_repository.get_report(conversation_id)

            existing_report.drawing_diary = drawing_diary.drawing_diary_id

            await self.report_repository.update_report(existing_report)

        except Exception as e:
            # Handle any errors during the save or update process
            raise HTTPException(
                status_code=500, detail="Failed to process drawing diary and report"
            )
