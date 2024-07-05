from fastapi import APIRouter, status, Depends
from fastapi import APIRouter, Path, Depends, HTTPException


from app.core.dependencies import get_db
from app.models.user import User
from app.service.lemon import LemonService
from app.schemas.lemon import LemonUpdate, LemonCreate, LemonRead
from app.models.lemon import Lemon as LemonModel
from app.auth.authenticate import get_current_user

# sqlalchemy
from sqlalchemy.orm import Session


lemon_user_module = APIRouter()


@lemon_user_module.get("/{user_id}/lemons")
def read_lemons_by_user(
    user_id: int = Path(..., title="User ID", description="The ID of the user"),
    db: Session = Depends(get_db),
):
    lemon_service = LemonService(db)

    lemons = lemon_service.get_lemon_by_user(user_id)
    print(lemons)

    pass


@lemon_user_module.patch("/{user_id}/lemon")
def update_lemon_by_user(
    lemon_data: LemonUpdate,
    user_id: int = Path(..., title="User ID", description="The ID of the user"),
    db: Session = Depends(get_db),
):
    pass
