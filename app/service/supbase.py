from fastapi import Depends, UploadFile, HTTPException
from app.utils.image import ImageUtil
from app.repository.user import UserRepository


class SupabaseService:
    def __init__(
        self,
        image_util: ImageUtil = Depends(ImageUtil),
        user_repository: UserRepository = Depends(UserRepository),
    ):
        self.image_util = image_util
        self.user_repository = user_repository

    async def upload_image(self, file: UploadFile) -> str:
        if file is None or file.filename is None:
            raise HTTPException(status_code=400, detail="File is required")

        # image upload
        pass
