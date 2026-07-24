from dataclasses import dataclass
from typing import TYPE_CHECKING, Required, TypedDict

from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message

if TYPE_CHECKING:
    from dungeon.models import TrackCache


class TrackDirContentDict(TypedDict):
    audio_path: str
    thumbnail_path: str | None


class YoutubeSearchResultDict(TypedDict):
    duration: str
    video_id: str
    title: str
    artist: str
    duration_seconds: int


class UserQueryLimit(TypedDict):
    semaphore: Required[int]
    ts: Required[float]


@dataclass
class TempTrackStatusInfo:
    title = "UNKNOWN"
    artist = "unknown"
    tg_file_id: str | None = None
    track_duration: int | None = None
    is_too_large: bool | None = None
    is_work_in_progress: bool | None = None
    # -----
    base_answer = "⏳ Обрабатываю запрос (это займет несколько секунд)\n"
    cache_data: TrackDirContentDict | bool = False
    cache_sent_successfully = False
    sent_message: Message | None = None

    def fill_from(self, track: "TrackCache"):
        self.title = track.title
        self.artist = track.artist
        self.tg_file_id = track.telegram_file_id
        self.is_too_large = track.is_too_large
        self.track_duration = track.track_duration
        self.is_work_in_progress = track.is_work_in_progress


class DownloadCallback(CallbackData, prefix="dl"):
    video_id: str
    idx: str
