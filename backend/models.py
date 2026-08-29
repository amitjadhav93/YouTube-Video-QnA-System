"""
Pydantic (v2) request/response schemas for the YouTube Video Q&A Chatbot API.

These models define the exact wire contract shared with the frontend team.
Field names and shapes must not be changed without updating the frontend.
"""

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# /api/health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Simple liveness indicator.")


# ---------------------------------------------------------------------------
# /api/process-video
# ---------------------------------------------------------------------------

class ProcessVideoRequest(BaseModel):
    video_url: str = Field(
        ...,
        description="Full YouTube video URL, e.g. https://www.youtube.com/watch?v=XXXXXXXXXXX",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )


class ProcessVideoResponse(BaseModel):
    session_id: str
    video_id: str
    status: str = "success"
    message: str = "Video processed successfully."


# ---------------------------------------------------------------------------
# /api/ask
# ---------------------------------------------------------------------------

class AskQuestionRequest(BaseModel):
    session_id: str
    question: str


class AskQuestionResponse(BaseModel):
    answer: str
    session_id: str


# ---------------------------------------------------------------------------
# /api/session/{session_id}  (DELETE)
# ---------------------------------------------------------------------------

class DeleteSessionResponse(BaseModel):
    status: str = "success"
    message: str = "Session deleted."


# ---------------------------------------------------------------------------
# Shared error shape
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
