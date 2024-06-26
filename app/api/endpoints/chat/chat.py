from fastapi import APIRouter, status, Depends

from app.schemas.chat import ChatResponse, ChatRequest

from app.service.talk import MessageRespondent
from app.core.dependencies import get_db

# sqlalchemy
from sqlalchemy.orm import Session


chat_module = APIRouter()


@chat_module.post(
    "/answer", response_model=ChatResponse, status_code=status.HTTP_200_OK
)
def chat_answer(req: ChatRequest, session: Session = Depends(get_db)):
    conversation_id = req.conversation_id
    message = req.message
    image_url = req.image_url
    is_image = req.is_image

    # MessageRespondent 클래스 초기화 시 세션을 제공하도록 수정
    message_respondent = MessageRespondent(session=session)

    try:
        answer = message_respondent.answer_conversation(message)
        return {"result": {"answer": answer}, "is_enough": False}

    except Exception as e:
        # 오류 처리를 원하는 방식으로 추가합니다.
        print(f"Error in answering conversation: {e}")
