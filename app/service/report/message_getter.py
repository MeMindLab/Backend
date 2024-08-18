from uuid import UUID
from fastapi import Depends, HTTPException

from app.repository.chat import MessageRepository
from app.utils.image import ImageUtil


class MessageGetter:
    def __init__(
        self,
        message_repository: MessageRepository = Depends(MessageRepository),
        image_utils: ImageUtil = Depends(ImageUtil),
    ):
        self.message_repository = message_repository
        self.image_utils = image_utils

    async def get_chat_history(self, conversation_id: UUID):
        """Retrieve and format chat history for LangChain"""

        conversation = await self.message_repository.get_messages(conversation_id)

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        image_urls = {
            message.id: await self.image_utils.get_image_url_by_path(
                message.image[0].path
            )
            if message.image
            else None
            for message in conversation
        }

        message_list = [
            {
                "role": "user" if message.is_from_user else "ai",
                "content": message.message
                if message.message
                else image_urls.get(message.id),
                "is_image": True if message.image else False,
            }
            for message in conversation
        ]

        return message_list
