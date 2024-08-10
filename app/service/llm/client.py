from fastapi import Depends

from openai import AsyncOpenAI


from langchain_openai import ChatOpenAI
from langchain.callbacks import AsyncIteratorCallbackHandler

from app.core.config import ConfigTemplate, get_config


class OpenAIClient:
    def __init__(
        self,
        config: ConfigTemplate = Depends(get_config),
    ):
        self.config = config
        self.chat_instance = self.create_chat_instance()

    def create_chat_instance(self) -> ChatOpenAI:
        # ChatOpenAI 설정
        chat = ChatOpenAI(
            api_key=self.config.OPENAI_API_KEY,
            temperature=0.1,
            streaming=True,
            callbacks=[
                AsyncIteratorCallbackHandler(),
            ],
        )
        return chat

    def create_openai_instance(self) -> AsyncOpenAI:
        # ChatOpenAI 설정
        client = AsyncOpenAI(
            api_key=self.config.OPENAI_API_KEY,
        )
        return client
