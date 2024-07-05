from fastapi import APIRouter, Depends


from app.service.lemon import LemonService
from app.schemas.lemon import LemonCreate, LemonResponse
from app.auth.authenticate import get_current_user


lemon_module = APIRouter(prefix="")


# Lemon CRUD operations
@lemon_module.post("", status_code=201, response_model=LemonResponse)
async def create_lemon_handler(
    request: LemonCreate,
    lemon_service: LemonService = Depends(),
    user_id: int = Depends(get_current_user),
):
    lemon = await lemon_service.create_lemon_for_user(
        lemon_create=request, user_id=user_id
    )
    return lemon
