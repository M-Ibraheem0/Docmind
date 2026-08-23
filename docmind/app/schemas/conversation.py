from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class SourceChunk(BaseModel):
    filename: str
    chunk_index: int
    excerpt: str


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceChunk]
    cached: bool = False