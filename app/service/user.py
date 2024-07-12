from fastapi import Depends, HTTPException

from app.models.user import User
from app.repository.user import UserRepository
from app.auth import hashpassword
from app.schemas.user import UserCreate, UserUpdate


hash_password = hashpassword.HashPassword()


class UserService:
    def __init__(self, user_repository: UserRepository = Depends(UserRepository)):
        self.user_repository = user_repository

    async def get_user_list(self, skip: int, limit: int) -> list[User]:
        return await self.user_repository.read_all_user(skip, limit)

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.user_repository.find_user_by_id(user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    async def get_user_by_nickname(self, nickname: str) -> User:
        user = await self.user_repository.find_user_by_nickname(nickname=nickname)
        return user

    async def find_user_by_email(self, email: str):
        user = await self.user_repository.find_user_by_email(email=email)
        return user

    async def create_new_user(self, user: User) -> User:
        new_user = User(
            email=user.email,
            password=hash_password.create_hash(user.password),
            nickname=user.nickname,
        )

        return await self.user_repository.save_user(user=new_user)

    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdate,
    ) -> User:
        user = await self.get_user_by_id(user_id=user_id)
        user.email = user_data.email
        user.nickname = user_data.nickname

        # Check if is_verified is provided
        if user_data.is_verified is not None:
            user.is_verified = user_data.is_verified

        # Check if mobile is provided
        if user_data.mobile is not None:
            user.mobile = user_data.mobile

        updated_user = await self.user_repository.save_user(user=user)

        return updated_user

    @staticmethod
    def validate_nickname_length(nickname: str):
        """사용자 이름과 닉네임의 길이를 검증합니다."""
        if len(nickname) < 3 or len(nickname) > 10:
            detail = {"message": "Nickname must be between 3 and 10 characters"}
            status_code = 400
            raise HTTPException(status_code=status_code, detail=detail)
