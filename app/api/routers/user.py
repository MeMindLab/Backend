from fastapi import APIRouter
from app.api.endpoints.user.user import user_module
from app.api.endpoints.user.auth import auth_module
from app.api.endpoints.lemons.lemon import lemon_module

user_router = APIRouter()

user_router.include_router(
    user_module,
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

user_router.include_router(
    auth_module,
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

user_router.include_router(
    lemon_module,
    prefix="/users",  # 레몬 모듈의 prefix를 "/users"로 지정하여 "/users/{user_id}/lemons"으로 매핑됩니다.
    tags=["lemons"],
    responses={404: {"description": "Not found"}},
)
