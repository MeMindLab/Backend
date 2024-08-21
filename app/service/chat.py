from uuid import UUID
from fastapi import Depends
from datetime import date

from app.core.dependencies import get_db
from app.repository.chat import ConversationRepository, MessageRepository
from app.service.image import ImageService
from app.service.llm import OpenAIClient, PromptGenerator, ConversationChain
from app.schemas.chat import MessageBase
from app.utils.image import ImageUtil


class EnoughJudge:
    @staticmethod
    def is_enough(conversation_length) -> bool:
        return conversation_length > 13


class MessageService:
    def __init__(
        self,
        session=Depends(get_db),
        openai_chat_client: OpenAIClient = Depends(OpenAIClient),
        message_repository: MessageRepository = Depends(),
        image_service: ImageService = Depends(),
    ):
        self.session = session
        self.llm = openai_chat_client.chat_instance
        self.chat_prompt = PromptGenerator().generate_chat_prompt()
        self.message_repository = message_repository
        self.conversation_chain = ConversationChain(
            llm=self.llm,
            prompt=self.chat_prompt,
        )
        self.image_service = image_service

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

    async def answer_message(
        self, user_text: str, conversation_id: UUID, image_url: str, is_image: bool
    ):
        # 이전 대화 내역이 있으면 채팅에 추가합니다.
        messages = await self.get_all_full_messages(conversation_id)
        order = len(messages)

        if is_image and image_url:
            # 이미지 메세지 처리
            await self.image_service.handle_image_message(
                url=image_url, conversation_id=conversation_id, index=order + 1
            )

            # 대화 기록에 이미지를 추가했으므로 챗봇의 메모리에 추가할 필요는 없음.
            return {
                "message": "Image received and stored.",
                "is_enough": EnoughJudge.is_enough(order),
            }

        else:
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
        image_utils: ImageUtil = Depends(),
    ):
        self.session = session
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository
        self.message_service = message_service
        self.image_utils = image_utils

    async def get_monthly_conversations(self, year: int, month: int, user_id: UUID):
        # 해당 월의 대화 리스트 가져오기
        conversations = await self.conversation_repository.get_monthly_conversations(
            user_id=user_id,
            month=month,
            year=year,
        )

        return conversations

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
            # 기존 대화가 있는 경우, 대화 기록을 가져옵니다.
            chat_history = await self.message_repository.get_messages(
                existing_conversation.id
            )

            image_urls = [
                await self.image_utils.get_image_url_by_path(message.image[0].path)
                if message.image
                else None
                for message in chat_history
            ]

            chat_history_list = [
                MessageBase(
                    is_from_user=message.is_from_user,
                    order=message.index,
                    message_id=message.id,
                    message_timestamp=message.message_timestamp,
                    message=message.message,
                    image_url=image_urls[i],
                )
                for i, message in enumerate(chat_history)
            ]

            return {
                "conversation_id": existing_conversation.id,
                "chat_history": chat_history_list,
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

            chat_history_list = [
                MessageBase(
                    is_from_user=message.is_from_user,
                    order=message.index,
                    message_id=message.id,
                    message_timestamp=message.message_timestamp,
                    message=message.message,
                    image_url=None,
                )
                for message in chat_history
            ]

            return {
                "conversation_id": new_conversation.id,
                "chat_history": chat_history_list,
                "is_enough": EnoughJudge.is_enough(len(chat_history)),
            }
