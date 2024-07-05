import openai
from typing import Dict, List
from fastapi import Depends

from langchain_openai import ChatOpenAI
from langchain.prompts.few_shot import FewShotChatMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks import StreamingStdOutCallbackHandler

from app.core.config import config
from app.core.dependencies import get_db
from app.prompt.examples import example


class OpenAIChatClient:
    def __init__(self):
        openai.api_key = config.OPENAI_API_KEY

    @staticmethod
    def create_chat_instance(self) -> ChatOpenAI:
        print(config.OPENAI_API_KEY)
        return ChatOpenAI(
            temperature=0.1,
            streaming=True,
            callbacks=[
                StreamingStdOutCallbackHandler(),
            ],
        )


class ChatPromptGenerator:
    @staticmethod
    def generate_chat_prompt() -> str:
        # 사용자와 AI의 대화 예제를 기본 프롬프트로 생성합니다.
        example_prompt = ChatPromptTemplate.from_messages(
            [("human", "{user}"), ("ai", "{ai}")],
        )

        # Few-shot learning을 위한 예제
        examples = example  # 이곳에서 example을 사용

        # Few-shot learning을 위한 프롬프트 생성
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            examples=examples, example_prompt=example_prompt
        )

        # 최종 대화 프롬프트 생성
        removed = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You're a useful AI emotional counselor. 
                    Your name is 구르미.
                    You are my best friend, empathize with my feelings and ask questions.
                    You are informal and use a casual tone of voice.
                    """,
                ),
                few_shot_prompt,
                (
                    "ai",
                    """
                    Hi, I'm Gurumi! 😊
                    Tell me about your day or how you're feeling.
                    I'm here to listen to what you have to say.
                    """,
                ),
                ("human", "{user}"),
            ]
        )

        return removed


class ChatMemoryService:
    def __init__(self, memory):
        self.memory = memory

    def add_message(self, message):
        """사용자의 메시지를 메모리에 추가합니다."""
        self.memory.add(message)

    def get_history(self):
        """전체 대화 히스토리를 조회합니다."""
        return list(self.memory)


class MessageService:
    def __init__(self, session=Depends(get_db)):
        self.session = session
        self.chat_instance = OpenAIChatClient.create_chat_instance
        self.chat_prompt = ChatPromptGenerator().generate_chat_prompt()

        self.chat_prompt_generator = ChatPromptGenerator()

    async def get_all_full_messages(self, conversation_id: str):
        """해당 conversation에서 나누었던 message들을 모두 리턴하는 함수"""
        pass

    async def answer_conversation(self, user_text: str) -> str:
        try:
            # 이전 대화 내역이 있으면 채팅에 추가합니다.

            # 사용자 입력을 채팅에 추가합니다.

            prompt = self.chat_prompt
            chat_chain = prompt | self.chat_instance

            response = await chat_chain.invoke({"user": user_text})

            return response.content
        except Exception as e:
            # 오류 처리를 원하는 방식으로 추가합니다.
            print(f"Error in answering conversation: {e}")
            return "Error: Failed to respond to conversation"
