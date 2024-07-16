from uuid import UUID
from fastapi import Depends
from datetime import date, datetime

from langchain_openai import ChatOpenAI
from langchain.prompts.few_shot import FewShotChatMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks import AsyncIteratorCallbackHandler


from app.core.config import ConfigTemplate, get_config
from app.core.dependencies import get_db
from app.prompt.examples import example
from app.repository.chat import ConversationRepository, MessageRepository


class OpenAIChatClient:
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


class ChatPromptGenerator:
    @staticmethod
    def generate_chat_prompt() -> ChatPromptTemplate:
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
        final_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You're a useful AI emotional counselor. 
                    Your name is 구르미.
                    You are my best friend, empathize with my feelings and ask questions.
                    You are informal and use a casual tone of voice.
                    Your first message to the user should be fixed to '안녕 난 구르미야 :)
                    오늘 하루 있었던 일이나 기분을 말해줘.
                    나 구르미가 모두 다 들어줄게!)'
                    At the end of the conversation, you should message
                    "Thanks for talking to 구르미, see you tomorrow!"
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

        return final_prompt


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
    def __init__(
        self,
        openai_chat_client: OpenAIChatClient = Depends(OpenAIChatClient),
        session=Depends(get_db),
    ):
        self.session = session
        self.chat_instance = openai_chat_client.chat_instance
        self.chat_prompt = ChatPromptGenerator().generate_chat_prompt()

    async def get_all_full_messages(self, conversation_id: str):
        """해당 conversation에서 나누었던 message들을 모두 리턴하는 함수"""
        pass

    async def answer_conversation(self, user_text: str) -> str:
        try:
            # 이전 대화 내역이 있으면 채팅에 추가합니다.

            # 사용자 입력을 채팅에 추가합니다.

            prompt = self.chat_prompt

            chat_chain = prompt | self.chat_instance

            response = await chat_chain.ainvoke({"user": user_text})

            return response.content
        except Exception as e:
            # 오류 처리를 원하는 방식으로 추가합니다.
            print(f"Error in answering conversation: {e}")
            return "Error: Failed to respond to conversation"


class ConversationService:
    def __init__(
        self,
        session=Depends(get_db),
        message_repository: MessageRepository = Depends(),
        conversation_repository: ConversationRepository = Depends(
            ConversationRepository
        ),
        message_service: MessageService = Depends(),
    ):
        self.session = session
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository
        self.message_service = message_service

    async def get_conversation(self, diary_date: date, user_id: UUID):
        result = await self.conversation_repository.get_conversation(
            diary_date, user_id
        )
        print(result)
        pass

    # conversation 생성, message load, 길이 check
    async def start_conversation(self, diary_date: date, user_id: UUID):
        """conversation이 있으면, 대화 내용을 리턴하고, 없으면 새로 conversation을 생성하는 함수"""
        existing_conversation = await self.get_conversation(diary_date, user_id)

        # if existing_conversation:
        #     # 기존 대화가 있는 경우, 대화 기록을 가져옵니다.
        #
        # else:

        # conversation이 존재하지 않는 경우, 새로 conversation 생성

        new_conversation = await self.conversation_repository.create_conversation(
            user_id, diary_date
        )

        # 초기 메시지 생성을 위해 GPT-3.5를 사용하여 대화 시작
        initial_message = await self.message_service.answer_conversation("")
        # 메시지 저장
        await self.message_repository.create_message(
            new_conversation.id,
            is_from_user=False,
            message=initial_message,
            index=0,
        )

        # # chat history
        chat_history = await self.message_repository.get_messages(new_conversation.id)

        return {
            "conversation_id": new_conversation.id,
            "chat_history": chat_history,
            "is_enough": False,  # 나중에 백엔드에서 로직을 추가하여 처리
        }
