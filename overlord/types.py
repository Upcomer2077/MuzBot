from typing import TypedDict


class TrackDirContentDict(TypedDict):
    """Dictionary structure storing the exact local file paths of a cached track's audio and thumbnail components."""

    _video_id: str
    audio_path: str
    thumbnail_path: str | None
