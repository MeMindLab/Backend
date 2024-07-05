from fastapi import APIRouter


from app.api.endpoints.lemons.lemon import lemon_module

lemon_router = APIRouter()

lemon_router.include_router(
    lemon_module,
    prefix="/lemons",
    tags=["lemons"],
    responses={404: {"description": "Not found"}},
)
