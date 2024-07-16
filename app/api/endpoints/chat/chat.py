from uuid import UUID
from fastapi import APIRouter, status, Depends

from app.schemas.chat import ChatResponse, ChatRequest, ConversationRequest
from app.service.chat import MessageService, ConversationService
from app.auth.authenticate import get_current_user

# sqlalchemy
from sqlalchemy.orm import Session


chat_module = APIRouter()


@chat_module.post("/start")
async def start_conversation(
    req: ConversationRequest,
    conversation_service: ConversationService = Depends(),
    auth: UUID = Depends(get_current_user),
):
    result = await conversation_service.start_conversation(
        diary_date=req.date, user_id=auth
    )

    return result


@chat_module.post("/answer", status_code=status.HTTP_200_OK)
async def chat_answer(req: ChatRequest, message_service: MessageService = Depends()):
    try:
        answer = await message_service.answer_message(
            user_text=req.message, conversation_id=req.conversation_id
        )
        return {"result": answer}

    except Exception as e:
        # 오류 처리를 원하는 방식으로 추가합니다.
        print(f"Error in answering conversation: {e}")
