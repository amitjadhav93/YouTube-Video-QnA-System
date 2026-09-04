import re
from typing import Optional
from urllib.parse import parse_qs, urlparse

_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


class InvalidYouTubeURLError(ValueError):
    """Raised when a URL cannot be parsed into a valid YouTube video ID."""


def extract_video_id(url: str) -> str:
    if not url or not isinstance(url, str):
        raise InvalidYouTubeURLError("youtube_url must be a non-empty string")

    url = url.strip()

    if _VIDEO_ID_RE.match(url):
        return url

    parseable = url if "://" in url else f"https://{url}"

    try:
        parsed = urlparse(parseable)
    except Exception as exc:  
        raise InvalidYouTubeURLError(f"Could not parse URL: {url}") from exc

    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]

    video_id: Optional[str] = None

    if host in {"youtu.be"}:
        path_parts = [p for p in parsed.path.split("/") if p]
        if path_parts:
            video_id = path_parts[0]

    elif host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        path = parsed.path or ""
        if path == "/watch":
            qs = parse_qs(parsed.query)
            values = qs.get("v")
            if values:
                video_id = values[0]
        elif path.startswith("/embed/"):
            video_id = path.split("/embed/", 1)[1].split("/")[0]
        elif path.startswith("/shorts/"):
            video_id = path.split("/shorts/", 1)[1].split("/")[0]
        elif path.startswith("/v/"):
            video_id = path.split("/v/", 1)[1].split("/")[0]
        else:
            qs = parse_qs(parsed.query)
            values = qs.get("v")
            if values:
                video_id = values[0]

    else:
        qs = parse_qs(parsed.query)
        values = qs.get("v")
        if values:
            video_id = values[0]
        else:
            for part in parsed.path.split("/"):
                if _VIDEO_ID_RE.match(part):
                    video_id = part
                    break

    if video_id:
        video_id = video_id.split("?")[0].split("&")[0]
        if _VIDEO_ID_RE.match(video_id):
            return video_id

    raise InvalidYouTubeURLError(f"Could not extract a valid video ID from URL: {url}")

