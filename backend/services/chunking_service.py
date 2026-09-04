from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from services.transcript_service import TranscriptSegment

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def _build_full_text_with_offsets(segments: List[TranscriptSegment]):
    parts: List[str] = []
    offsets: List[tuple] = []
    cursor = 0
    for seg in segments:
        text = seg["text"].replace("\n", " ").strip()
        if not text:
            continue
        offsets.append((cursor, seg["start"]))
        parts.append(text)
        cursor += len(text) + 1  # +1 for the joining space
    full_text = " ".join(parts)
    return full_text, offsets


def _start_time_for_offset(offset: int, offsets: List[tuple]) -> float:
    best = 0.0
    for char_offset, start_time in offsets:
        if char_offset <= offset:
            best = start_time
        else:
            break
    return best


def chunk_transcript(video_id: str, segments: List[TranscriptSegment]) -> List[Document]:
    full_text, offsets = _build_full_text_with_offsets(segments)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    raw_chunks = splitter.split_text(full_text)

    documents: List[Document] = []
    search_from = 0
    for chunk_text in raw_chunks:
        idx = full_text.find(chunk_text, max(0, search_from - CHUNK_OVERLAP))
        if idx == -1:
            idx = full_text.find(chunk_text)
        if idx == -1:
            idx = search_from 

        start_time = _start_time_for_offset(idx, offsets)
        documents.append(
            Document(
                page_content=chunk_text,
                metadata={"video_id": video_id, "start_time": round(start_time, 2)},
            )
        )
        search_from = idx + max(1, len(chunk_text) - CHUNK_OVERLAP)

    return documents
