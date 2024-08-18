from typing import List, Optional, Union
from pydantic import BaseModel, Field
from uuid import UUID


class EmotionBase(BaseModel):
    comfortable_percentage: float
    happy_percentage: float
    sad_percentage: float
    joyful_percentage: float
    annoyed_percentage: float
    lethargic_percentage: float
    total_score: int

    class Config:
        from_attributes = True


class ReportSummaryBase(BaseModel):
    summary: str
    tags: List[str]


class ReportChatMessageBase(BaseModel):
    role: str
    content: Union[str, None]
    is_image: bool


class ReportBase(BaseModel):
    report_id: UUID
    report_summary: ReportSummaryBase
    emotions: EmotionBase
    conversation_id: UUID
    drawing_diary_id: Optional[UUID] = None
    chat_history: List[ReportChatMessageBase]
    images: List[str] = []

    class Config:
        from_attributes = True
