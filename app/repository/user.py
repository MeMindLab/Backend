from fastapi import Depends


from app.models.user import User
from app.core.dependencies import get_db

from sqlalchemy import delete, select


class UserRepository:
    def __init__(self, session=Depends(get_db)):
        self.session = session

    async def get_user_list(self) -> list[User]:
        query = select(User).order_by(User.created_at.desc()).limit(10)

        users = await self.session.execute(query)

        return users.scalars().all()

    async def find_user_by_id(self, user_id: str) -> User | None:
        query = select(User).where(User.id == user_id)

        user = await self.session.execute(query)

        return user.scalars().first()

    async def find_user_by_username(self, username: str) -> User:
        query = select(User).where(User.username == username)
        user = await self.session.execute(query)
        return user.scalars().first()

    async def find_user_by_email(self, email: str):
        query = select(User).where(User.email == email)
        user = await self.session.execute(query)

        return user.scalars().first()
