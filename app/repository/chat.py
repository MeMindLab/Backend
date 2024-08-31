import uuid
from datetime import datetime, date
from uuid import UUID
from typing import List

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.models.chat import Conversation, Message
from app.core.dependencies import get_db


class ConversationRepository:
    def __init__(
        self,
        session: AsyncSession = Depends(get_db),
    ):
        self.session = session

    async def get_monthly_conversations(
        self, user_id: UUID, month: int, year: int
    ) -> list[Conversation]:
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .where(Conversation.date >= date(year, month, 1))
            .where(Conversation.date < date(year + (month // 12), (month % 12) + 1, 1))
        )

        result = await self.session.execute(query)
        conversations = []
        for row in result.scalars().all():
            conversation = Conversation(
                id=row.id,
                user_id=row.user_id,
                date=row.date,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            conversations.append(conversation)

        return conversations

    async def get_conversation(
        self, date: datetime.date, user_id: UUID
    ) -> list[Conversation]:
        """해당 일자에 conversation를 리턴하는 함수"""

        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .where(Conversation.date == date)
        )

        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def create_conversation(self, user_id: UUID, date_object: datetime.date):
        """새로운 대화를 생성하는 함수"""
        new_conversation = Conversation.create(user_id=user_id, date=date_object)
        self.session.add(new_conversation)
        await self.session.commit()
        await self.session.refresh(instance=new_conversation)
        return new_conversation

    async def find_conversations_by_user_id(self, user_id: UUID):
        query = select(Conversation).where(Conversation.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete_conversation(self, conversation_id: UUID):
        query = delete(Conversation).where(Conversation.id == conversation_id)
        await self.session.execute(query)
        await self.session.commit()


class MessageRepository:
    def __init__(
        self,
        session: AsyncSession = Depends(get_db),
    ):
        self.session = session

    async def get_messages(self, conversation_id: UUID) -> List[Message]:
        """해당 conversation에서 나누었던 message들을 모두 리턴하는 함수"""

        query = (
            select(Message)
            .options(selectinload(Message.image))
            .filter(Message.conversation_id == conversation_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete_message(self, message_id: UUID):
        query = delete(Message).where(Message.id == message_id)
        await self.session.execute(query)
        await self.session.commit()

    async def create_message(
        self,
        conversation_id: UUID,
        is_from_user: bool,
        index: int,
        message: str = "",
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
