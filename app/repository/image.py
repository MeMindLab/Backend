from fastapi import Depends

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
