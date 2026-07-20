from dataclasses import dataclass
from typing import TypedDict

from aiogram.types import Message


class TrackDirContentDict(TypedDict):
    audio_path: str
    thumbnail_path: str | None


class YoutubeSearchResultDict(TypedDict):
    duration: str
    video_id: str
    title: str
    artist: str
    duration_seconds: int


@dataclass
class TempTrackStatusInfo:
    title = "UNKNOWN"
    artist = "unknown"
    tg_file_id: str | None = None
    track_duration: int | None = None
    is_too_large: bool | None = None
    is_work_in_progress: bool | None = None

    base_answer = "⏳ Обрабатываю запрос (это займет несколько секунд)...\n"
    cache_data: TrackDirContentDict | bool = False
    cache_sent_successfully = False
    sent_message: Message | None = None
