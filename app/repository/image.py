from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy import select, delete

from app.core.dependencies import get_db
from app.models.image import Image


class ImageRepository:
    def __init__(self, session=Depends(get_db)):
        self.session = session

    async def save_image(self, image: Image) -> Image:
        self.session.add(image)
        await self.session.commit()
        await self.session.refresh(image)
        return image

    async def delete_image(self, image_id: UUID):
        query = delete(Image).where(Image.id == image_id)
        await self.session.execute(query)
        await self.session.commit()

    async def delete_image_by_message_id(self, message_id: UUID):
        try:
            query = delete(Image).where(Image.message_id == message_id)
            await self.session.execute(query)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            print(f"Error during images deletion: {e}")
            raise e

    async def get_image_by_id(self, image_id: UUID) -> Image:
        query = select(Image).where(Image.id == image_id)
        result = await self.session.execute(query)

        return result.scalars().one_or_none()

    async def upload_image(self, conversation_id: UUID, image_id: UUID) -> Image:
        exist_image = await self.get_image_by_id(image_id=image_id)

        if not exist_image:
            raise HTTPException(status_code=404, detail="Image not found")

        # conversation_id 업데이트
        exist_image.conversation_id = conversation_id

        self.session.add(instance=exist_image)
        await self.session.commit()
        await self.session.refresh(exist_image)
        return exist_image
