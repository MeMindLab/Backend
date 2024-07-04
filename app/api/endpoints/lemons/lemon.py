from fastapi import APIRouter, Path, Depends, HTTPException


from app.core.dependencies import get_db
from app.models.user import User
from app.service.lemon import LemonService
from app.schemas.lemon import LemonUpdate, LemonCreate, LemonRead
from app.models.lemon import Lemon as LemonModel
from app.auth.authenticate import get_current_user

# sqlalchemy
from sqlalchemy.orm import Session


lemon_module = APIRouter(prefix="")


# Lemon CRUD operations
@lemon_module.post("", status_code=201)
async def create_lemon_handler(
    request: LemonCreate,
    lemon_service: LemonService = Depends(),
    user: User = Depends(get_current_user),
):
    lemon: LemonModel = LemonModel.create(request=request, user_id=user.id)  # id = None
    saved_lemon = await lemon_service.create_lemon(lemon)  # id =int
    pass
    # return LemonRead.model_validate(saved_lemon)


@lemon_module.get("/{user_id}/lemon")
def read_lemons_by_user(
    user_id: int = Path(..., title="User ID", description="The ID of the user"),
    db: Session = Depends(get_db),
):
    lemon_service = LemonService(db)

    lemons = lemon_service.get_lemon_by_user(user_id)
    print(lemons)

    pass


@lemon_module.post("/{user_id}")
def create_lemon_for_user():
    pass


@lemon_module.patch("/{user_id}/lemon")
def update_lemon_by_user(
    lemon_data: LemonUpdate,
    user_id: int = Path(..., title="User ID", description="The ID of the user"),
    db: Session = Depends(get_db),
):
    pass
