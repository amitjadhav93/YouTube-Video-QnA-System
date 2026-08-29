"""
In-memory session store.

Each successfully processed video gets a session_id (UUID4). The session
holds everything needed to answer follow-up questions about that video:
the video_id, the FAISS-backed retriever, and the RetrievalQA chain built
on top of it.

KNOWN LIMITATIONS (acceptable for this project):
- This store is a plain in-process dict. It will NOT survive server
  restarts, and it will NOT be shared across multiple worker processes
  (e.g. `uvicorn --workers 4` or multiple gunicorn workers each get their
  own copy). For a production multi-worker deployment you'd want a shared
  store (Redis, a DB-backed vector store, etc.) instead.
- TODO: sessions are never automatically expired/cleaned up. A simple
  approach would be to store `created_at` per session and run a periodic
  background task (e.g. via `asyncio` + FastAPI's lifespan, or an APScheduler
  job) that drops sessions older than N hours. Skipped here as a
  nice-to-have per the project spec.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Session:
    """Everything needed to answer questions about one processed video."""

    session_id: str
    video_id: str
    qa_chain: Any  # a LangChain RetrievalQA chain instance


class SessionManager:
    """
    Thread-safe in-memory manager for chatbot sessions.

    FastAPI/uvicorn can handle requests concurrently (via a thread pool for
    sync code, or the event loop for async code), so a lock guards the
    underlying dict from concurrent read/write races.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()

    def create_session(self, video_id: str, qa_chain: Any) -> Session:
        """Create and store a new session, returning it."""
        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id, video_id=video_id, qa_chain=qa_chain)
        with self._lock:
            self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Look up a session by id. Returns None if unknown/expired."""
        with self._lock:
            return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Remove a session. Returns True if it existed and was removed."""
        with self._lock:
            return self._sessions.pop(session_id, None) is not None


# Module-level singleton used by the FastAPI routes.
session_manager = SessionManager()
