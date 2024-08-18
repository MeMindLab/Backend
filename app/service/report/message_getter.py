from uuid import UUID
from fastapi import Depends, HTTPException

from app.repository.chat import MessageRepository


class MessageGetter:
    def __init__(
        self,
        message_repository: MessageRepository = Depends(MessageRepository),
    ):
        self.message_repository = message_repository

    async def get_chat_history(self, conversation_id: UUID):
        """Retrieve and format chat history for LangChain"""

        conversation = await self.message_repository.get_messages(conversation_id)

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        message_list = [
            {
                "role": "user" if message.is_from_user else "ai",
                "content": message.message if message.message else message.image_url,
                "is_image": True if message.image_url else False,
            }
            for message in conversation
        ]

        return message_list
