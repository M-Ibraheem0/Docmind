from pydantic import BaseModel
from datetime import datetime
from app.models.document import DocumentStatus


class DocumentResponse(BaseModel):
    id: int
    filename: str
    status: DocumentStatus
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}