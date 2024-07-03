from fastapi import Depends, HTTPException
from typing import Optional


from app.models.lemon import Lemon
from app.repository.lemon import LemonRepository


class LemonService:
    def __init__(self, lemon_repository: LemonRepository = Depends(LemonRepository)):
        self.lemon_repository = lemon_repository

    async def create_lemon(self, lemon: Lemon) -> Lemon:
        return await self.lemon_repository.save_lemon(lemon)

    async def get_lemon_by_user(self, user_id: int) -> Optional[Lemon]:
        if user_id is None:
            raise HTTPException(status_code=404, detail="User id is required!")

        lemon = self.lemon_repository.get_lemon_by_user_id(user_id)
        if lemon is None:
            raise HTTPException(
                status_code=404, detail=f"Lemon not found for user_id={user_id}"
            )

        return lemon
