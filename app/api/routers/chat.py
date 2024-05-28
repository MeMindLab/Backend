from fastapi import APIRouter
from app.api.endpoints.chat.chat import chat_module

chat_router = APIRouter()

chat_router.include_router(
    chat_module,
    prefix="/chat",
    tags=["chat"],
)
