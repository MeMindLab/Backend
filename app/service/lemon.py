from fastapi import Depends, HTTPException
from typing import Optional


from app.models.lemon import Lemon
from app.schemas.lemon import LemonCreate

from app.repository.lemon import LemonRepository
from app.repository.user import UserRepository


class LemonService:
    def __init__(
        self,
        lemon_repository: LemonRepository = Depends(LemonRepository),
        user_repository: UserRepository = Depends(UserRepository),
    ):
        self.lemon_repository = lemon_repository
        self.user_repository = user_repository

    async def create_lemon_for_user(
        self, lemon_create: LemonCreate, user_id: int
    ) -> Lemon:
        lemon = Lemon.create(request=lemon_create, user_id=user_id)
        saved_lemon = await self.lemon_repository.save_lemon(lemon=lemon)
        return saved_lemon

    async def get_lemon_by_user(self, user_id: int) -> Optional[Lemon]:
        if user_id is None:
            raise HTTPException(status_code=404, detail="User id is required!")

        lemon = self.lemon_repository.get_lemon_by_user_id(user_id)
        if lemon is None:
            raise HTTPException(
                status_code=404, detail=f"Lemon not found for user_id={user_id}"
            )

        return lemon
