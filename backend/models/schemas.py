from typing import List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class ProcessVideoRequest(BaseModel):
    youtube_url: str = Field(..., min_length=1, description="Full YouTube URL")


class ProcessVideoResponse(BaseModel):
    video_id: str
    status: str  
    chunk_count: int
    transcript_available: bool


class AskRequest(BaseModel):
    video_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)


class SourceChunk(BaseModel):
    text: str
    start_time: Optional[float] = None


class AskResponse(BaseModel):
    video_id: str
    question: str
    answer: str
    sources: List[SourceChunk]


class ErrorResponse(BaseModel):
    detail: str
