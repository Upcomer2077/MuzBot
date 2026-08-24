from aiogram.types import FSInputFile

from schemas.dicts.dir import TrackDirContentDict


def prepare_audio_file_to_send(cache_data: TrackDirContentDict):
    """Wrap local media cache files into Telegram-compatible input file wrappers.

    Args:
        cache_data: Dictionary containing absolute file paths for the audio and thumbnail.

    Returns:
        A tuple containing the audio input wrapper and an optional thumbnail input wrapper.
    """
    audio_file = FSInputFile(path=cache_data["audio_path"])
    thumb_file = (
        FSInputFile(cache_data["thumbnail_path"])
        if cache_data["thumbnail_path"]
        else None
    )
    return (audio_file, thumb_file)
