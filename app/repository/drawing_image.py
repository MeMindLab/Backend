from fastapi import Depends


from app.core.dependencies import get_db
from app.models.report import DrawingDiary


class DrawingImageRepository:
    def __init__(self, session=Depends(get_db)):
        self.session = session

    async def save_drawing_diary(self, drawing_diary: DrawingDiary):
        self.session.add(drawing_diary)
        await self.session.commit()
        await self.session.refresh(drawing_diary)
        return drawing_diary

    async def update_drawing_diary(self, drawing_diary: DrawingDiary):
        pass
