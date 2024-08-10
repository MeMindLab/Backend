import os
from urllib.parse import urlparse

from fastapi import Depends, HTTPException, status

from app.models.image import Image
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
        keywords_test = "a white siamese cat and dog"
        keyword_string = ", ".join(keywords)

        prompt = f"""
        Create an adorable and whimsical image based on the following keywords:

        keywords:{keywords}
        
        A delightful and cozy illustration filled with charming elements related to the keywords. In the center, a friendly owl is serving a cup of hot,steaming decaf coffee to a smiling fox. The background is a whimsical autumn garden with a warm, golden sunset. Colorful leaves are falling, and there are miniature pumpkins and gourds scattered around. A small table is set with a plate of delicious, crispy chicken and a variety of tasty side dishes. The atmosphere is warm and inviting, with a sense of comfort and happiness. The use of soft colors and playful characters creates a heartwarming image that captures the essence of the user's experience. 
        
        The image should include:
        
        - Cute, playful characters or elements directly related to each keyword
        - Soft pastel colors and gentle lighting to enhance the cuteness
        
        
        Make sure each keyword is clearly represented. 
        The style is cute and cartoonish, reminiscent of a delightful children's illustration.

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
