import logging

from fastapi import APIRouter, HTTPException

from models.schemas import AskRequest, AskResponse, SourceChunk
from services import vectorstore_service
from services.qna_service import QnAError, answer_question

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["qna"])


@router.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest) -> AskResponse:
    if not vectorstore_service.is_processed(payload.video_id):
        raise HTTPException(
            status_code=404,
            detail="Video has not been processed yet. Call /api/process-video first.",
        )

    try:
        answer, source_docs = answer_question(payload.video_id, payload.question)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Video has not been processed yet. Call /api/process-video first.",
        ) from exc
    except QnAError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected error answering question for video_id=%s", payload.video_id)
        raise HTTPException(
            status_code=500, detail=f"Unexpected error generating answer: {exc}"
        ) from exc

    sources = [
        SourceChunk(text=doc.page_content, start_time=doc.metadata.get("start_time"))
        for doc in source_docs
    ]

    return AskResponse(
        video_id=payload.video_id,
        question=payload.question,
        answer=answer,
        sources=sources,
    )
