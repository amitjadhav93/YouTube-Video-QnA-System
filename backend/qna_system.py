"""
Core Q&A pipeline logic: turning a YouTube URL into a queryable RAG chain.

Pipeline (mirrors the original Streamlit prototype):
    1. Extract the video ID from a YouTube URL.
    2. Fetch the English transcript via youtube-transcript-api.
    3. Join transcript chunks into one text blob, wrapped in a LangChain
       Document.
    4. Split it with RecursiveCharacterTextSplitter (chunk_size=1000,
       chunk_overlap=200).
    5. Embed chunks with HuggingFace sentence-transformers/all-MiniLM-L6-v2
       (CPU).
    6. Store embeddings in a FAISS vector store.
    7. Load an Ollama LLM.
    8. Build a RetrievalQA chain ("stuff", retriever k=3).

This module raises plain Python exceptions with clear, user-facing messages;
it does not know anything about HTTP. The FastAPI route layer (main.py) is
responsible for translating these into the API's JSON error shape and status
codes.
"""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)

from config import settings


class InvalidVideoURLError(Exception):
    """Raised when a video ID cannot be extracted from the given URL."""


class TranscriptUnavailableError(Exception):
    """Raised when no English transcript exists for the video."""


class VideoProcessingError(Exception):
    """Raised for any other failure while building the RAG pipeline."""


# ---------------------------------------------------------------------------
# Step 1: URL -> video ID
# ---------------------------------------------------------------------------

def extract_video_id(video_url: str) -> str:
    """
    Extract the 11-character YouTube video ID from a URL.

    Supports both:
      - https://www.youtube.com/watch?v=XXXXXXXXXXX
      - https://youtu.be/XXXXXXXXXXX

    Raises:
        InvalidVideoURLError: if no video ID can be found.
    """
    if not video_url or not isinstance(video_url, str):
        raise InvalidVideoURLError("A video URL is required.")

    parsed = urlparse(video_url.strip())

    video_id: str | None = None

    if parsed.hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            query_params = parse_qs(parsed.query)
            values = query_params.get("v")
            if values:
                video_id = values[0]
        elif parsed.path.startswith("/embed/") or parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/")[2] if len(parsed.path.split("/")) > 2 else None
    elif parsed.hostname in ("youtu.be",):
        video_id = parsed.path.lstrip("/")

    # Fallback: try a regex match anywhere in the string for odd formats.
    if not video_id:
        match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})", video_url)
        if match:
            video_id = match.group(1)

    if not video_id or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise InvalidVideoURLError(
            "Could not extract a valid YouTube video ID from the provided URL."
        )

    return video_id


# ---------------------------------------------------------------------------
# Step 2-3: video ID -> transcript Document
# ---------------------------------------------------------------------------

def fetch_transcript_document(video_id: str) -> Document:
    """
    Fetch the English transcript for a video and wrap it in a LangChain
    Document.

    Raises:
        TranscriptUnavailableError: if transcripts are disabled or none
            exist for this video.
        VideoProcessingError: for any other transcript-fetch failure.
    """
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id, languages=["en"])
        transcript_chunks = fetched.to_raw_data()
    except (TranscriptsDisabled, NoTranscriptFound):
        raise TranscriptUnavailableError(
            "Transcript is not available for this video."
        )
    except Exception as exc:  # noqa: BLE001 - surface any other fetch failure
        raise VideoProcessingError(f"Failed to fetch transcript: {exc}") from exc

    full_text = " ".join(chunk["text"] for chunk in transcript_chunks)
    if not full_text.strip():
        raise TranscriptUnavailableError(
            "Transcript is not available for this video."
        )

    return Document(page_content=full_text, metadata={"video_id": video_id})


# ---------------------------------------------------------------------------
# Step 4-8: Document -> RetrievalQA chain
# ---------------------------------------------------------------------------

def build_qa_chain(document: Document) -> RetrievalQA:
    """
    Split, embed, index, and wrap a transcript Document into a RetrievalQA
    chain backed by a local Ollama LLM.

    Raises:
        VideoProcessingError: if any stage of the pipeline fails.
    """
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents([document])

        embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
        )

        vector_store = FAISS.from_documents(chunks, embeddings)
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})

        llm = OllamaLLM(model=settings.ollama_model, base_url=settings.ollama_base_url)

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
        )
    except Exception as exc:  # noqa: BLE001 - wrap any pipeline failure
        raise VideoProcessingError(f"Failed to build Q&A pipeline: {exc}") from exc

    return qa_chain


def process_video(video_url: str) -> tuple[str, RetrievalQA]:
    """
    End-to-end: URL -> (video_id, RetrievalQA chain).

    This is the single entry point the API layer calls for
    POST /api/process-video.
    """
    video_id = extract_video_id(video_url)
    document = fetch_transcript_document(video_id)
    qa_chain = build_qa_chain(document)
    return video_id, qa_chain


def answer_question(qa_chain: RetrievalQA, question: str) -> str:
    """
    Run a question through an already-built RetrievalQA chain.

    Raises:
        VideoProcessingError: if the LLM/chain invocation fails.
    """
    try:
        result = qa_chain.invoke({"query": question})
    except Exception as exc:  # noqa: BLE001 - surface any chain failure
        raise VideoProcessingError(f"Failed to generate an answer: {exc}") from exc

    # RetrievalQA.invoke returns a dict with a "result" key by default.
    answer = result.get("result") if isinstance(result, dict) else str(result)
    return answer or ""
