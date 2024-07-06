from app.core.config import get_config, ConfigTemplate
from fastapi import Depends, UploadFile
from typing import BinaryIO
from PIL import Image
from supabase import create_client
import uuid
from multiprocessing import get_logger


class ImageUtil:
    def __init__(
        self,
        config: ConfigTemplate = Depends(get_config),
    ):
        self.config = config
        self.supabase_client = create_client(
            supabase_key=config.SUPABASE_KEY,
            supabase_url=config.SUPABASE_URL,
        )

    def upload_image_to_supabase(
        self, file: BinaryIO, bucket_name: str, file_path: str
    ) -> None:
        self.supabase_client.storage.from_(bucket_name).upload(
            file=file, path=file_path, file_options={"content-type": "image/jpeg"}
        )

    async def upload_image_storagea(
        self, file: BinaryIO, filename: str, path: str, save_name: str
    ):
        # 파일 확장자 및 크기 검증
        await self._validate_file_extension(file, filename)
        extension = filename.split(".")[-1]

        file_path = f"{path}/{save_name}_{uuid.uuid4()}.{extension}"
        try:
            response = await self.upload_image_to_supabase(
                file=file, bucket_name=self.config.SUPABASE_BUCKET, file_path=file_path
            )
            print(response)
            return response
        except Exception as e:
            get_logger().error(e)
            raise ValueError(f"Failed to upload image to Supabase: {str(e)}")

    async def _validate_file_extension(self, file: BinaryIO, filename: str):
        if not filename.endswith((".jpg", ".jpeg", ".png")):
            raise ValueError("Invalid file extension")

        # 이미지 크기 제한
        file.seek(0, 2)
        if file.tell() > self.config.MAX_UPLOAD_IMAGE_SIZE:
            raise ValueError("File size exceeds maximum size")

        # 이미지 파일 콘텐츠 검증
        file.seek(0)
        try:
            with Image.open(file) as img:
                img.verify()
        except Exception:
            raise ValueError("Invalid image file")

        # 파일 포인터를 다시 처음으로 이동
        file.seek(0)
