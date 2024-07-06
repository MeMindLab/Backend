# app/models/image

import uuid
from sqlalchemy import UUID
from sqlalchemy.orm import mapped_column, String
from app.core.database import Base


class Image(Base):
    __tablename__ = "images"

    id = mapped_column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    path = mapped_column(String(256), nullable=False)
    extension = mapped_column(String(8), nullable=False)
