from fastapi import Depends

from sqlalchemy.orm import Session
from app.models.lemon import Lemon
from app.core.dependencies import get_db

from typing import Optional


class LemonService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_lemon_by_user(self, user_id: int):
        return self.db.query(Lemon).filter(Lemon.user_id == user_id).all()
