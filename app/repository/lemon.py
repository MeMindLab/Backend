from fastapi import Depends


from typing import Optional
from sqlalchemy import select, delete
from app.models.lemon import Lemon
from app.core.dependencies import get_db


class LemonRepository:
    def __init__(self, session=Depends(get_db)):
        self.session = session

    async def get_lemon_by_user_id(self, user_id: int) -> Optional[Lemon]:
        query = select(Lemon).filter(Lemon.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar()

    # save lemon
    async def save_lemon(self, lemon: Lemon) -> Lemon:
        try:
            self.session.add(lemon)
            await self.session.commit()  # 데이터베이스에 저장
            await self.session.refresh(lemon)  # 데이터베이스로부터 객체 새로고침
            return lemon
        except Exception as e:
            print(f"save lemon Error:{e}")
            await self.session.rollback()  # 롤백
            raise e
        finally:
            await self.session.close()  # 세션 닫

    async def update_lemon(self, lemon: Lemon) -> Lemon:
        try:
            self.session.add(lemon)
            await self.session.commit()
            await self.session.refresh(lemon)
            return lemon
        except Exception as e:
            print(f"update lemon Error:{e}")
            await self.session.rollback()  # 롤백
            raise e
        finally:
            await self.session.close()

    def delete_lemon(self, lemon_id: int) -> None:
        self.session.execute(delete(Lemon).where(Lemon.id == lemon_id))
        self.session.commit()
