import os
import uuid
import io
from urllib.parse import urlparse
from PIL import Image
from fastapi import Depends
from typing import BinaryIO
from supabase_py_async import AsyncClient
from multiprocessing import get_logger

from app.core.config import get_config, ConfigTemplate
from app.models.image import Image as ImageModel


class ImageUtil:
    def __init__(
        self,
        config: ConfigTemplate = Depends(get_config),
    ):
        self.config = config
        self.supabase_client = AsyncClient(
            supabase_key=config.SUPABASE_KEY,
            supabase_url=config.SUPABASE_URL,
        )

    def extract_path_and_extension(self, url: str) -> tuple[str, str]:
        # URL에서 경로 추출
        parsed_url = urlparse(url)
        path = parsed_url.path

        filename = path.split("/")[-1]
        extension = filename.split(".")[-1] if "." in filename else ""

        path_parts = path.split("/")
        if "Images" in path_parts:
            index = path_parts.index("Images")
            path = "/".join(path_parts[index:])

        return path, extension

    async def get_image_url_by_path(self, file_path: str):
        image_url = await self.supabase_client.storage.from_(
            self.config.SUPABASE_BUCKET
        ).get_public_url(file_path)
        return image_url

    async def upload_image_to_supabase(
        self, file: io.BufferedReader, bucket_name: str, file_name: str
    ) -> None:
        await self.supabase_client.storage.from_(bucket_name).upload(
            file=file, path=file_name, file_options={"content-type": "image/jpeg"}
        )

    async def save_binary_to_filesystem(self, file: BinaryIO, filename: str) -> None:
        with open(filename, "wb") as f:
            f.write(file.read())

    async def upload_image_storage(
        self, file: BinaryIO, filename: str, path: str, save_name: str
    ) -> ImageModel:
        # 파일 확장자 및 크기 검증
        await self._validate_file_extension(file, filename)
        extension = filename.split(".")[-1]
        file_path = f"{path}/{save_name}_{uuid.uuid4()}.{extension}"

        try:
            # save image to file sytem
            await self.save_binary_to_filesystem(file, f"./{filename}")

            with open(f"./{filename}", "rb") as f:
                await self.upload_image_to_supabase(
                    file=f,
                    bucket_name=self.config.SUPABASE_BUCKET,
                    file_name=file_path,
                )
                os.remove(f"./{filename}")  # Remove file after uploading

            return ImageModel(
                path=file_path,
                extension=extension,
            )

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
