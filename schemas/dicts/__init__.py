from typing import Required, TypedDict


class YoutubeSearchResultDict(TypedDict):
    """Normalized data structure representing a track item pulled directly from YouTube Music search responses."""

    duration: str
    video_id: str
    title: str
    artist: str
    duration_seconds: int


class PlaylistInfoDict(TypedDict):
    id: str
    title: str | None
    artist: str | None


class UserQueryLimitDict(TypedDict):
    """Data blueprint for monitoring a single user's rate limits, tracking remaining downloads and request timestamps."""

    semaphore: Required[int]
    ts: Required[float]
