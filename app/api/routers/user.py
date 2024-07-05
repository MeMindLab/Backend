from fastapi import APIRouter
from app.api.endpoints.user.user import user_module
from app.api.endpoints.user.auth import auth_module
from app.api.endpoints.user.lemon import lemon_user_module


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
    lemon_user_module,
    prefix="/users",
    tags=["lemons"],
    responses={404: {"description": "Not found"}},
)
