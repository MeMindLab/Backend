from fastapi import Depends


from app.models.user import User
from app.core.dependencies import get_db


from sqlalchemy.ext.asyncio import AsyncSession

# from sqlalchemy.future import select
from sqlalchemy import select


class UserRepository:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def read_all_user(self, skip: int, limit: int) -> list[User]:
        result = await self.session.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    async def find_user_by_id(self, user_id: str) -> User | None:
        query = select(User).filter(User.id == user_id)
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
