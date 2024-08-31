from fastapi import Depends, HTTPException
from uuid import UUID

from app.repository.image import ImageRepository
from app.repository.drawing_image import DrawingImageRepository

from app.service.llm import OpenAIClient, PromptGenerator
from app.models.report import DrawingDiary
from app.repository.report import ReportRepository
from app.utils.image import ImageUtil


class DrawingDiaryService:
    def __init__(
        self,
        image_repository: ImageRepository = Depends(ImageRepository),
        image_utils: ImageUtil = Depends(ImageUtil),
        openai_client: OpenAIClient = Depends(OpenAIClient),
        drawing_diary_repository=Depends(DrawingImageRepository),
        report_repository=Depends(ReportRepository),
    ):
        self.image_repository = image_repository
        self.image_utils = image_utils
        self.drawing_diary_repository = drawing_diary_repository
        self.report_repository = report_repository
        self.openai_client = openai_client
        self.prompt_generator = PromptGenerator()

    async def create_drawing_diary(
        self,
        image_url: str,
        image_title: str,
        conversation_id: UUID,
    ):
        if not image_url or not image_title:
            raise HTTPException(status_code=400, detail="Invalid image url or title")

        existing_report = await self.report_repository.get_report_by_conversation_id(
            conversation_id
        )
        if not existing_report:
            raise HTTPException(status_code=404, detail="Report not found")

            # Create DrawingDiary instance
        drawing_diary = DrawingDiary.create(
            image_url=image_url, image_title=image_title
        )

        # Save to repository
        await self.drawing_diary_repository.save_drawing_diary(drawing_diary)

        existing_report.drawing_diary_id = drawing_diary.drawing_diary_id
        await self.report_repository.update_report(existing_report)

    async def generate_image(self, keywords: list[str]) -> str:
        client = self.openai_client.create_openai_instance()
        keyword_string = ", ".join(keywords)
        prompt = self.prompt_generator.generate_image_prompt(keyword_string)

        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        return image_url
