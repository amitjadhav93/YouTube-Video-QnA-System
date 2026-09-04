import logging

from fastapi import APIRouter, HTTPException

from models.schemas import ProcessVideoRequest, ProcessVideoResponse
from services import chunking_service, transcript_service, vectorstore_service
from services.transcript_service import TranscriptUnavailableError
from utils.youtube_utils import InvalidYouTubeURLError, extract_video_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["video"])


@router.post("/process-video", response_model=ProcessVideoResponse)
def process_video(payload: ProcessVideoRequest) -> ProcessVideoResponse:
    try:
        video_id = extract_video_id(payload.youtube_url)
    except InvalidYouTubeURLError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if vectorstore_service.is_processed(video_id):
        chunk_count = vectorstore_service.get_chunk_count(video_id) or 0
        return ProcessVideoResponse(
            video_id=video_id,
            status="already_processed",
            chunk_count=chunk_count,
            transcript_available=True,
        )

    try:
        segments = transcript_service.fetch_transcript(video_id)
    except TranscriptUnavailableError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


    try:
        documents = chunking_service.chunk_transcript(video_id, segments)
        if not documents:
            raise ValueError("Chunking produced zero chunks from the transcript.")
    except Exception as exc:  
        logger.exception("Chunking failed for video_id=%s", video_id)
        raise HTTPException(
            status_code=500, detail=f"Failed to chunk transcript: {exc}"
        ) from exc

  
    try:
        chunk_count = vectorstore_service.build_and_save_index(video_id, documents)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Indexing failed for video_id=%s", video_id)
        raise HTTPException(
            status_code=500, detail=f"Failed to build vector index: {exc}"
        ) from exc

    return ProcessVideoResponse(
        video_id=video_id,
        status="processed",
        chunk_count=chunk_count,
        transcript_available=True,
    )
