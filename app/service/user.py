from fastapi import Depends, HTTPException


from app.models.user import User
from app.repository.user import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository = Depends(UserRepository)):
        self.user_repository = user_repository

    async def get_user_list(self) -> list[User]:
        return await self.user_repository.get_user_list()

    async def get_user_by_id(self, user_id: str) -> User:
        user = await self.user_repository.find_user_by_id(user_id=user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    async def get_user_by_username(self, username: str) -> User:
        user = await self.user_repository.find_user_by_username(username=username)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def find_user_by_email(self, email: str):
        user = await self.user_repository.find_user_by_email(email=email)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user
