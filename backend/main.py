"""
FastAPI app for the YouTube Video Q&A Chatbot backend.

Endpoints:
    GET    /api/health
    POST   /api/process-video
    POST   /api/ask
    DELETE /api/session/{session_id}

Run with:
    uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from models import (
    AskQuestionRequest,
    AskQuestionResponse,
    DeleteSessionResponse,
    ErrorResponse,
    HealthResponse,
    ProcessVideoRequest,
    ProcessVideoResponse,
)
from qna_system import (
    InvalidVideoURLError,
    TranscriptUnavailableError,
    VideoProcessingError,
    answer_question,
    process_video,
)
from session_manager import session_manager

app = FastAPI(
    title="YouTube Video Q&A Chatbot API",
    description="Backend for a RAG-based chatbot that answers questions about a YouTube video's transcript.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Error handling
#
# Route handlers below raise HTTPException(status_code=..., detail=<dict
# matching ErrorResponse>). FastAPI's default behavior wraps that detail in
# an extra {"detail": {...}} envelope, which would NOT match the exact API
# contract shared with the frontend. This handler unwraps it so the response
# body is exactly {"status": "error", "message": "..."} at the top level.
# ---------------------------------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    # If detail is already our error shape (a dict with "status"/"message"),
    # return it as-is. Otherwise, fall back to wrapping whatever detail is.
    if isinstance(exc.detail, dict) and "message" in exc.detail:
        content = exc.detail
    else:
        content = ErrorResponse(message=str(exc.detail)).model_dump()
    return JSONResponse(status_code=exc.status_code, content=content)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Malformed request bodies (missing fields, wrong types) -> 400 in our
    # error shape rather than FastAPI's default 422 validation payload.
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(message=f"Invalid request: {exc}").model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Last-resort fallback so no raw traceback ever reaches the client.
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(message=f"Internal server error: {exc}").model_dump(),
    )


# ---------------------------------------------------------------------------
# 1) Health check
# ---------------------------------------------------------------------------

@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Simple liveness endpoint."""
    return HealthResponse(status="ok")


# ---------------------------------------------------------------------------
# 2) Process a video
# ---------------------------------------------------------------------------

@app.post("/api/process-video", response_model=ProcessVideoResponse)
async def process_video_route(payload: ProcessVideoRequest) -> ProcessVideoResponse:
    """
    Fetch the transcript for the given YouTube URL, build a RAG pipeline
    over it, and create a new session for follow-up questions.
    """
    try:
        video_id, qa_chain = process_video(payload.video_url)
    except (InvalidVideoURLError, TranscriptUnavailableError) as exc:
        raise HTTPException(status_code=400, detail=ErrorResponse(message=str(exc)).model_dump())
    except VideoProcessingError as exc:
        raise HTTPException(status_code=400, detail=ErrorResponse(message=str(exc)).model_dump())

    session = session_manager.create_session(video_id=video_id, qa_chain=qa_chain)

    return ProcessVideoResponse(
        session_id=session.session_id,
        video_id=video_id,
        status="success",
        message="Video processed successfully.",
    )


# ---------------------------------------------------------------------------
# 3) Ask a question
# ---------------------------------------------------------------------------

@app.post("/api/ask", response_model=AskQuestionResponse)
async def ask_question_route(payload: AskQuestionRequest) -> AskQuestionResponse:
    """Answer a question about a previously processed video."""
    session = session_manager.get_session(payload.session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                message="Session not found. Please process the video again."
            ).model_dump(),
        )

    try:
        answer = answer_question(session.qa_chain, payload.question)
    except VideoProcessingError as exc:
        raise HTTPException(status_code=500, detail=ErrorResponse(message=str(exc)).model_dump())

    return AskQuestionResponse(answer=answer, session_id=session.session_id)


# ---------------------------------------------------------------------------
# 4) Delete/reset a session
# ---------------------------------------------------------------------------

@app.delete("/api/session/{session_id}", response_model=DeleteSessionResponse)
async def delete_session_route(session_id: str) -> DeleteSessionResponse:
    """Delete a session, freeing its in-memory retriever/chain."""
    deleted = session_manager.delete_session(session_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                message="Session not found. Please process the video again."
            ).model_dump(),
        )
    return DeleteSessionResponse(status="success", message="Session deleted.")
