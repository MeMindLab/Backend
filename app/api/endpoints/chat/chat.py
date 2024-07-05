from fastapi import APIRouter, status, Depends

from app.schemas.chat import ChatResponse, ChatRequest

from app.service.chat import MessageRespondent
from app.service.test import MessageService


# sqlalchemy
from sqlalchemy.orm import Session


chat_module = APIRouter()


@chat_module.post(
    "/answer", response_model=ChatResponse, status_code=status.HTTP_200_OK
)
async def chat_answer(req: ChatRequest, message_service: MessageService = Depends()):
    conversation_id = req.conversation_id
    message = req.message
    image_url = req.image_url
    is_image = req.is_image

    try:
        answer = await message_service.answer_conversation(user_text=req.message)
        return {"result": {"answer": answer}, "is_enough": False}

    except Exception as e:
        # 오류 처리를 원하는 방식으로 추가합니다.
        print(f"Error in answering conversation: {e}")
