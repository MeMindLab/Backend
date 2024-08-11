import os
from urllib.parse import urlparse
from fastapi import Depends

from app.repository.image import ImageRepository
from app.service.llm import OpenAIClient


class ImageService:
    def __init__(
        self,
        image_repository: ImageRepository = Depends(ImageRepository),
        openai_client: OpenAIClient = Depends(OpenAIClient),
    ):
        self.image_repository = image_repository
        self.openai_client = openai_client

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
