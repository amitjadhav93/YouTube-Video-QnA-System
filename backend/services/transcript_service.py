import logging
from typing import List, TypedDict

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

logger = logging.getLogger(__name__)


class TranscriptSegment(TypedDict):
    text: str
    start: float
    duration: float


class TranscriptUnavailableError(Exception):
    """Raised when a transcript cannot be fetched for any reason."""


def fetch_transcript(video_id: str) -> List[TranscriptSegment]:
    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id)
        segments: List[TranscriptSegment] = [
            {
                "text": snippet.text,
                "start": float(snippet.start),
                "duration": float(snippet.duration),
            }
            for snippet in fetched
        ]
        if not segments:
            raise TranscriptUnavailableError(
                f"Transcript for video '{video_id}' is empty."
            )
        return segments

    except TranscriptsDisabled as exc:
        raise TranscriptUnavailableError(
            f"Transcripts are disabled for video '{video_id}'."
        ) from exc

    except VideoUnavailable as exc:
        raise TranscriptUnavailableError(
            f"Video '{video_id}' is unavailable (private, deleted, or region-locked)."
        ) from exc

    except NoTranscriptFound as exc:
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            candidate = next(iter(transcript_list), None)
            if candidate is None:
                raise TranscriptUnavailableError(
                    f"No transcript is available for video '{video_id}' in any language."
                ) from exc

            if candidate.is_translatable:
                candidate = candidate.translate("en")

            fetched = candidate.fetch()
            segments = [
                {
                    "text": snippet.text,
                    "start": float(snippet.start),
                    "duration": float(snippet.duration),
                }
                for snippet in fetched
            ]
            if not segments:
                raise TranscriptUnavailableError(
                    f"Transcript for video '{video_id}' is empty."
                )
            return segments
        except TranscriptUnavailableError:
            raise
        except Exception as fallback_exc:
            raise TranscriptUnavailableError(
                f"No transcript is available for video '{video_id}' in any language."
            ) from fallback_exc

    except CouldNotRetrieveTranscript as exc:
        raise TranscriptUnavailableError(
            f"Could not retrieve a transcript for video '{video_id}': {exc}"
        ) from exc

    except Exception as exc:  # noqa: BLE001 - final safety net
        logger.exception("Unexpected error fetching transcript for %s", video_id)
        raise TranscriptUnavailableError(
            f"Unexpected error fetching transcript for video '{video_id}': {exc}"
        ) from exc
