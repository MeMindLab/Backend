from uuid import UUID
from fastapi import Depends, HTTPException
from pydantic import BaseModel

from langchain_core.output_parsers import JsonOutputParser


from app.repository.chat import MessageRepository
from app.service.llm import OpenAIClient, PromptGenerator
from .message_getter import MessageGetter


class SummaryResponse(BaseModel):
    summary: str


class SummaryExtractor:
    def __init__(
        self,
        message_getter: MessageGetter = Depends(MessageGetter),
        openai_chat_client: OpenAIClient = Depends(OpenAIClient),
        message_repository: MessageRepository = Depends(),
    ):
        self.llm = openai_chat_client.chat_instance
        self.prompt = PromptGenerator().generate_summary_prompt()
        self.message_repository = message_repository
        self.message_getter = message_getter

    async def get_summary(self, conversation_id: UUID):
        chat_history = await self.message_getter.get_chat_history(conversation_id)

        output_parser = JsonOutputParser(pydantic_object=SummaryResponse)
        chain = self.prompt | self.llm | output_parser

        response = await chain.ainvoke({"conversation": chat_history})

        return response
