from pydantic import BaseModel


class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    image_url: str
    is_image: bool


class ChatResult(BaseModel):
    answer: str


class ChatResponse(BaseModel):
    result: ChatResult
