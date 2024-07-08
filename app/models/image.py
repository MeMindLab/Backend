# app/models/image

import uuid
from sqlalchemy import String, Uuid

from sqlalchemy.orm import mapped_column
from app.core.database import Base


class Image(Base):
    __tablename__ = "images"

    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    path = mapped_column(String(256), nullable=False)
    extension = mapped_column(String(8), nullable=False)
