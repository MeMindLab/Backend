from fastapi import APIRouter, Depends
from fastapi import APIRouter, Path, Depends


from app.service.lemon import LemonService
from app.schemas.lemon import LemonResponse, LemonUpdate

from app.auth.authenticate import get_current_user


lemon_user_module = APIRouter()


@lemon_user_module.get("/{user_id}/lemons", response_model=LemonResponse)
async def read_lemons_by_user(
    user_id: int = Path(..., title="User ID", description="The ID of the user"),
    lemon_service: LemonService = Depends(),
):
    lemons = await lemon_service.get_lemon_by_user_id(user_id)
    return lemons


@lemon_user_module.patch("/{user_id}/lemon")
async def update_lemon_by_user(
    lemon_data: LemonUpdate,
    user_id: int = Path(..., title="User ID", description="The ID of the user"),
    lemon_service: LemonService = Depends(),
):
    updated_lemon = await lemon_service.update_lemon_by_user_id(lemon_data, user_id)
    return updated_lemon
