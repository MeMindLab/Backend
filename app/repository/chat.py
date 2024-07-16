import uuid
from datetime import datetime
from uuid import UUID
from typing import List

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.chat import Conversation, Message
from app.core.dependencies import get_db


class ConversationRepository:
    def __init__(
        self,
        session: AsyncSession = Depends(get_db),
    ):
        self.session = session

    async def get_conversation(self, date: datetime.date, user_id: UUID):
        """해당 일자에 conversation_id를 리턴하는 함수"""
        # # 날짜 파싱
        # date_object = datetime.strptime(date, "%Y-%m-%d").date()

        # 기존 대화 검색
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .where(Conversation.date == date)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_conversation(self, user_id: UUID, date_object: datetime.date):
        """새로운 대화를 생성하는 함수"""

        new_conversation = Conversation.create(user_id=user_id, date=date_object)
        self.session.add(new_conversation)
        await self.session.commit()
        await self.session.refresh(instance=new_conversation)
        return new_conversation


class MessageRepository:
    def __init__(
        self,
        session: AsyncSession = Depends(get_db),
    ):
        self.session = session

    async def get_messages(self, conversation_id: UUID) -> List[Message]:
        """해당 conversation에서 나누었던 message들을 모두 리턴하는 함수"""

        query = select(Message).filter(Message.conversation_id == conversation_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_message(
        self,
        conversation_id: UUID,
        is_from_user: bool,
        message: str,
        index: int,
    ):
        """메시지를 저장하는 함수"""

        new_message = Message.create(
            conversation_id=conversation_id,
            is_from_user=is_from_user,
            message=message,
            index=index,
        )
        self.session.add(new_message)
        await self.session.commit()
        await self.session.refresh(instance=new_message)
        return new_message
