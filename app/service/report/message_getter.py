from uuid import UUID
from fastapi import Depends, HTTPException

from app.repository.chat import MessageRepository


class MessageGetter:
    def __init__(
        self,
        message_repository: MessageRepository = Depends(MessageRepository),
    ):
        self.message_repository = message_repository

    async def get_chat_history(self, conversation_id: UUID) -> list[dict[str, str]]:
        """Retrieve and format chat history for LangChain"""

        conversation = await self.message_repository.get_messages(conversation_id)

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        message_list = [
            {
                "role": "user" if message.is_from_user else "ai",
                "content": message.message if message.message else message.image_url,
            }
            for message in conversation
        ]

        return message_list
