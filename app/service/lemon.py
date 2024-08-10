from uuid import UUID
from fastapi import Depends, HTTPException
from typing import Optional


from app.models.lemon import Lemon
from app.schemas.lemon import LemonCreate, LemonUpdate

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
        self, lemon_create: LemonCreate, user_id: UUID
    ) -> Lemon:
        # 사용자의 레몬을 가져옴
        existing_lemon = await self.lemon_repository.get_lemon_by_user_id(user_id)

        # 이미 연결된 레몬이 있는 경우 처리
        if existing_lemon:
            raise HTTPException(
                status_code=400, detail=f"Lemon already exists for user_id={user_id}"
            )

        lemon = Lemon.create(request=lemon_create, user_id=user_id)
        saved_lemon = await self.lemon_repository.save_lemon(lemon=lemon)
        return saved_lemon

    async def get_lemon_by_user_id(self, user_id: int) -> Optional[Lemon]:
        if user_id is None:
            raise HTTPException(status_code=404, detail="User id is required!")

        lemon = await self.lemon_repository.get_lemon_by_user_id(user_id)
        if lemon is None:
            raise HTTPException(
                status_code=404, detail=f"Lemon not found for user_id={user_id}"
            )
        return lemon

    async def update_lemon_by_user_id(
        self, lemon_data: LemonUpdate, user_id: int
    ) -> Lemon:
        # 사용자의 레몬을 가져옴
        existing_lemon = await self.lemon_repository.get_lemon_by_user_id(user_id)

        if not existing_lemon:
            raise HTTPException(
                status_code=404, detail=f"Lemon not found for user_id={user_id}"
            )

        # 레몬 정보 업데이트
        existing_lemon.lemon_count = lemon_data.lemon_count

        # 레몬 저장
        updated_lemon = await self.lemon_repository.update_lemon(existing_lemon)

        return updated_lemon
