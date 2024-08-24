from datetime import datetime
from uuid import UUID
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.core.dependencies import get_db


class UserRepository:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def read_all_user(self, skip: int, limit: int) -> list[User]:
        query = (
            select(User)
            .outerjoin(User.lemons)
            .options(selectinload(User.lemons))
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def find_user_by_id(self, user_id: UUID) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        user = result.scalars().first()
        return user

    async def find_user_by_nickname(self, nickname: str) -> User:
        query = select(User).where(User.nickname == nickname)
        user = await self.session.execute(query)
        return user.scalars().first()

    async def find_user_by_email(self, email: str):
        query = select(User).where(User.email == email)
        user = await self.session.execute(query)
        return user.scalars().first()

    async def save_user(self, user: User) -> User:
        self.session.add(instance=user)
        await self.session.commit()  # db save
        await self.session.refresh(instance=user)
        return user

    async def deactivate_user(self, user: User, delete_reasons: list[str]):
        try:
            user.delete_reasons = delete_reasons
            user.delete()
            user.is_active = False

            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)

        except Exception as e:
            await self.session.rollback()  # Rollback in case of error
            print(f"Error during deactivation: {e}")

    async def reactivate_user(self, user: User):
        try:
            user.undelete()  # Undelete using the mixin method
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        except Exception as e:
            await self.session.rollback()
            print(f"Error during reactivation: {e}")
