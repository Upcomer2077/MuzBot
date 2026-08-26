from typing import Required, TypedDict

from aiogram.filters.callback_data import CallbackData


class TrackDirContentDict(TypedDict):
    """Dictionary structure storing the exact local file paths of a cached track's audio and thumbnail components."""

    _video_id: str
    audio_path: str
    thumbnail_path: str | None


class YoutubeSearchResultDict(TypedDict):
    """Normalized data structure representing a track item pulled directly from YouTube Music search responses."""

    duration: str | None
    video_id: str
    title: str
    artist: str
    duration_seconds: int


class UserQueryLimit(TypedDict):
    """Data blueprint for monitoring a single user's rate limits, tracking remaining downloads and request timestamps."""

    semaphore: Required[int]
    ts: Required[float]


class DownloadCallback(CallbackData, prefix="dl"):
    """Callback data schema defining expected inline keyboard button parameters for handling individual audio download requests."""

    video_id: str
    idx: str


class DownloadPlaylistCallback(CallbackData, prefix="dlp"):
    """Callback data schema defining expected inline keyboard button parameters for handling individual playlist download requests."""

    playlist_id: str


class PlaylistInfoDict(TypedDict):
    id: str
    title: str | None
    artist: str | None
