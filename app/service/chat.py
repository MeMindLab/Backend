from uuid import UUID
from fastapi import Depends
from datetime import date
from operator import itemgetter

from langchain_openai import ChatOpenAI
from langchain.prompts.few_shot import FewShotChatMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.memory import (
    ConversationSummaryBufferMemory,
)
from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
    Runnable,
    RunnableParallel,
)
from langchain_core.output_parsers import StrOutputParser

from app.core.config import ConfigTemplate, get_config
from app.core.dependencies import get_db
from app.prompt.examples import example
from app.repository.chat import ConversationRepository, MessageRepository


class EnoughJudge:
    @staticmethod
    def is_enough(conversation_length) -> bool:
        return conversation_length > 13


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
            [
                ("human", "{user}"),
                ("ai", "{ai}"),
            ],
        )

        examples = example
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            examples=examples, example_prompt=example_prompt
        )

        final_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You're a useful AI emotional counselor. 
                    Your name is 구르미.
                    You are my best friend, empathize with my feelings and ask questions.
                    You are informal and use a casual tone of voice.
                    Your first message to the user should be fixed to '안녕 난 구르미야 :) 오늘 하루 있었던 일이나 기분을 말해줘. 나 구르미가 모두 다 들어줄게!)'
                    """,
                ),
                (
                    "ai",
                    """
                    Hi, I'm Gurumi! 😊
                    Tell me about your day or how you're feeling.
                    I'm here to listen to what you have to say.
                    """,
                ),
                few_shot_prompt,
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{user}"),
            ]
        )

        return final_prompt


class ConversationChain(Runnable):
    def __init__(
        self,
        llm,
        prompt,
        input_key: str = "user",
    ):
        self.prompt = prompt
        self.llm = llm

        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=120,
            return_messages=True,
            memory_key="chat_history",
        )

        self.input_key = input_key
        self.chain = (
            RunnablePassthrough.assign(
                chat_history=RunnableLambda(self.memory.aload_memory_variables)
                | itemgetter(self.memory.memory_key)
            )
            | prompt
            | llm
            | StrOutputParser()
        )

    async def add_user_message(self, message):
        """Adds a user's message to memory."""
        await self.memory.asave_context(inputs={"human": message}, outputs={"ai": ""})

    async def add_memory(self, user_message: str, ai_message: str):
        """사용자와 AI 메시지를 모두 메모리에 추가합니다."""
        await self.memory.asave_context(
            inputs={"human": user_message}, outputs={"ai": ai_message}
        )

    async def invoke(self, query, configs=None, **kwargs):
        answer = await self.chain.ainvoke({self.input_key: query})
        await self.memory.asave_context(inputs={"human": query}, outputs={"ai": answer})
        return answer


class MessageService:
    def __init__(
        self,
        session=Depends(get_db),
        openai_chat_client: OpenAIChatClient = Depends(OpenAIChatClient),
        message_repository: MessageRepository = Depends(),
    ):
        self.session = session
        self.llm = openai_chat_client.chat_instance
        self.chat_prompt = ChatPromptGenerator().generate_chat_prompt()
        self.message_repository = message_repository
        self.conversation_chain = ConversationChain(
            llm=self.llm,
            prompt=self.chat_prompt,
        )

    async def get_messages_from_ai(self, text: str):
        try:
            response = await self.conversation_chain.invoke(text)
            return response
        except Exception as e:
            # 오류 처리를 원하는 방식으로 추가합니다.
            print(f"Error in processing dialogue: {e}")
            return "Error: Failed to process dialogue"

    async def get_all_full_messages(self, conversation_id: UUID):
        """해당 conversation에서 나누었던 message들을 모두 리턴하는 함수"""
        messages = await self.message_repository.get_messages(conversation_id)
        return messages

    async def answer_message(self, user_text: str, conversation_id: UUID):
        # 이전 대화 내역이 있으면 채팅에 추가합니다.
        messages = await self.get_all_full_messages(conversation_id)
        order = len(messages)

        # 메모리에 챗봇의 응답도 추가합니다.
        for message in messages:
            await self.conversation_chain.add_memory(
                user_message=message.message if message.is_from_user else "",
                ai_message=message.message if not message.is_from_user else "",
            )

        # # 유저 메세지 저장
        await self.message_repository.create_message(
            conversation_id=conversation_id,
            is_from_user=True,
            message=user_text,
            index=order + 1,
        )

        # chain에 대화 요청
        ai_message = await self.get_messages_from_ai(user_text)

        # 요청된 대화 저장
        await self.message_repository.create_message(
            conversation_id=conversation_id,
            is_from_user=False,
            message=ai_message,
            index=order + 2,
        )

        # 챗봇의 답변을 사용자 메시지와 함께 반환합니다.
        return {
            "message": ai_message,
            "is_enough": EnoughJudge.is_enough(order),
        }


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
        return result

    # conversation 생성, message load, 길이 check
    async def start_conversation(self, diary_date: date, user_id: UUID):
        """conversation이 있으면, 대화 내용을 리턴하고, 없으면 새로 conversation을 생성하는 함수"""
        existing_conversation = await self.get_conversation(diary_date, user_id)

        if existing_conversation:
            print(existing_conversation)

            # 기존 대화가 있는 경우, 대화 기록을 가져옵니다.
            chat_history = await self.message_repository.get_messages(
                existing_conversation.id
            )

            return {
                "conversation_id": existing_conversation.id,
                "chat_history": chat_history,
                "is_enough": EnoughJudge.is_enough(len(chat_history)),
            }
        else:
            # conversation이 존재하지 않는 경우, 새로 conversation 생성

            new_conversation = await self.conversation_repository.create_conversation(
                user_id, diary_date
            )

            initial_message = "안녕 난 구르미야 :) 오늘 하루 있었던 일이나 기분을 말해줘. 나 구르미가 모두 다 들어줄게!"

            # 메시지 저장
            await self.message_repository.create_message(
                new_conversation.id,
                is_from_user=False,
                message=initial_message,
                index=0,
            )

            # chat history
            chat_history = await self.message_repository.get_messages(
                new_conversation.id
            )

            return {
                "conversation_id": new_conversation.id,
                "chat_history": chat_history,
                "is_enough": EnoughJudge.is_enough(len(chat_history)),
            }
