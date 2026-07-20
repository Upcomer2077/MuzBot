from aiogram.types import FSInputFile

from type import TrackDirContentDict


def prepare_audio_file_to_send(cache_data: TrackDirContentDict):
    audio_file = FSInputFile(path=cache_data["audio_path"])
    thumb_file = (
        FSInputFile(cache_data["thumbnail_path"])
        if cache_data["thumbnail_path"]
        else None
    )
    return (audio_file, thumb_file)
