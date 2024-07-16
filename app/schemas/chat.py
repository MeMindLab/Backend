from datetime import datetime, date
from typing import List
from pydantic import BaseModel


class Message(BaseModel):
    is_from_user: bool
    order: int
    message_id: int
    message_timestamp: datetime
    message: str


class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    image_url: str
    is_image: bool


class ChatResult(BaseModel):
    answer: str


class ChatResponse(BaseModel):
    is_enough: bool
    result: ChatResult


class ConversationRequest(BaseModel):
    date: date


class ConversationResponse(BaseModel):
    conversation_id: str
    is_enough: bool
    chat_history: List[Message]
