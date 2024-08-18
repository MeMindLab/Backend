from uuid import UUID
import datetime

from fastapi import Depends, UploadFile, HTTPException
from app.utils.image import ImageUtil
from app.repository.image import ImageRepository


class SupabaseService:
    def __init__(
        self,
        image_util: ImageUtil = Depends(ImageUtil),
        image_repository: ImageRepository = Depends(ImageRepository),
    ):
        self.image_util = image_util
        self.image_repository = image_repository

    async def upload_image(
        self,
        user_id: UUID,
        conversation_id: UUID,
        file: UploadFile,
        is_drawing: bool = False,
    ):
        if file is None or file.filename is None:
            raise HTTPException(status_code=400, detail="File is required")

        path = (
            f"Images/{user_id}/{conversation_id}/drawing"
            if is_drawing
            else f"Images/{user_id}/{conversation_id}"
        )

        # image upload
        image = await self.image_util.upload_image_storage(
            file=file.file,
            filename=file.filename,
            path=path,  # file path to add conversation id
            save_name=datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        )

        # save image to db
        image = await self.image_repository.save_image(image=image)

        # link to conversaton table
        await self.image_repository.upload_image(
            conversation_id=conversation_id, image_id=image.id
        )

        # return image_url
        image_url = await self.image_util.get_image_url_by_path(file_path=image.path)

        return image_url
