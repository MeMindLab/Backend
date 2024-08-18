import os
from urllib.parse import urlparse
from fastapi import Depends, HTTPException
from uuid import UUID

from app.repository.image import ImageRepository
from app.repository.chat import MessageRepository
from app.service.llm import OpenAIClient
from app.models.image import Image


class ImageService:
    def __init__(
        self,
        image_repository: ImageRepository = Depends(ImageRepository),
        openai_client: OpenAIClient = Depends(OpenAIClient),
        message_repository: MessageRepository = Depends(),
    ):
        self.image_repository = image_repository
        self.openai_client = openai_client
        self.message_repository = message_repository

    async def handle_image_message(self, url: str, conversation_id: UUID, index: int):
        try:
            # 이미지 메세지 저장

            path, extension = self.extract_path_and_extension(url)

            # 메시지 생성
            message = await self.message_repository.create_message(
                conversation_id=conversation_id,
                is_from_user=True,
                index=index,
            )

            image = Image.create(
                path=path,
                extension=extension,
                conversation_id=conversation_id,
                message_id=message.id,
            )
            await self.image_repository.save_image(image)
        except Exception as e:
            # 로깅 또는 적절한 에러 처리
            raise HTTPException(status_code=500, detail=f"Error saving image: {e}")

    def extract_path_and_extension(self, url: str) -> tuple[str, str]:
        # URL에서 경로 추출
        parsed_url = urlparse(url)
        path = parsed_url.path

        # 경로에서 파일 이름과 확장자 추출
        filename = path.split("/")[-1]  # 파일 이름 추출
        extension = filename.split(".")[-1] if "." in filename else ""  # 확장자 추출

        path_parts = path.split("/")
        if "Images" in path_parts:
            index = path_parts.index("Images")
            path = "/".join(path_parts[index:])  # 'Images'와 그 이후의 경로

        return path, extension

    def get_file_extension_from_dallE_url(self, url: str) -> str:
        path = urlparse(url).path
        filename = os.path.basename(path)
        _, extension = os.path.splitext(filename)

        return extension.lstrip(".")

    async def generate_image(self, keywords: list[str]) -> str:
        client = self.openai_client.create_openai_instance()
        keyword_string = ", ".join(keywords)

        prompt = f"""
        Create a whimsical image based on these keywords
        Keywords:{keyword_string}
    
        A delightful image filled with elements related to the keywords. 
        - It should have a landscape painting feel and be colorful and related to your keywords, and it would be nice to have some natural or topographical elements added.
        
        Make sure each keyword is clearly represented. 
        """

        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        return image_url
