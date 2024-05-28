from fastapi import APIRouter, status

from app.schemas.chat import ChatResponse, ChatRequest


chat_module = APIRouter()


@chat_module.post(
    "/answer", response_model=ChatResponse, status_code=status.HTTP_200_OK
)
async def chat_answer(req: ChatRequest):
    conversation_id = req.conversation_id
    message = req.message
    image_url = req.image_url
    is_image = req.is_image

    # 답변 생성
    answer = "오늘 많이 더우셨겠어요"

    return {"result": {"answer": answer}}
