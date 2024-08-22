from datetime import datetime
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


class DrawingDiaryBase(BaseModel):
    image_url: str
    image_title: str

    class Config:
        from_attributes = True


class ReportBase(BaseModel):
    report_id: UUID
    report_summary: ReportSummaryBase
    emotions: EmotionBase
    conversation_id: UUID
    drawing_diary: Optional[DrawingDiaryBase] = None
    chat_history: List[ReportChatMessageBase]
    images: List[str] = []

    class Config:
        from_attributes = True


class ReportCreateRequest(BaseModel):
    conversation_id: UUID


class ListRequestBase(BaseModel):
    limit: int = Field(20, ge=1, le=20)
    cursor: str | None = Field(None, max_length=100)


class ListResponseBase(BaseModel):
    next_cursor: UUID | None = None


class ReportListRequest(ListRequestBase):
    keywords: str


class ReportListResponse(ListResponseBase):
    class Report(BaseModel):
        id: UUID
        tags: list[str]
        ai_summary: str
        thumbnail: Optional[str] = None
        created_at: datetime = Field(default_factory=datetime.utcnow)

    reports: list[Report]
