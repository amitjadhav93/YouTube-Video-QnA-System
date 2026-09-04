import logging
import os
from functools import lru_cache
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from services import vectorstore_service

logger = logging.getLogger(__name__)

GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
DEFAULT_TOP_K = 4

_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that answers questions about a "
            "YouTube video using only the provided transcript excerpts. "
            "If the excerpts don't contain enough information to answer "
            "confidently, say so plainly instead of guessing. Be concise "
            "and directly answer the question.",
        ),
        (
            "human",
            "Transcript excerpts:\n{context}\n\nQuestion: {question}\n\nAnswer:",
        ),
    ]
)


class QnAError(Exception): 
    pass


@lru_cache(maxsize=1)
def _get_llm() -> ChatGoogleGenerativeAI:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise QnAError(
            "GOOGLE_API_KEY is not set. Add it to your .env file "
            "(see .env.example)."
        )
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME,
        google_api_key=api_key,
        temperature=0.2,
    )


def _format_context(docs: List[Document]) -> str:
    blocks = []
    for i, doc in enumerate(docs, start=1):
        start = doc.metadata.get("start_time")
        prefix = f"[Excerpt {i}" + (f", ~{start:.0f}s" if start is not None else "") + "]"
        blocks.append(f"{prefix}\n{doc.page_content}")
    return "\n\n".join(blocks)


def answer_question(
    video_id: str, question: str, top_k: int = DEFAULT_TOP_K
) -> Tuple[str, List[Document]]:
    try:
        docs = vectorstore_service.similarity_search(video_id, question, top_k=top_k)
    except FileNotFoundError:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("Similarity search failed for video_id=%s", video_id)
        raise QnAError(f"Failed to search transcript index: {exc}") from exc

    if not docs:
        return (
            "I couldn't find any relevant content in this video's transcript "
            "to answer that question.",
            [],
        )

    context = _format_context(docs)

    try:
        llm = _get_llm()
        chain = _PROMPT | llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})
    except QnAError:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("Gemini generation failed for video_id=%s", video_id)
        raise QnAError(f"Failed to generate an answer: {exc}") from exc

    return answer.strip(), docs
