from dataclasses import dataclass
from typing import TYPE_CHECKING, Required, TypedDict

from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message

if TYPE_CHECKING:
    from dungeon.models import TrackCache


class TrackDirContentDict(TypedDict):
    """Dictionary structure storing the exact local file paths of a cached track's audio and thumbnail components."""

    _video_id: str
    audio_path: str
    thumbnail_path: str | None


class YoutubeSearchResultDict(TypedDict):
    """Normalized data structure representing a track item pulled directly from YouTube Music search responses."""

    duration: str
    video_id: str
    title: str
    artist: str
    duration_seconds: int


class UserQueryLimit(TypedDict):
    """Data blueprint for monitoring a single user's rate limits, tracking remaining downloads and request timestamps."""

    semaphore: Required[int]
    ts: Required[float]


@dataclass
class TrackState:
    """State management object tracking download status flags, media metadata, and response messaging pipelines."""

    video_id: str | None = None
    title: str = "UNKNOWN"
    artist: str = "unknown"
    tg_file_id: str | None = None
    track_duration: int | None = None
    is_too_large: bool | None = None
    is_work_in_progress: bool | None = None
    # -----
    base_answer = "⏳ Обрабатываю запрос (это займет несколько секунд)\n"
    cache_data: TrackDirContentDict | None = None
    is_cache_sent_successfully = False
    sent_audio: Message | None = None

    def fill_from(self, track: "TrackCache"):
        self.video_id = track.video_id
        self.title = track.title
        self.artist = track.artist
        self.tg_file_id = track.telegram_file_id
        self.is_too_large = track.is_too_large
        self.track_duration = track.track_duration
        self.is_work_in_progress = track.is_work_in_progress

        return self


class DownloadCallback(CallbackData, prefix="dl"):
    """Callback data schema defining expected inline keyboard button parameters for handling individual audio download requests."""

    video_id: str
    idx: str


class PlaylistInfoDict(TypedDict):
    id: str
    title: str | None


@dataclass(slots=True)
class PlaylistTask:
    user_id: int
    playlist_id: str
    videos: list[YoutubeSearchResultDict]
