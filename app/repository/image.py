from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy import select

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
