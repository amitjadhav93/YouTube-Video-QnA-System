import json
import logging
import os
import threading
from pathlib import Path
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from services.embedding_service import get_embeddings

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_STORES_DIR = BASE_DIR / "vector_stores"
REGISTRY_PATH = VECTOR_STORES_DIR / "_registry.json"

_registry_lock = threading.Lock()


def _ensure_base_dir() -> None:
    VECTOR_STORES_DIR.mkdir(parents=True, exist_ok=True)


def _video_dir(video_id: str) -> Path:
    return VECTOR_STORES_DIR / video_id


def _load_registry() -> dict:
    _ensure_base_dir()
    if not REGISTRY_PATH.exists():
        return {}
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        logger.warning("Registry file at %s was unreadable; starting fresh.", REGISTRY_PATH)
        return {}


def _save_registry(registry: dict) -> None:
    _ensure_base_dir()
    tmp_path = REGISTRY_PATH.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    os.replace(tmp_path, REGISTRY_PATH)


def is_processed(video_id: str) -> bool:
    with _registry_lock:
        registry = _load_registry()
    return video_id in registry and _video_dir(video_id).exists()


def get_chunk_count(video_id: str) -> Optional[int]:
    with _registry_lock:
        registry = _load_registry()
    entry = registry.get(video_id)
    return entry.get("chunk_count") if entry else None


def build_and_save_index(video_id: str, documents: List[Document]) -> int:
    _ensure_base_dir()
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)

    video_dir = _video_dir(video_id)
    video_dir.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(video_dir))

    with _registry_lock:
        registry = _load_registry()
        registry[video_id] = {"chunk_count": len(documents)}
        _save_registry(registry)

    logger.info("Indexed %d chunks for video_id=%s", len(documents), video_id)
    return len(documents)


def load_index(video_id: str) -> FAISS:
    video_dir = _video_dir(video_id)
    if not video_dir.exists():
        raise FileNotFoundError(f"No FAISS index found for video_id='{video_id}'")

    embeddings = get_embeddings()
    return FAISS.load_local(
        str(video_dir),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def similarity_search(video_id: str, query: str, top_k: int = 4) -> List[Document]:
    vectorstore = load_index(video_id)
    return vectorstore.similarity_search(query, k=top_k)
