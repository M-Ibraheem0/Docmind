import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum, func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.database import Base


class DocumentStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    ready = "ready"
    failed = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(SAEnum(DocumentStatus), default=DocumentStatus.pending, nullable=False)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    chunk_index = Column(Integer, nullable=False)

    document = relationship("Document", back_populates="chunks")