from uuid import UUID
from fastapi import APIRouter, Depends

from app.schemas.chat import (
    ChatRequest,
    ConversationRequest,
    MonthlyConversationsResponse,
    ConversationBase,
)

from app.service import MessageService, ConversationService
from app.auth.authenticate import get_current_user


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


@chat_module.post("/answer")
async def chat_answer(
    req: ChatRequest,
    message_service: MessageService = Depends(),
):
    try:
        answer = await message_service.answer_message(
            user_text=req.message,
            conversation_id=req.conversation_id,
            image_url=req.image_url,
            is_image=req.is_image,
        )
        return {"result": answer}

    except Exception as e:
        # 오류 처리를 원하는 방식으로 추가합니다.
        print(f"Error in answering conversation: {e}")


@chat_module.get("/monthly-conversations", response_model=MonthlyConversationsResponse)
async def get_monthly_conversations(
    year: int,
    month: int,
    conversation_service: ConversationService = Depends(),
    auth: UUID = Depends(get_current_user),
):
    try:
        conversations = await conversation_service.get_monthly_conversations(
            year=year, month=month, user_id=auth
        )

        result = MonthlyConversationsResponse(
            conversations=[
                ConversationBase(
                    conversation_id=conversation.id,
                    user_id=conversation.user_id,
                    date=conversation.date,
                )
                for conversation in conversations
            ]
        )

        return result

    except Exception as e:
        # Error handling can be added as per your application's needs
        print(f"Error in fetching monthly conversations: {e}")
        return {"error": "Failed to fetch monthly conversations"}
